#!/usr/bin/env python3
"""SpeechCam - club speech recorder for Raspberry Pi Zero W.

Video:  Raspberry Pi Camera Module 3, H.264 encoded in hardware by rpicam-vid
        (or camera = "hdmi": any HDMI source through a USB capture dongle)
Audio:  wireless lav receiver (USB audio)
Output: H.264 + PCM master (.mkv) while recording, then an .mp4 made in the
        background when the camera is idle (a quick remux for the Pi camera,
        a full transcode for HDMI capture).

Controls: RECORD button (focus knob), MODE button (crank), power button
(handled by the kernel gpio-shutdown overlay). Toastmasters timing lights
on the front, red REC tally, beeps through a PAM8302 + speaker, and a web
page at http://speechcam.local:8080 for control and downloads.

Run `speechcam.py devices` to list cameras and microphones,
`speechcam.py --simulate` to try it on any computer with ffmpeg.
"""

import argparse
import glob
import html
import json
import math
import os
import re
import shlex
import shutil
import signal
import struct
import subprocess
import sys
import threading
import time
import tomllib
import urllib.parse
import wave
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONFIG_PATHS = [Path("/etc/speechcam/config.toml"), HERE / "config.toml"]

DEFAULTS = {
    "recordings_dir": "/home/pi/recordings",
    "camera": "picamera",
    "camera_options": "--autofocus-mode continuous",
    "video_bitrate": 6000000,
    "video_device": "auto",
    "video_size": "1920x1080",
    "video_fps": 30,
    "audio_device": "auto",
    "audio_match": "",
    "audio_channels": 1,
    "audio_rate": 48000,
    "audio_offset": 0.0,
    "max_minutes": 30,
    "min_free_mb": 1500,
    "transcode": True,
    "transcode_bitrate": "3M",
    "keep_master": False,
    "crop": "",
    "beep_device": "plughw:CARD=Headphones",
    "volume": 0.6,
    "web_port": 8080,
    "pins": {"record": 17, "mode": 27, "tally": 22, "green": 5, "yellow": 6, "red": 26},
    "default_profile": "speech_5_7",
    "profiles": [
        {"id": "off", "name": "No timing lights"},
        {"id": "table_topics", "name": "Table Topics (1-2 min)", "green": 60, "yellow": 90, "red": 120},
        {"id": "evaluation", "name": "Evaluation (2-3 min)", "green": 120, "yellow": 150, "red": 180},
        {"id": "icebreaker", "name": "Ice Breaker (4-6 min)", "green": 240, "yellow": 300, "red": 360},
        {"id": "speech_5_7", "name": "Speech (5-7 min)", "green": 300, "yellow": 360, "red": 420},
        {"id": "speech_10_12", "name": "Speech (10-12 min)", "green": 600, "yellow": 660, "red": 720},
    ],
}

# Capture dongles also expose a USB microphone; skip them when auto-picking
CAPTURE_CARD_HINTS = ("ms2109", "macrosilicon", "capture", "cam link", "hdmi", "usb3. 0", "usb3.0")
GRACE_SECONDS = 30   # Toastmasters: red light + 30 s -> over time


def log(*args):
    print(time.strftime("%H:%M:%S"), *args, flush=True)


def load_config(path=None):
    cfg = json.loads(json.dumps(DEFAULTS))
    paths = [Path(path)] if path else CONFIG_PATHS
    for p in paths:
        if p.exists():
            with open(p, "rb") as f:
                user = tomllib.load(f)
            pins = {**cfg["pins"], **user.pop("pins", {})}
            cfg.update(user)
            cfg["pins"] = pins
            log(f"config: {p}")
            break
    return cfg


# ---------------------------------------------------------------------------
# Devices
# ---------------------------------------------------------------------------

def find_video_device():
    for path in sorted(glob.glob("/dev/v4l/by-id/usb-*-video-index0")):
        return path
    return "/dev/video0"


def list_sound_cards():
    cards = []
    try:
        text = Path("/proc/asound/cards").read_text()
    except OSError:
        return cards
    for m in re.finditer(r"^\s*(\d+)\s+\[(\S+)\s*\]:\s*(.+?)\s*$", text, re.M):
        cards.append({"index": int(m.group(1)), "id": m.group(2), "desc": m.group(3)})
    return cards


def find_audio_device(match=""):
    capture_cards = []
    for card in list_sound_cards():
        if not Path(f"/proc/asound/card{card['index']}/pcm0c").exists():
            continue  # no capture side
        text = f"{card['id']} {card['desc']}".lower()
        if match:
            if match.lower() in text:
                return f"plughw:CARD={card['id']},DEV=0"
            continue
        if "usb" not in text:
            continue
        if any(h in text for h in CAPTURE_CARD_HINTS):
            capture_cards.append(card)
            continue
        return f"plughw:CARD={card['id']},DEV=0"
    if capture_cards:
        log("warning: no separate microphone found, using the capture card's audio")
        return f"plughw:CARD={capture_cards[0]['id']},DEV=0"
    return None


def print_devices():
    print("Video (by-id):")
    for p in sorted(glob.glob("/dev/v4l/by-id/*")) or ["  (none)"]:
        print("  ", p)
    if shutil.which("v4l2-ctl"):
        subprocess.run(["v4l2-ctl", "--list-devices"])
        dev = find_video_device()
        print(f"\nFormats on {dev}:")
        subprocess.run(["v4l2-ctl", "-d", dev, "--list-formats-ext"])
    print("\nSound cards:")
    for c in list_sound_cards():
        print(f"   {c['index']}: {c['id']:<14} {c['desc']}")
    print("\nAuto-picked microphone:", find_audio_device() or "(none)")
    print("Auto-picked camera:    ", find_video_device())


# ---------------------------------------------------------------------------
# GPIO (real or simulated)
# ---------------------------------------------------------------------------

class FakeLED:
    def __init__(self, name):
        self.name, self.is_lit = name, False

    def on(self):
        self.is_lit = True

    def off(self):
        self.is_lit = False

    def blink(self, on_time=0.5, off_time=0.5, **_):
        self.is_lit = True

    def close(self):
        pass


class Panel:
    """Buttons and lights. Falls back to fakes when not on a Pi."""

    def __init__(self, pins, simulate=False):
        self.leds = {}
        self.buttons = []
        self.real = False
        if not simulate:
            try:
                from gpiozero import LED, Button
                for name in ("tally", "green", "yellow", "red"):
                    self.leds[name] = LED(pins[name])
                self._record = Button(pins["record"], pull_up=True, bounce_time=0.05)
                self._mode = Button(pins["mode"], pull_up=True, bounce_time=0.05)
                self.buttons = [self._record, self._mode]
                self.real = True
            except Exception as e:  # not a Pi, or gpio busy
                log(f"GPIO unavailable ({e}); buttons disabled, lights simulated")
        if not self.real:
            self.leds = {n: FakeLED(n) for n in ("tally", "green", "yellow", "red")}

    def on_record(self, fn):
        if self.real:
            self._record.when_pressed = fn

    def on_mode(self, fn):
        if self.real:
            self._mode.when_pressed = fn

    def lights(self, color):
        """color: None, 'green', 'yellow', 'red', or 'red_blink'."""
        for name in ("green", "yellow", "red"):
            led = self.leds[name]
            if color == "red_blink" and name == "red":
                led.blink(0.4, 0.4)
            elif name == color:
                led.on()
            else:
                led.off()

    def state(self):
        return {n: bool(l.is_lit) for n, l in self.leds.items()}


# ---------------------------------------------------------------------------
# Beeper (PWM audio -> PAM8302 -> speaker)
# ---------------------------------------------------------------------------

class Beeper:
    SOUNDS = {
        "start": [(660, 0.09), (0, 0.04), (880, 0.09), (0, 0.04), (1320, 0.18)],
        "stop": [(1320, 0.09), (0, 0.04), (880, 0.09), (0, 0.04), (660, 0.18)],
        "error": [(220, 0.25), (0, 0.08), (220, 0.25), (0, 0.08), (220, 0.25)],
        "click": [(1800, 0.015), (0, 0.03), (900, 0.02)],
        "tick": [(1000, 0.07)],
        "ready": [(880, 0.08), (0, 0.05), (1175, 0.12)],
    }

    def __init__(self, device, volume, simulate=False):
        self.device = device
        self.enabled = bool(shutil.which("aplay")) and not simulate
        self.dir = Path("/tmp/speechcam-sounds")
        self.dir.mkdir(exist_ok=True)
        for name, notes in self.SOUNDS.items():
            self._write(self.dir / f"{name}.wav", notes, volume)

    @staticmethod
    def _write(path, notes, volume, rate=22050):
        frames = bytearray()
        for freq, dur in notes:
            n = int(rate * dur)
            for i in range(n):
                env = min(1.0, i / 200, (n - i) / 200)  # avoid clicks
                v = math.sin(2 * math.pi * freq * i / rate) if freq else 0.0
                frames += struct.pack("<h", int(32767 * volume * env * v))
        with wave.open(str(path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(rate)
            w.writeframes(bytes(frames))

    def play(self, name, count=1, wait=False):
        if not self.enabled:
            return
        def run():
            for _ in range(count):
                subprocess.run(["aplay", "-q", "-D", self.device, str(self.dir / f"{name}.wav")],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(0.12)
        if wait:
            run()
        else:
            threading.Thread(target=run, daemon=True).start()


# ---------------------------------------------------------------------------
# Background finisher: MKV master -> MP4, only while idle
# ---------------------------------------------------------------------------

class Transcoder(threading.Thread):
    def __init__(self, cfg, simulate=False):
        super().__init__(daemon=True)
        self.cfg = cfg
        self.simulate = simulate
        self.queue = []
        self.cv = threading.Condition()
        self.proc = None
        self.current = None
        self.paused = False

    def add(self, path):
        with self.cv:
            self.queue.append(Path(path))
            self.cv.notify()

    def pending(self):
        with self.cv:
            names = [p.name for p in self.queue]
        return ([self.current.name] if self.current else []) + names

    def pause(self):
        # Recording needs every CPU cycle on a Pi Zero
        self.paused = True
        if self.proc and self.proc.poll() is None:
            self.proc.send_signal(signal.SIGSTOP)

    def resume(self):
        self.paused = False
        if self.proc and self.proc.poll() is None:
            self.proc.send_signal(signal.SIGCONT)
        with self.cv:
            self.cv.notify()

    def _cmd(self, src, dst, encoder):
        if self.cfg["camera"] == "picamera" and not self.cfg["crop"]:
            # already H.264: only the audio needs encoding (~1 min per speech)
            return ["nice", "-n", "15", "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                    "-i", str(src), "-c:v", "copy", "-c:a", "aac", "-b:a", "128k",
                    "-movflags", "+faststart", str(dst)]
        vf = ",".join(f for f in (self.cfg["crop"], "format=yuv420p") if f)
        cmd = ["nice", "-n", "15", "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
               "-i", str(src), "-vf", vf]
        if encoder == "hw":
            cmd += ["-c:v", "h264_v4l2m2m", "-b:v", self.cfg["transcode_bitrate"]]
        else:
            cmd += ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "26"]
        return cmd + ["-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(dst)]

    def run(self):
        while True:
            with self.cv:
                while not self.queue or self.paused:
                    self.cv.wait()
                src = self.queue.pop(0)
            self.current = src
            dst = src.with_suffix(".mp4")
            tmp = src.with_suffix(".part.mp4")
            ok = False
            for encoder in (("sw",) if self.simulate else ("hw", "sw")):
                log(f"transcode {src.name} ({encoder})")
                self.proc = subprocess.Popen(self._cmd(src, tmp, encoder))
                if self.paused:
                    self.proc.send_signal(signal.SIGSTOP)
                if self.proc.wait() == 0:
                    ok = True
                    break
                log(f"transcode with {encoder} failed")
            self.proc = None
            self.current = None
            if ok:
                tmp.rename(dst)
                if not self.cfg["keep_master"]:
                    src.unlink(missing_ok=True)
                log(f"done: {dst.name}")
            else:
                tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Recorder
# ---------------------------------------------------------------------------

def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]


class SpeechCam:
    def __init__(self, cfg, simulate=False):
        self.cfg = cfg
        self.simulate = simulate
        self.dir = Path(cfg["recordings_dir"]).expanduser()
        self.dir.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self.panel = Panel(cfg["pins"], simulate)
        self.beeper = Beeper(cfg["beep_device"], cfg["volume"], simulate)
        self.transcoder = Transcoder(cfg, simulate)
        self.transcoder.start()
        self.proc = None
        self.cam_proc = None
        self.started = None
        self.current = None
        self.events = {}
        self.error = None
        self.speaker = ""
        self.profile_index = next((i for i, p in enumerate(cfg["profiles"])
                                   if p["id"] == cfg["default_profile"]), 0)
        self.panel.on_record(self.toggle)
        self.panel.on_mode(self.next_profile)
        # Re-queue masters left from a power cut or an earlier run
        if cfg["transcode"]:
            for mkv in sorted(self.dir.glob("*.mkv")):
                if not mkv.with_suffix(".mp4").exists():
                    self.transcoder.add(mkv)
        threading.Thread(target=self._tick, daemon=True).start()

    # -- state ------------------------------------------------------------
    @property
    def profile(self):
        return self.cfg["profiles"][self.profile_index]

    def recording(self):
        return self.proc is not None and self.proc.poll() is None

    def elapsed(self):
        return time.monotonic() - self.started if self.recording() else 0.0

    def light_for(self, t):
        p = self.profile
        if "red" not in p:
            return None
        if t >= p["red"] + GRACE_SECONDS:
            return "red_blink"
        for color in ("red", "yellow", "green"):
            if t >= p[color]:
                return color
        return None

    def status(self):
        t = self.elapsed()
        du = shutil.disk_usage(self.dir)
        return {
            "recording": self.recording(),
            "elapsed": round(t, 1),
            "light": self.light_for(t) if self.recording() else None,
            "file": self.current.name if self.current and self.recording() else None,
            "profile": self.profile["id"],
            "profiles": [{"id": p["id"], "name": p["name"]} for p in self.cfg["profiles"]],
            "speaker": self.speaker,
            "error": self.error,
            "free_mb": du.free // 2**20,
            "processing": self.transcoder.pending(),
            "leds": self.panel.state(),
        }

    # -- controls ---------------------------------------------------------
    def toggle(self):
        if self.recording():
            self.stop()
        else:
            self.start()

    def next_profile(self):
        if self.recording():
            return
        self.set_profile(self.cfg["profiles"][(self.profile_index + 1) % len(self.cfg["profiles"])]["id"])
        # beep the profile number so you can change it without the web page
        self.beeper.play("tick", count=self.profile_index + 1)

    def set_profile(self, pid):
        with self.lock:
            for i, p in enumerate(self.cfg["profiles"]):
                if p["id"] == pid:
                    self.profile_index = i
                    log(f"profile: {p['name']}")
                    return True
        return False

    def _camera_cmd(self):
        """Process that writes raw H.264 to stdout (Pi camera mode)."""
        c = self.cfg
        if self.simulate:
            return ["ffmpeg", "-hide_banner", "-loglevel", "error", "-re", "-f", "lavfi",
                    "-i", f"testsrc2=size={c['video_size']}:rate={c['video_fps']}",
                    "-c:v", "libx264", "-preset", "ultrafast", "-tune", "zerolatency",
                    "-g", str(c["video_fps"] * 2), "-f", "h264", "-"]
        width, height = c["video_size"].split("x")
        exe = shutil.which("rpicam-vid") or shutil.which("libcamera-vid") or "rpicam-vid"
        return [exe, "-t", "0", "-n", "--codec", "h264", "--inline",
                "--width", width, "--height", height, "--framerate", str(c["video_fps"]),
                "--bitrate", str(c["video_bitrate"]), "--intra", str(c["video_fps"] * 2),
                *shlex.split(c["camera_options"]), "-o", "-"]

    def _audio_input(self):
        c = self.cfg
        if self.simulate:
            return ["-re", "-f", "lavfi", "-i", f"sine=frequency=440:sample_rate={c['audio_rate']}"]
        audio = find_audio_device(c["audio_match"]) if c["audio_device"] == "auto" else c["audio_device"]
        if not audio:
            log("warning: no microphone found, recording video only")
            return []
        offset = ["-itsoffset", str(c["audio_offset"])] if c["audio_offset"] else []
        return ["-thread_queue_size", "2048", *offset, "-f", "alsa", "-ac", str(c["audio_channels"]),
                "-ar", str(c["audio_rate"]), "-i", audio]

    def _ffmpeg_cmd(self, out, video_fd=None):
        c = self.cfg
        if video_fd is not None:
            # Raw H.264 has no timestamps: stamp frames on arrival, which is
            # the same clock ALSA uses, so sound and picture stay in sync
            audio = self._audio_input()
            cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
                   "-thread_queue_size", "1024", "-use_wallclock_as_timestamps", "1",
                   "-probesize", "1M", "-f", "h264", "-i", f"/dev/fd/{video_fd}", *audio]
            if audio:
                cmd += ["-map", "0:v", "-map", "1:a"]
            return cmd + ["-c:v", "copy", "-c:a", "pcm_s16le", "-f", "matroska", str(out)]
        video = find_video_device() if c["video_device"] == "auto" else c["video_device"]
        audio = find_audio_device(c["audio_match"]) if c["audio_device"] == "auto" else c["audio_device"]
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
               "-thread_queue_size", "512", "-f", "v4l2", "-input_format", "mjpeg",
               "-video_size", c["video_size"], "-framerate", str(c["video_fps"]),
               "-ts", "mono2abs", "-i", video]
        if audio:
            cmd += ["-thread_queue_size", "2048", "-f", "alsa", "-ac", str(c["audio_channels"]),
                    "-ar", str(c["audio_rate"]), "-i", audio, "-map", "0:v", "-map", "1:a"]
        else:
            log("warning: no microphone found, recording video only")
        # Copy the camera's MJPEG as-is: the Pi Zero can't encode live
        return cmd + ["-c:v", "copy", "-c:a", "pcm_s16le", "-f", "matroska", str(out)]

    def start(self):
        with self.lock:
            if self.recording():
                return
            free = shutil.disk_usage(self.dir).free // 2**20
            if free < self.cfg["min_free_mb"]:
                return self._fail(f"SD card nearly full ({free} MB free)")
            stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            name = "_".join(x for x in (stamp, slug(self.speaker), self.profile["id"]) if x)
            self.current = self.dir / f"{name}.mkv"
            self.transcoder.pause()
            self.beeper.play("start", wait=True)   # finish the chime before the mic opens
            # stderr to a file: a full pipe would stall ffmpeg mid-speech
            self.errlog = open(self.dir / ".ffmpeg.log", "w+")
            if self.cfg["camera"] == "picamera":
                read_fd, write_fd = os.pipe()
                cam_cmd = self._camera_cmd()
                log("camera:", " ".join(cam_cmd))
                self.cam_proc = subprocess.Popen(cam_cmd, stdout=write_fd, stderr=self.errlog,
                                                 stdin=subprocess.DEVNULL)
                os.close(write_fd)
                cmd = self._ffmpeg_cmd(self.current, video_fd=read_fd)
                log("record:", " ".join(cmd))
                self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=self.errlog,
                                             pass_fds=(read_fd,))
                os.close(read_fd)
            else:
                cmd = self._ffmpeg_cmd(self.current)
                log("record:", " ".join(cmd))
                self.proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=self.errlog)
            self.started = time.monotonic()
            self.events = {}
            self.error = None
            self.panel.leds["tally"].on()
            # ffmpeg exits at once if the camera or mic is missing
            time.sleep(1.0)
            if self.proc.poll() is not None or self._camera_died():
                self._stop_camera()
                if self.proc.poll() is None:
                    self.proc.kill()
                self.proc = None
                self.current.unlink(missing_ok=True)
                return self._fail("recorder failed: " + self._last_error())
            log(f"recording {self.current.name}")

    def stop(self):
        with self.lock:
            if not self.proc:
                return
            duration = self.elapsed()
            proc, self.proc = self.proc, None
            try:
                proc.stdin.write(b"q")          # ffmpeg's clean shutdown
                proc.stdin.flush()
            except OSError:
                pass
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.send_signal(signal.SIGINT)
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
            self._stop_camera()
            self.panel.leds["tally"].off()
            self.panel.lights(None)
            self.beeper.play("stop")
            self._write_sidecar(duration)
            log(f"stopped after {duration:.1f}s")
            if self.cfg["transcode"] and self.current.exists():
                self.transcoder.add(self.current)
            self.transcoder.resume()

    def _camera_died(self):
        return self.cam_proc is not None and self.cam_proc.poll() is not None

    def _stop_camera(self):
        cam, self.cam_proc = self.cam_proc, None
        if cam and cam.poll() is None:
            cam.send_signal(signal.SIGINT)
            try:
                cam.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cam.kill()

    def _write_sidecar(self, duration):
        meta = {
            "file": self.current.name,
            "speaker": self.speaker,
            "profile": self.profile["name"],
            "duration_seconds": round(duration, 1),
            "lights_at_seconds": self.events,
            "verdict": self._verdict(duration),
            "recorded": datetime.now().isoformat(timespec="seconds"),
        }
        self.current.with_suffix(".json").write_text(json.dumps(meta, indent=2))

    def _verdict(self, t):
        p = self.profile
        if "red" not in p:
            return None
        if t < p["green"] - GRACE_SECONDS:
            return "under time"
        if t > p["red"] + GRACE_SECONDS:
            return "over time"
        return "within time"

    def _last_error(self):
        self.errlog.seek(0)
        lines = self.errlog.read().strip().splitlines()
        return lines[-1] if lines else "unknown error"

    def _fail(self, message):
        log("ERROR:", message)
        self.error = message
        self.panel.leds["tally"].blink(0.15, 0.15)
        self.beeper.play("error")
        self.transcoder.resume()
        threading.Timer(5, lambda: self.recording() or self.panel.leds["tally"].off()).start()

    def _tick(self):
        last = None
        while True:
            time.sleep(0.2)
            with self.lock:
                if self.proc and (self.proc.poll() is not None or self._camera_died()):
                    self.stop()
                    self._fail("recording stopped unexpectedly: " + self._last_error())
                    continue
                if not self.recording():
                    last = None
                    continue
                t = self.elapsed()
                light = self.light_for(t)
                if light != last:
                    self.panel.lights(light)
                    if light:
                        self.events.setdefault(light, round(t, 1))
                    last = light
                if t > self.cfg["max_minutes"] * 60:
                    log("max length reached")
                    self.stop()

    # -- files ------------------------------------------------------------
    def recordings(self):
        items = {}
        for f in self.dir.iterdir():
            if f.suffix not in (".mp4", ".mkv", ".json") or ".part" in f.name:
                continue
            if self.current and f == self.current and self.recording():
                continue
            entry = items.setdefault(f.stem, {"name": f.stem, "files": []})
            if f.suffix == ".json":
                try:
                    entry["meta"] = json.loads(f.read_text())
                except ValueError:
                    pass
            else:
                entry["files"].append({"name": f.name, "mb": round(f.stat().st_size / 2**20, 1)})
        return sorted(items.values(), key=lambda e: e["name"], reverse=True)

    def delete(self, stem):
        if not re.fullmatch(r"[\w.-]+", stem):
            return False
        if stem in [Path(n).stem for n in self.transcoder.pending()]:
            return False
        for ext in (".mp4", ".mkv", ".json"):
            (self.dir / f"{stem}{ext}").unlink(missing_ok=True)
        return True


# ---------------------------------------------------------------------------
# Web interface
# ---------------------------------------------------------------------------

def make_handler(cam):
    page = (HERE / "web.html").read_text()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def _json(self, obj, code=200):
            body = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            url = urllib.parse.urlparse(self.path)
            if url.path == "/":
                body = page.encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            elif url.path == "/api/status":
                self._json(cam.status())
            elif url.path == "/api/recordings":
                self._json(cam.recordings())
            elif url.path.startswith("/files/"):
                self._send_file(urllib.parse.unquote(url.path[len("/files/"):]))
            else:
                self._json({"error": "not found"}, 404)

        def _send_file(self, name):
            path = (cam.dir / name).resolve()
            if path.parent != cam.dir.resolve() or not path.is_file() or path.suffix not in (".mp4", ".mkv", ".json"):
                return self._json({"error": "not found"}, 404)
            types = {".mp4": "video/mp4", ".mkv": "video/x-matroska", ".json": "application/json"}
            self.send_response(200)
            self.send_header("Content-Type", types[path.suffix])
            self.send_header("Content-Length", str(path.stat().st_size))
            self.send_header("Content-Disposition", f'attachment; filename="{path.name}"')
            self.end_headers()
            with open(path, "rb") as f:
                shutil.copyfileobj(f, self.wfile, 1 << 16)

        def do_POST(self):
            length = int(self.headers.get("Content-Length") or 0)
            try:
                data = json.loads(self.rfile.read(length) or b"{}")
            except ValueError:
                return self._json({"error": "bad json"}, 400)
            path = urllib.parse.urlparse(self.path).path
            if path == "/api/start":
                if "speaker" in data:
                    cam.speaker = str(data["speaker"])[:60]
                cam.start()
            elif path == "/api/stop":
                cam.stop()
            elif path == "/api/settings":
                if cam.recording():
                    return self._json({"error": "busy recording"}, 409)
                if "profile" in data:
                    cam.set_profile(data["profile"])
                if "speaker" in data:
                    cam.speaker = str(data["speaker"])[:60]
            elif path == "/api/delete":
                if not cam.delete(str(data.get("name", ""))):
                    return self._json({"error": "cannot delete"}, 400)
            else:
                return self._json({"error": "not found"}, 404)
            self._json(cam.status())

    return Handler


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("command", nargs="?", default="run", choices=["run", "devices"])
    ap.add_argument("--config", help="path to config.toml")
    ap.add_argument("--simulate", action="store_true", help="fake camera/mic/GPIO for testing on a PC")
    args = ap.parse_args()

    if args.command == "devices":
        return print_devices()

    cfg = load_config(args.config)
    if args.simulate and cfg["recordings_dir"].startswith("/home/pi"):
        cfg["recordings_dir"] = str(HERE / "recordings")
    cam = SpeechCam(cfg, simulate=args.simulate)

    def shutdown(*_):
        cam.stop()
        sys.exit(0)
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)

    server = ThreadingHTTPServer(("0.0.0.0", cfg["web_port"]), make_handler(cam))
    log(f"SpeechCam ready - http://{os.uname().nodename}.local:{cfg['web_port']}/")
    cam.beeper.play("ready")
    server.serve_forever()


if __name__ == "__main__":
    main()

# SpeechCam: Club Speech Recorder

A speech recorder built into a 3D-printed 1920s cine camera. Press the shutter
button on top and it records the speaker. Toastmasters-style green / yellow /
red timing lights on the front show the speaker their time. Afterwards you
download an MP4 to your phone over Wi-Fi.

![SpeechCam](enclosure/render/front.png)

## How it works

```
 iPhone 6s Plus (camera, and viewfinder through the back window)
   └─ Lightning Digital AV Adapter ─ HDMI ─ USB capture dongle ─┐
 Wireless lav mic receiver ─────────────────────────────────────┼─ OTG hub ─ Pi Zero W
 Buttons, timing LEDs, REC tally, beeper (PAM8302 + speaker) ───┘   (GPIO)
```

- **The iPhone is only the camera.** It sends its screen out over HDMI and
  stores nothing, so its 668 MB of free space doesn't matter. Its screen shows
  through the back of the camera as the viewfinder.
- **The Pi Zero W records.** It can't encode video live, so it saves the
  capture dongle's MJPEG stream untouched with clean lav-mic audio (`.mkv`).
  Once the camera is idle, it converts that file to a small H.264 `.mp4`
  (about 110 MB per 5 minutes at the default 3 Mbps). The conversion pauses automatically if you
  start recording again.
- **Web page** at `http://speechcam.local:8080`: record/stop, speaker name,
  timing profile, a live timer, and downloads. Each recording gets a `.json`
  file listing when each light came on and whether the speech was within time.

## What you have and what it's for

| From your pile | Used for |
|---|---|
| Raspberry Pi Zero W ×2 | One is the recorder, one is a spare |
| Raspberry Pi Zero 1.3 ×2 | Not used (no Wi-Fi). Spares |
| Pimoroni GPIO Hammer Header | Solderless header for the Pi Zero W |
| Tactile button assortment | Bench testing before the panel buttons arrive |
| Adafruit PAM8302 amp + Gikfun 40 mm speaker | Start/stop/error beeps |
| DIY micro-USB solder plugs | 5 V pigtail into the Pi's PWR port |
| Micro-USB DIP breakouts | Fallback power inlet |
| Red/black LED-strip wire | 5 V power and LED wiring |
| 40-pin rainbow ribbon | Optional: run the GPIO out to a perma-proto board |
| Wireless lav mic (USB-C receiver) | Speech audio |
| iPhone 6s Plus | Camera + viewfinder |
| Blue display HAT | **Not used yet.** Tell me the model and I can add a status screen |

## Shopping list

| Item | Qty | ≈ Cost | Notes |
|---|---|---|---|
| **Apple Lightning Digital AV Adapter** (MD826AM/A) | 1 | $40–50 | Get the genuine one. Cheap clones often show a black screen |
| **USB HDMI capture dongle**, MS2109 type ("HDMI to USB 2.0, 1080p") | 1 | $12–18 | Must support USB 2.0 and MJPEG 1280×720 |
| Short HDMI cable, male–male, 0.3–0.5 m, thin | 1 | $7 | Has to coil up inside the box |
| **Micro-USB OTG hub**, 3–4 ports (or a pogo-pin USB hub board for Pi Zero) | 1 | $10–15 | |
| USB-A male → USB-C male cable, short | 1 | $5 | Lav receiver → hub |
| 5 V 3 A USB-C power supply | 1 | $10 | |
| USB-C female breakout (with 5.1 kΩ CC resistors) + USB-A female breakout | 1 each | $4 | Power inlet + phone charging port |
| microSD, 32 GB A1 or better | 1 | $8 | |
| 16 mm momentary panel push buttons (brass) | 3 | $10 | Record, Mode, Power |
| 5 mm LEDs: 2 red, 1 yellow, 1 green, plus 4 × 330 Ω resistors | 1 set | $3 | Optional 8 mm chrome LED holders |
| 270 Ω resistor + 33 nF capacitor | 1 | — | Audio filter |
| M3 × 10 self-tapping screws ×8, M2.5 screws ×2, 1/4"-20 nut | | $5 | |
| Filament: wood/brown PLA, brass/gold PLA, black matte PLA | | | |

The Mini-HDMI adapter on the original supplies sheet isn't needed: the Pi
runs headless.

## Build in this order

### Phase 0: prove the video chain on a laptop (before buying Pi parts)

1. Plug iPhone → AV adapter → HDMI → capture dongle → laptop. Open the Camera
   app, OBS, or QuickTime (*New Movie Recording*, then pick the dongle).
2. On the iPhone, open the Camera app in **Video** mode and turn it to
   landscape. Confirm the laptop shows the picture.
3. Note how much of the Camera app's buttons appear in the HDMI picture.
   iOS mirrors the whole screen. You can crop them out later with the `crop`
   setting, or use a camera app that outputs a clean HDMI feed.
4. Plug the lav receiver into the laptop and check that it appears as a
   microphone.

If any of these fail, it's much cheaper to find out now.

### Phase 1: software on the Pi

1. Use **Raspberry Pi Imager** to flash **Raspberry Pi OS Lite (32-bit)**. In
   the settings, set hostname `speechcam`, user `pi`, your Wi-Fi, and enable
   SSH.
2. Copy this folder over and install:
   ```bash
   scp -r speech-recorder/software pi@speechcam.local:~/speechcam
   ssh pi@speechcam.local
   cd ~/speechcam && sudo ./install.sh            # add --hotspot for club use (see below)
   sudo reboot
   ```
3. Plug in the hub, capture dongle, and lav receiver, then run
   `python3 /opt/speechcam/speechcam.py devices`. Check that the camera
   lists **MJPG 1280x720** and that your mic was auto-picked.
4. Open `http://speechcam.local:8080` on your phone and make a test
   recording.

**Wi-Fi at the club:** `sudo HOTSPOT_PASSWORD=yourpass ./install.sh --hotspot`
sets up a fallback. The Pi joins your home Wi-Fi when it can find it.
Otherwise it creates its own network called **SpeechCam**. Join that
network and browse to `http://10.42.0.1:8080`.

### Phase 2: buttons, lights, beeper

Wire them up as described in [docs/WIRING.md](docs/WIRING.md). Test on a breadboard with
the tactile buttons from your kit, then move to the panel buttons.

### Phase 3: print and assemble

See [docs/ENCLOSURE.md](docs/ENCLOSURE.md). **Measure your phone first.** The lens
position comes from where the iPhone's camera sits.

## Using it at a meeting

1. Fit the phone, plug in power, and switch it on. Two rising beeps mean it's ready.
2. On the iPhone: Camera → Video → landscape. Turn on **Guided Access** so
   nobody can leave the Camera app. Set Auto-Lock to Never.
3. Press **MODE** (the crank) to choose the timing profile. The camera beeps
   the profile number, e.g. 5 beeps = Speech 5–7. Or pick it on the web page,
   where you can also type the speaker's name.
4. Press **RECORD** on top. You hear a rising chime, the REC jewel lights, and the
   timing lights run. Press again to stop.
5. Download MP4s from the web page later. Masters are deleted after conversion
   unless you set `keep_master = true`.

| Light | Meaning |
|---|---|
| Green | minimum time reached |
| Yellow | middle |
| Red | maximum time |
| Red blinking | 30 s over (disqualification in contests) |

The profiles, pins, and resolution are all set in `/etc/speechcam/config.toml`.

## Try the software without a Pi

```bash
cd software && python3 speechcam.py --simulate
# open http://localhost:8080 - a test pattern and tone stand in for camera and mic
```

## Troubleshooting

| Symptom | Fix |
|---|---|
| "recorder failed: … No such file" | Capture dongle not seen. Check `lsusb` and the hub. Some hubs need their own power |
| Mic not found | `arecord -l`, then set `audio_match` to part of its name |
| Choppy video / dropped frames | Use `video_fps = 25` or `video_size = "960x540"` |
| Black HDMI picture | Use a genuine Apple adapter. Charge the phone. Unplug and replug the adapter after the Camera app is open |
| No beeps | Check `aplay -l` for a "Headphones" card and the wiring to A+ |
| Logs | `journalctl -u speechcam -f` |

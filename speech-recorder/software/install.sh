#!/bin/bash
# SpeechCam installer for Raspberry Pi OS Lite (Bookworm, 32-bit) on a Pi Zero W.
# The Camera Module 3 is detected automatically (camera_auto_detect=1 is the default).
# Run from this folder:   sudo ./install.sh
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then echo "Run with sudo"; exit 1; fi
USER_NAME=${SUDO_USER:-pi}
HERE=$(cd "$(dirname "$0")" && pwd)
BOOT=/boot/firmware/config.txt
[ -f "$BOOT" ] || BOOT=/boot/config.txt

echo "== Packages"
apt-get update
apt-get install -y ffmpeg rpicam-apps-lite python3-gpiozero python3-lgpio v4l-utils alsa-utils

echo "== Program files -> /opt/speechcam"
mkdir -p /opt/speechcam /etc/speechcam
install -m 755 "$HERE/speechcam.py" /opt/speechcam/
install -m 644 "$HERE/web.html" /opt/speechcam/
[ -f /etc/speechcam/config.toml ] || install -m 644 "$HERE/config.toml" /etc/speechcam/
sed -i "s#/home/pi/recordings#/home/$USER_NAME/recordings#" /etc/speechcam/config.toml
sudo -u "$USER_NAME" mkdir -p "/home/$USER_NAME/recordings"

echo "== Boot config ($BOOT)"
add_line() { grep -qxF "$1" "$BOOT" || echo "$1" >> "$BOOT"; }
add_line "# --- speechcam ---"
add_line "dtparam=audio=on"
add_line "dtoverlay=audremap,pins_18_19"      # PWM audio on GPIO18 -> PAM8302
add_line "dtoverlay=gpio-shutdown,gpio_pin=3"  # power button: GPIO3 to GND

echo "== Service"
sed "s/^User=pi/User=$USER_NAME/; s/^Group=pi/Group=$USER_NAME/" "$HERE/speechcam.service" \
  > /etc/systemd/system/speechcam.service
systemctl daemon-reload
systemctl enable speechcam

if [ "${1:-}" = "--hotspot" ]; then
  # Fallback Wi-Fi: joins known networks first, otherwise starts its own
  # network "SpeechCam" (password below) so you can connect at the club.
  echo "== Hotspot fallback"
  nmcli con delete speechcam-ap >/dev/null 2>&1 || true
  nmcli con add type wifi ifname wlan0 con-name speechcam-ap autoconnect yes ssid SpeechCam \
    802-11-wireless.mode ap 802-11-wireless.band bg ipv4.method shared \
    wifi-sec.key-mgmt wpa-psk wifi-sec.psk "${HOTSPOT_PASSWORD:-speakup123}" \
    connection.autoconnect-priority -10
fi

echo
echo "Done. Reboot now:  sudo reboot"
echo "Then open http://$(hostname).local:8080 on your phone."
echo "Check the camera with:  rpicam-hello --list-cameras"
echo "Check the mic with:     python3 /opt/speechcam/speechcam.py devices"

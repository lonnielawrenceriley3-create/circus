# Enclosure: 1920s cine camera

![front](../enclosure/render/front.png)
![back](../enclosure/render/back.png)

Outer size: **215 × 90 × 147 mm** (W × D × H), plus reels on top. The body
needs a **220 × 220 mm** bed or larger (Ender 3, Prusa MK4, any Bambu).

## Why the lens is off to one side

The iPhone's camera sits in the corner of the phone, and its field of view is
wide (about 60° horizontally in video mode). The phone must therefore sit
**right behind the front wall**, with a short, flared lens barrel. A longer
tube would show up as a black ring in the video. The lens ends up near the
right edge. That's normal for an early movie camera, and the space on the
left holds the nameplate and the timing lights.

## Before printing: measure your phone

Open `enclosure/speechcam.scad` and check the values at the top:

| Parameter | Default (6s Plus, no case) | Measure |
|---|---|---|
| `phone_len` | 158.2 | long side |
| `phone_hgt` | 77.9 | short side |
| `phone_thk` | 7.3 | thickness |
| `cam_from_end` | 10.0 | short edge → **centre** of the rear lens |
| `cam_from_edge` | 10.0 | long edge → centre of the rear lens |

The bore allows ±3 mm of error in the camera position. If you change
anything, re-export the STLs (command at the top of the `.scad` file) and
check the model with `part="assembly"` in OpenSCAD.

## Parts

| STL | Qty | Suggested filament | Orientation / supports |
|---|---|---|---|
| `body.stl` | 1 | wood-fill PLA or brown PLA | as exported (front face down), **no supports** |
| `faceplate.stl` | 1 | gold / brass silk PLA | as exported, no supports |
| `lens.stl` | 1 | **black matte** PLA (stops glare inside the bore) | front-down as exported, no supports |
| `back.stl` | 1 | gold or brown | as exported, no supports |
| `reel.stl` | 2 | black or silver | flat |
| `reel_stand.stl` | 1 | gold | as exported |
| `axle_cap.stl` | 2 | gold | flat |
| `crank.stl` | 1 | gold | flat (handle up) |
| `rails.stl` | 1 (2 rails) | any | flat |
| `tray.stl` | 1 | any | flat |

Suggested settings: 0.2 mm layers, 3 walls, 15 % infill. The body is the long
print (≈ 12–16 h).

## Hardware

- 8 × M3 × 10 self-tapping screws (back panel)
- 2 × M2.5 × 6 screws for the Pi Zero (2 of the 4 holes is enough)
- 1 × 1/4"-20 hex nut, glued into the floor boss (standard tripod thread)
- 3 × 16 mm panel-mount momentary push buttons (brass ones look the part)
- Zip ties for the capture dongle and hub on the tray
- CA glue or E6000

## Assembly order

1. **Rails:** glue the short rail into the floor groove behind the phone
   slot and the tall rail into the groove under the shelf. Check that the
   phone goes in first: push its top edge up into the top slot, swing the
   bottom forward, then drop it onto the pads.
2. **Tripod nut:** drop the 1/4"-20 nut into the hex pocket in the floor
   boss and glue it.
3. **Faceplate:** glue it to the front. The LED holes and lens hole line it
   up.
4. **Lens:** press the spigot through the faceplate into the body. Glue it once
   you've confirmed the picture has no dark corners.
5. **Reel stand:** glue the pegs into the two holes on top. Slide the reels on,
   then glue the caps onto the axle tips. Glue only the caps, so the reels
   still spin.
6. **Buttons:** RECORD goes in the top hole and MODE in the right-side hole. Glue
   the crank ring around the MODE button bezel. POWER goes in the back panel.
7. **Speaker:** glue it behind the grille on the left side.
8. **Electronics:** fix the Pi Zero, hub, PAM8302 and capture dongle on the
   tray, set the tray on the shelf, and route the HDMI cable down through the
   slot to the AV adapter.
9. **Phone:** fit the phone, plug in the AV adapter and charge cable, and fit
   foam behind the left end so the phone stays pressed against the right end
   stop.
10. **Back panel:** screw it on. The phone screen shows through the
    "ground-glass" window as your viewfinder.

## Things to check

- In this orientation the iPhone's **volume buttons are on the bottom edge**.
  They sit over the gap between the two floor pads. If either button gets
  pressed, the camera app will take photos.
- If the video has dark corners, the lens isn't centred on the phone camera.
  Re-measure `cam_from_end` / `cam_from_edge`.

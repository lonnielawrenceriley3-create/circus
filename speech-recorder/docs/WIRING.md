# Wiring

All GPIO numbers are **BCM**. Physical pin numbers are in brackets.
Fit the Pimoroni GPIO Hammer Header to the Pi Zero W first (no soldering).

## Pin map

| Function | Where on the camera | BCM | Pin | Wire to |
|---|---|---|---|---|
| RECORD button | left side, inside the focus knob | GPIO17 | [11] | button → GND [9] |
| MODE button | right side, inside the crank | GPIO27 | [13] | button → GND [14] |
| POWER button | back door | GPIO3 | [5] | button → GND [6]. Hold to shut down, press to wake. Handled by the kernel, not the app |
| REC tally LED (red) | lens board, bottom left | GPIO22 | [15] | 330 Ω → LED anode (long leg), cathode → GND [20] |
| Timing light, green | hood, left | GPIO5 | [29] | 330 Ω → LED → GND [30] |
| Timing light, yellow | hood, middle | GPIO6 | [31] | 330 Ω → LED → GND [34] |
| Timing light, red | hood, right | GPIO26 | [37] | 330 Ω → LED → GND [39] |
| Beeper audio (PWM) | back door | GPIO18 | [12] | RC filter → PAM8302 **A+** |
| PAM8302 power | | 5V | [4] | PAM8302 **VIN**; PAM8302 **GND** and **A−** → GND [25] |

Leave GPIO19 [35] unconnected: the PWM audio overlay claims it.

## Diagram

```
                      Raspberry Pi Zero W (mounted upright on the back door)
                       ┌─────────────────────────────────────────────┐
          POWER btn ── │ [5]  GPIO3        [6]  GND ─────── POWER btn  │
                       │ [9]  GND ── RECORD btn                      │
        RECORD btn ─── │ [11] GPIO17       [12] GPIO18 ── 270Ω ──┬── A+  PAM8302
          MODE btn ─── │ [13] GPIO27       [14] GND ── MODE btn  33nF  A−  ── GND
     tally ─330Ω─ ──── │ [15] GPIO22                            GND   VIN ── 5V [4]
                       │                   [20] GND ── LED cathodes   OUT+/− ── 40 mm speaker
     green ─330Ω─ ──── │ [29] GPIO5        [30] GND
    yellow ─330Ω─ ──── │ [31] GPIO6        [34] GND
       red ─330Ω─ ──── │ [37] GPIO26       [39] GND
                       │                                             │
                       │  CAM connector ◄── Zero camera cable ── Camera Module 3
                       │  PWR micro-USB ◄── 5 V pigtail from the USB-C inlet
                       │  USB micro-USB ◄── OTG cable ── lav receiver
                       └─────────────────────────────────────────────┘
```

The RC filter (270 Ω in series, 33 nF from A+ to GND) smooths the PWM. The
beeps still work without it but sound harsher.

## Power

```
 5 V 2.5 A USB-C supply → USB-C breakout (back door) → DIY micro-USB plug → Pi PWR port
```

Make the pigtail with one of the DIY micro-USB male solder connectors from
your kit (pin 1 = 5 V, pin 5 = GND). 22 AWG wire (your red/black LED-strip
wire) is plenty.

## Leave slack

The Pi, amp and speaker live on the back door, while the buttons, LEDs and
camera are in the body. Leave about 15 cm of wire on every run so the door
can swing open. Small 2-pin Dupont or JST connectors make it easy to unplug
the door.

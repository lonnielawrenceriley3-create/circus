# Wiring

All GPIO numbers are **BCM**. Physical pin numbers are in brackets.
Fit the Pimoroni GPIO Hammer Header to the Pi Zero W first (no soldering).

## Pin map

| Function | BCM | Pin | Wire to |
|---|---|---|---|
| RECORD button (top) | GPIO17 | [11] | button → GND [9] |
| MODE button (under the crank) | GPIO27 | [13] | button → GND [14] |
| POWER button (back) | GPIO3 | [5] | button → GND [6]. Hold to shut down, press to wake. Handled by the kernel, not by the app |
| REC tally LED (red) | GPIO22 | [15] | 330 Ω → LED anode (long leg), cathode → GND [20] |
| Timing light, green | GPIO5 | [29] | 330 Ω → LED → GND [30] |
| Timing light, yellow | GPIO6 | [31] | 330 Ω → LED → GND [34] |
| Timing light, red | GPIO26 | [37] | 330 Ω → LED → GND [39] |
| Beeper audio (PWM) | GPIO18 | [12] | RC filter → PAM8302 **A+** |
| PAM8302 power | 5V | [4] | PAM8302 **VIN**; PAM8302 **GND** and **A−** → GND [25] |

Leave GPIO19 [35] unconnected: the PWM audio overlay claims it.

## Diagram

```
                      Raspberry Pi Zero W (top view, header on the right)
                       ┌─────────────────────────────────────────────┐
          POWER btn ── │ [5]  GPIO3        [6]  GND ─────── POWER btn  │
                       │ [9]  GND ── REC btn                         │
           REC btn ─── │ [11] GPIO17       [12] GPIO18 ── 270Ω ──┬── A+  PAM8302
          MODE btn ─── │ [13] GPIO27       [14] GND ── MODE btn  33nF  A−  ── GND
     tally ─330Ω─ ──── │ [15] GPIO22                            GND   VIN ── 5V [4]
                       │                   [20] GND ── LED cathodes   OUT+/− ── 40 mm speaker
     green ─330Ω─ ──── │ [29] GPIO5        [30] GND
    yellow ─330Ω─ ──── │ [31] GPIO6        [34] GND
       red ─330Ω─ ──── │ [37] GPIO26       [39] GND
                       │                                             │
                       │  PWR micro-USB ◄── 5 V from the inlet       │
                       │  USB micro-USB ◄── OTG hub                  │
                       └─────────────────────────────────────────────┘
```

The RC filter (270 Ω in series, 33 nF from A+ to GND) smooths the PWM. The
beeps still work without it but sound harsher.

## USB and video chain

```
 iPhone 6s Plus ──Lightning── Apple Digital AV Adapter ──HDMI cable── USB capture dongle ─┐
                               └── Lightning charge port ◄── charging cable ◄── USB-A (5 V)  │
                                                                                            ├── OTG hub ── Pi "USB" port
 Wireless lav receiver ──USB-C → USB-A cable───────────────────────────────────────────────┘
```

## Power

One 5 V 3 A supply feeds everything through the back-panel inlet:

```
 5 V 3 A USB-C supply → USB-C breakout (back panel) ─┬─ DIY micro-USB plug → Pi PWR port
                                                     └─ USB-A female breakout → Lightning cable → AV adapter charge port
```

- Use the DIY micro-USB male solder connectors from your kit to make the short
  pigtail into the Pi's **PWR** port (pins 1 = 5 V, 5 = GND).
- Use 22 AWG wire for the 5 V runs. Your red/black LED-strip extension wire
  works.
- The micro-USB DIP breakouts you have can stand in for the USB-C inlet. Micro-USB
  is only rated for about 1.8 A, though, so expect the phone to charge slowly.

## LEDs

5 mm LEDs push in from inside through the front wall and the faceplate. If you
want chrome "jewel" bezels instead, use 8 mm LED holders and set
`led_d = 8.2` in `speechcam.scad` before exporting the body and faceplate.

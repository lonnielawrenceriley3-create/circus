#!/usr/bin/env python3
"""Draw SpeechCam's layout sheet (docs/layout.svg): front view, right-side
X-ray, top X-ray and the inside of the back door, with every component at
its real size and position. Numbers mirror speechcam.scad - if you change
the model, change them here too."""

import math
from pathlib import Path

# ---- geometry from speechcam.scad (mm) --------------------------------
W, D, H, WALL = 96, 80, 136, 2.6
CX, Z_T, Z_V, T = 48, 46, 98, 10
STD = (13, 83, 14, 126)                       # x0, x1, z0, z1
TAN = math.tan(math.radians(38.5))
LENS_Y = -7.7                                 # camera lens front
BORE = lambda L: 4 + L * TAN
HOOD = (8, 88, 7, 73, 136, 160)               # x0 x1 y0 y1 z0 z1
LIGHTS = [(31, "#3ddc4a"), (48, "#ffd400"), (65, "#ff3b30")]
LIGHT_Z = 148
BTN_Y, BTN_Z = 33.6, 87.04
TALLY = (21, 22)
PI = (18, 48, 30, 95)                         # x0 x1 z0 z1 (upright on the door)
PI_Y = (73.6, 75)
SPK = (68, 108, 20)
PWR = (72, 56)
CAM = (35.5, 60.5, 31.5, 55.5)

C = {
    "body": "#3b3835", "body_in": "#4d4945", "std": "#55514c", "chrome": "#c9c9c9",
    "pi": "#2e8b57", "cam": "#228b22", "ribbon": "#f39c12", "amp": "#4169e1",
    "spk": "#6b6b6b", "btn": "#d4a017", "usb": "#9b59b6", "lav": "#111",
    "plug": "#bfc5cc", "ink": "#1d1d1f", "dim": "#c0392b", "bg": "#fbfaf7",
}

S = 3.2   # px per mm


class View:
    def __init__(self, ox, oy, title, sub, top):
        """top = how far the view extends upward, in mm (for the title)."""
        self.ox, self.oy, self.el = ox, oy, []
        ty = oy - top * S - 48
        self.el.append(f'<text x="{ox - 120}" y="{ty}" class="vt">{title}</text>'
                       f'<text x="{ox - 120}" y="{ty + 18}" class="vs">{sub}</text>')

    def p(self, u, v):
        return self.ox + u * S, self.oy + v * S

    def rect(self, u0, u1, v0, v1, fill, stroke="none", rx=0, extra=""):
        x0, y0 = self.p(min(u0, u1), 0)
        x1, _ = self.p(max(u0, u1), 0)
        _, ya = self.p(0, min(v0, v1))
        _, yb = self.p(0, max(v0, v1))
        self.el.append(f'<rect x="{x0:.1f}" y="{ya:.1f}" width="{x1 - x0:.1f}" height="{yb - ya:.1f}" '
                       f'rx="{rx * S:.1f}" fill="{fill}" stroke="{stroke}" {extra}/>')

    def circle(self, u, v, r, fill, stroke="none", extra=""):
        x, y = self.p(u, v)
        self.el.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r * S:.1f}" fill="{fill}" stroke="{stroke}" {extra}/>')

    def poly(self, pts, fill, stroke="none", extra=""):
        s = " ".join("%.1f,%.1f" % self.p(u, v) for u, v in pts)
        self.el.append(f'<polygon points="{s}" fill="{fill}" stroke="{stroke}" {extra}/>')

    def line(self, pts, stroke, w=1.5, extra=""):
        s = " ".join("%.1f,%.1f" % self.p(u, v) for u, v in pts)
        self.el.append(f'<polyline points="{s}" fill="none" stroke="{stroke}" stroke-width="{w}" {extra}/>')

    def label(self, u, v, tu, tv, text, anchor="start"):
        """Leader from the point (u, v) to a label at (tu, tv)."""
        x, y = self.p(u, v)
        tx, ty = self.p(tu, tv)
        self.el.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{tx:.1f}" y2="{ty:.1f}" class="ld"/>'
                       f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.2" fill="{C["ink"]}"/>')
        dy = -4
        for i, t in enumerate(text.split("\n")):
            self.el.append(f'<text x="{tx + (4 if anchor == "start" else -4):.1f}" y="{ty + dy + i * 14:.1f}" '
                           f'text-anchor="{anchor}" class="lb">{t}</text>')

    def dim(self, u0, v0, u1, v1, off, text, vertical=False):
        """Dimension line offset by `off` mm."""
        if vertical:
            a, b = self.p(u0 + off, v0), self.p(u0 + off, v1)
            e0, e1 = self.p(u0, v0), self.p(u1, v1)
            self.el.append(f'<line x1="{e0[0]:.1f}" y1="{a[1]:.1f}" x2="{a[0]:.1f}" y2="{a[1]:.1f}" class="ex"/>'
                           f'<line x1="{e1[0]:.1f}" y1="{b[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" class="ex"/>')
            mx, my = a[0], (a[1] + b[1]) / 2
            rot = f'transform="rotate(-90 {mx - 5:.1f} {my:.1f})"'
            self.el.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" class="dm"/>'
                           f'<text x="{mx - 5:.1f}" y="{my:.1f}" {rot} text-anchor="middle" class="dt">{text}</text>')
        else:
            a, b = self.p(u0, v0 + off), self.p(u1, v0 + off)
            e0, e1 = self.p(u0, v0), self.p(u1, v1)
            self.el.append(f'<line x1="{a[0]:.1f}" y1="{e0[1]:.1f}" x2="{a[0]:.1f}" y2="{a[1]:.1f}" class="ex"/>'
                           f'<line x1="{b[0]:.1f}" y1="{e1[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" class="ex"/>')
            self.el.append(f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" class="dm"/>'
                           f'<text x="{(a[0] + b[0]) / 2:.1f}" y="{a[1] - 5:.1f}" text-anchor="middle" class="dt">{text}</text>')

    def svg(self):
        return "\n".join(self.el)


# Screen v grows downward, so pass v = -z (or -y) everywhere through these:
def front_view(ox, oy):
    v = View(ox, oy, "1 · FRONT", "what the speaker sees", 160)
    z = lambda zz: -zz
    v.rect(HOOD[0], HOOD[1], z(HOOD[4]), z(HOOD[5]), C["chrome"], C["ink"], 1)
    for x, col in LIGHTS:
        v.circle(x, z(LIGHT_Z), 4.6, C["chrome"], C["ink"])
        v.circle(x, z(LIGHT_Z), 2.5, col)
    v.rect(0, W, z(0), z(H), C["body"], rx=4)
    v.rect(*STD[:2], z(STD[2]), z(STD[3]), C["std"], C["ink"], 6)
    # knob (left) and crank (right) seen edge-on
    v.rect(-10, 0, z(BTN_Z - 18.5), z(BTN_Z + 18.5), C["chrome"], C["ink"], 1)
    v.rect(96.5, 100.5, z(BTN_Z - 14), z(BTN_Z + 14), C["chrome"], C["ink"], 1)
    v.rect(96.5, 100, z(BTN_Z - 30), z(BTN_Z), C["chrome"], C["ink"])
    v.rect(100, 108, z(BTN_Z - 32.6), z(BTN_Z - 27.4), C["chrome"], C["ink"])
    v.circle(111, z(BTN_Z - 30), 4, C["chrome"], C["ink"])
    # taking lens
    v.circle(CX, z(Z_T), 25, "#2a2724", C["chrome"], 'stroke-width="2"')
    v.circle(CX, z(Z_T), 19.5, "#1c1a18", C["chrome"])
    v.circle(CX, z(Z_T), BORE(15.3), "#0b0b0b")
    v.rect(CAM[0], CAM[1], z(CAM[2]), z(CAM[3]), "none", C["cam"], 0, 'stroke-dasharray="5 3" stroke-width="2"')
    v.rect(CX - 4.25, CX + 4.25, z(Z_T - 4.25), z(Z_T + 4.25), "#222", C["cam"])
    v.circle(CX, z(Z_T), 2.2, "#4a6fa5")
    # viewing lens
    v.circle(CX, z(Z_V), 20, "#2a2724", C["chrome"], 'stroke-width="2"')
    v.circle(CX, z(Z_V), 17, "#1c1a18")
    v.circle(CX, z(Z_V), 14.2, "#2c3e50", C["chrome"])
    for wx in (22, 74):
        v.circle(wx, z(74.5), 6.5, "#2a2724", C["chrome"])
    v.rect(22, 74, z(118.6), z(125.6), "#2a2724", C["chrome"], 1.5)
    x, y = v.p(CX, z(120.2))
    v.el.append(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="middle" class="np">SPEECHCAM</text>')
    v.circle(*TALLY[:1], z(TALLY[1]), 4.6, C["chrome"])
    v.circle(*TALLY[:1], z(TALLY[1]), 2.5, "#ff3b30")
    # labels
    v.label(65, z(LIGHT_Z), 120, z(160), "Timing lights\ngreen · yellow · red")
    v.label(CX + 3, z(Z_T + 6), 120, z(52), "Camera Module 3\nbehind taking lens")
    v.label(CX + 12, z(Z_V + 6), 120, z(110), "Viewing lens\n(decorative, 28 mm glass)")
    v.label(TALLY[0], z(TALLY[1]), -12, z(6), "REC light", "end")
    v.label(-5, z(BTN_Z + 10), -14, z(122), "Focus knob\n= RECORD", "end")
    v.label(111, z(BTN_Z - 30), 120, z(40), "Crank = MODE")
    v.dim(0, z(0), W, z(0), 9, "96")
    v.dim(0, z(0), 0, z(H), -52, "136", vertical=True)
    v.dim(0, z(H), 0, z(HOOD[5]), -52, "+24", vertical=True)
    return v


def side_view(ox, oy):
    v = View(ox, oy, "2 · RIGHT SIDE, X-RAY", "front on the left · everything inside drawn in place", 160)
    z = lambda zz: -zz
    # shell
    v.rect(0, D, z(0), z(H), C["body"], rx=4)
    v.rect(WALL, D - WALL, z(WALL), z(H - WALL), C["body_in"])
    v.rect(80, 83.8, z(3), z(133), C["body"], C["ink"])               # door
    v.rect(HOOD[2], HOOD[3], z(HOOD[4]), z(HOOD[5]), C["chrome"], C["ink"], 1)
    v.rect(HOOD[2] - 1.6, HOOD[2] + 8.6, z(LIGHT_Z - 2.5), z(LIGHT_Z + 2.5), "#ff3b30")
    # standard and lenses
    v.rect(-T, 0, z(14), z(126), C["std"], C["ink"], 1)
    v.rect(-14, -10, z(Z_T - 25), z(Z_T + 25), "#2a2724", C["chrome"])
    v.rect(-21.5, -14, z(Z_T - 18.5), z(Z_T + 18.5), "#2a2724", C["chrome"])
    v.rect(-23, -21.5, z(Z_T - 19.5), z(Z_T + 19.5), "#2a2724", C["chrome"])
    v.poly([(LENS_Y, z(Z_T - 4)), (-23, z(Z_T - BORE(15.3))), (-23, z(Z_T + BORE(15.3))), (LENS_Y, z(Z_T + 4))], "#0b0b0b")
    # field of view (vertical 41 deg) from the lens
    for s in (1, -1):
        v.line([(LENS_Y, z(Z_T)), (-40, z(Z_T + s * math.tan(math.radians(20.5)) * (40 + LENS_Y)))],
               "#4a6fa5", 1.2, 'stroke-dasharray="4 3"')
    v.rect(-13, -10, z(Z_V - 20), z(Z_V + 20), "#2a2724", C["chrome"])
    v.rect(-19, -13, z(Z_V - 17), z(Z_V + 17), "#2a2724", C["chrome"])
    v.rect(-20, -19, z(Z_V - 18), z(Z_V + 18), "#2c3e50", C["chrome"])
    v.rect(-16, -10, z(68), z(81), "#2a2724", C["chrome"])
    v.rect(-12, -3.4, z(TALLY[1] - 2.5), z(TALLY[1] + 2.5), "#ff3b30")
    # camera module
    v.rect(-1.2, -0.2, z(CAM[2]), z(CAM[3]), C["cam"])
    v.rect(LENS_Y, -1.2, z(Z_T - 4.25), z(Z_T + 4.25), "#111")
    v.rect(-0.2, 4.3, z(32), z(37.5), "#eee", C["ink"])
    # ribbon
    v.line([(4, z(34.5)), (4, z(12)), (71, z(12)), (71, z(31))], C["ribbon"], 4)
    # tripod boss and nut
    v.poly([(22, z(WALL)), (30, z(10.6)), (50, z(10.6)), (50, z(WALL))], C["body"], C["ink"])
    v.rect(33.6, 46.4, z(5), z(10.6), C["chrome"])
    # lav receiver and its cable to the Pi
    v.rect(14, 28, z(3), z(13), C["lav"], "#888")
    v.line([(28, z(8)), (60, z(8)), (60, z(60)), (71, z(70))], "#888", 2, 'stroke-dasharray="5 3"')
    # Pi Zero on the door
    v.rect(*PI_Y, z(PI[2]), z(PI[3]), C["pi"])
    v.rect(65.1, 73.6, z(37), z(88), "#555")
    v.rect(51.6, 65.1, z(37), z(88), "#111")
    v.rect(71, 74, z(67.4), z(75.4), C["plug"], C["ink"])
    v.rect(77, 78.6, z(27.5), z(43.5), C["amp"])
    v.rect(78.4, 80, z(17), z(27), C["usb"])
    v.rect(68, 79.5, z(SPK[1] - 20), z(SPK[1] + 20), C["spk"], C["ink"])
    v.rect(57, 83, z(PWR[1] - 8), z(PWR[1] + 8), "#888", C["ink"])
    v.rect(83, 85, z(PWR[1] - 9), z(PWR[1] + 9), C["btn"])
    # buttons end-on + crank
    v.circle(BTN_Y, z(BTN_Z), 14, C["chrome"], C["ink"], 'fill-opacity="0.85"')
    v.circle(BTN_Y, z(BTN_Z), 9, C["btn"])
    v.rect(BTN_Y - 1.75, BTN_Y + 1.75, z(BTN_Z - 30), z(BTN_Z - 6), C["chrome"], C["ink"])
    v.circle(BTN_Y, z(BTN_Z - 30), 4, C["chrome"], C["ink"])
    # labels
    v.label(-23, z(Z_T - 12), -32, z(14), "Flared bore =\ncamera's view", "end")
    v.label(-4, z(Z_T + 4), -32, z(64), "Camera Module 3\n(25×24×11.5)", "end")
    v.label(66, z(12), 92, z(8), "Zero camera cable\n(150 mm)")
    v.label(21, z(8), -32, z(2), "Lav receiver", "end")
    v.label(36, z(8), -32, z(-12), "Tripod nut 1/4\"", "end")
    v.label(74.3, z(PI[3] - 4), 92, z(100), "Pi Zero W\n+ GPIO header")
    v.label(73.7, z(SPK[1]), 92, z(126), "40 mm speaker")
    v.label(84, z(PWR[1]), 92, z(62), "POWER button")
    v.label(77.8, z(35), 92, z(40), "PAM8302 amp")
    v.label(79.2, z(22), 92, z(22), "USB-C 5 V inlet")
    v.label(BTN_Y + 9, z(BTN_Z), 92, z(82), "MODE button\ninside the crank")
    v.dim(0, z(0), D, z(0), 9, "80 body")
    v.dim(-23, z(0), 0, z(0), 9, "23")
    return v


def top_view(ox, oy):
    v = View(ox, oy, "3 · TOP, X-RAY", "front at the bottom · all heights overlaid", 86)
    y = lambda yy: -yy
    v.rect(0, W, y(0), y(D), C["body"], rx=4)
    v.rect(WALL, W - WALL, y(WALL), y(D - WALL), C["body_in"])
    v.rect(4, 92, y(80), y(83.8), C["body"], C["ink"])
    v.rect(HOOD[0], HOOD[1], y(HOOD[2]), y(HOOD[3]), "none", C["chrome"], 1, 'stroke-dasharray="6 4" stroke-width="2"')
    v.rect(13, 83, y(-T), y(0), C["std"], C["ink"], 1)
    v.rect(23, 73, y(-14), y(-10), "#2a2724", C["chrome"])
    v.rect(29.5, 66.5, y(-21.5), y(-14), "#2a2724", C["chrome"])
    v.poly([(CX - 4, y(LENS_Y)), (CX - BORE(15.3), y(-23)), (CX + BORE(15.3), y(-23)), (CX + 4, y(LENS_Y))], "#0b0b0b")
    for s in (1, -1):   # horizontal field of view, 66 deg
        v.line([(CX, y(LENS_Y)), (CX + s * math.tan(math.radians(33)) * (34 + LENS_Y), y(-34))],
               "#4a6fa5", 1.2, 'stroke-dasharray="4 3"')
    v.rect(*CAM[:2], y(-1.2), y(-0.2), C["cam"])
    v.rect(CX - 4.25, CX + 4.25, y(LENS_Y), y(-1.2), "#111")
    v.rect(38, 58, y(-0.2), y(4.3), "#eee", C["ink"])
    v.circle(CX, y(40), 10, C["body"], C["ink"])
    v.line([(CX, y(4)), (CX, y(71)), (33, y(71))], C["ribbon"], 13 * S * 0.35)
    v.rect(8, 36, y(14), y(28), C["lav"], "#888")
    # side buttons, knob, crank
    for x0, x1 in ((0, 26), (70, 96)):
        v.rect(x0, x1, y(BTN_Y - 8), y(BTN_Y + 8), "#888", C["ink"])
    v.rect(-10, -0.5, y(BTN_Y - 18.5), y(BTN_Y + 18.5), C["chrome"], C["ink"], 1)
    v.rect(96.5, 100.5, y(BTN_Y - 14), y(BTN_Y + 14), C["chrome"], C["ink"], 1)
    v.rect(100, 108, y(BTN_Y - 2.6), y(BTN_Y + 2.6), C["chrome"], C["ink"])
    v.circle(111, y(BTN_Y), 4, C["chrome"], C["ink"])
    # door-mounted parts
    v.rect(PI[0], PI[1], y(PI_Y[0]), y(PI_Y[1]), C["pi"])
    v.rect(18.5, 23.5, y(51.6), y(73.6), "#111")
    v.rect(48, 68, y(71), y(74), C["plug"], C["ink"])
    v.rect(48, 88, y(68), y(79.5), C["spk"], C["ink"], 0, 'fill-opacity="0.8"')
    v.rect(64, 80, y(57), y(85), "#888", C["ink"])
    v.rect(53.5, 74.5, y(77), y(78.6), C["amp"])
    v.label(13, y(BTN_Y), -14, y(70), "RECORD button\nbody (26 deep)", "end")
    v.label(83, y(BTN_Y), 118, y(48), "MODE button")
    v.label(CX, y(30), 118, y(30), "Camera cable\nalong the floor")
    v.label(22, y(21), -14, y(10), "Lav receiver", "end")
    v.label(21, y(62), -14, y(52), "Header + Dupont\nplugs (22 deep)", "end")
    v.label(72, y(64), 118, y(64), "POWER button")
    v.label(68, y(73), 118, y(86), "Speaker / OTG plug")
    v.label(CX + 16, y(-30), 118, y(-26), "66° view")
    v.dim(0, y(0), W, y(0), 30, "96")
    return v


def door_view(ox, oy):
    v = View(ox, oy, "4 · BACK DOOR, INSIDE", "seen from inside the camera", 133)
    z = lambda zz: -zz
    v.rect(4, 92, z(3), z(133), C["body"], C["ink"], 3)
    for sx, sz in ((9.6, 9.6), (86.4, 9.6), (9.6, 126.4), (86.4, 126.4)):
        v.circle(sx, z(sz), 1.7, "#111")
    v.rect(*PI[:2], z(PI[2]), z(PI[3]), C["pi"], C["ink"], 1.5)
    for hx, hz in ((21.5, 33.5), (44.5, 33.5), (21.5, 91.5), (44.5, 91.5)):
        v.circle(hx, z(hz), 2.8, "#d9d9d9", C["ink"])
    v.rect(18.5, 23.5, z(37), z(88), "#111")
    v.rect(22, 44, z(30), z(34), "#eee", C["ink"])                    # camera connector
    v.rect(48, 68, z(67.4), z(75.4), C["plug"], C["ink"])              # OTG plug
    v.rect(48, 58, z(80), z(88), C["plug"], C["ink"])                  # PWR pigtail
    v.rect(53.5, 74.5, z(27.5), z(43.5), C["amp"], C["ink"])
    v.circle(SPK[0], z(SPK[1]), 22, "none", C["ink"])
    v.circle(SPK[0], z(SPK[1]), 20, C["spk"], C["ink"])
    v.circle(PWR[0], z(PWR[1]), 8, "#888", C["ink"])
    v.rect(60, 72, z(17), z(27), C["usb"], C["ink"])
    v.line([(33, z(30)), (33, z(14))], C["ribbon"], 11 * S * 0.35)
    v.label(30, z(64), -14, z(64), "Pi Zero W\n(USB ports face right)", "end")
    v.label(21, z(60), -14, z(100), "GPIO header", "end")
    v.label(33, z(32), -14, z(32), "Camera connector", "end")
    v.label(58, z(71.4), 104, z(84), "USB: OTG cable\nto lav receiver")
    v.label(53, z(84), 104, z(100), "PWR: 5 V pigtail")
    v.label(SPK[0] + 10, z(SPK[1] + 10), 104, z(126), "Speaker 40 mm")
    v.label(PWR[0] + 6, z(PWR[1]), 104, z(56), "POWER button")
    v.label(70, z(36), 104, z(36), "PAM8302 amp")
    v.label(68, z(22), 104, z(18), "USB-C inlet")
    v.dim(4, z(3), 92, z(3), 9, "88")
    return v


def legend(ox, oy):
    rows = [
        (C["cam"], "Raspberry Pi Camera Module 3, standard (SC0872)", "25 × 24 × 11.5 mm"),
        (C["ribbon"], "Raspberry Pi Zero camera cable (SC0002)", "150 mm"),
        (C["pi"], "Raspberry Pi Zero W", "65 × 30 mm, on 5 mm standoffs"),
        (C["amp"], "Adafruit PAM8302 amplifier", "in a printed cradle"),
        (C["spk"], "Gikfun 40 mm speaker", "behind the grille"),
        ("#888", "16 mm panel push buttons ×3", "~26 mm deep behind the panel"),
        (C["usb"], "USB-C breakout (5 V in)", "behind the slot"),
        (C["lav"], "Wireless lav receiver", "loose on the floor"),
    ]
    out = [f'<text x="{ox}" y="{oy}" class="vt">PARTS</text>']
    for i, (col, name, size) in enumerate(rows):
        y = oy + 24 + i * 22
        out.append(f'<rect x="{ox}" y="{y - 11}" width="14" height="14" rx="3" fill="{col}"/>'
                   f'<text x="{ox + 22}" y="{y}" class="lb">{name}</text>'
                   f'<text x="{ox + 370}" y="{y}" class="ls">{size}</text>')
    y = oy + 24 + len(rows) * 22 + 14
    notes = ["Tightest fits (all clear):",
             "· OTG plug ↔ POWER button: 3.4 mm",
             "· PWR plug ↔ speaker rim: 2.4 mm",
             "· Header plugs ↔ RECORD button: 10 mm",
             "Leave ~15 cm of wire on every lead to the door."]
    for i, t in enumerate(notes):
        out.append(f'<text x="{ox}" y="{y + i * 18}" class="{"lb" if i == 0 else "ls"}">{t}</text>')
    return "\n".join(out)


def main():
    views = [front_view(300, 720), side_view(1120, 720), top_view(300, 1150), door_view(1120, 1330)]
    style = f"""
      text {{ font-family: -apple-system, 'Segoe UI', Roboto, sans-serif; fill: {C['ink']}; }}
      .vt {{ font-size: 20px; font-weight: 700; letter-spacing: 1px; }}
      .vs {{ font-size: 13px; fill: #6b6b6b; }}
      .lb {{ font-size: 13px; font-weight: 600; }}
      .ls {{ font-size: 12.5px; fill: #555; }}
      .np {{ font-size: 15px; font-weight: 700; fill: #d8d8d8; font-family: Georgia, serif; dominant-baseline: middle; }}
      .ld {{ stroke: {C['ink']}; stroke-width: 1; }}
      .ex {{ stroke: {C['dim']}; stroke-width: 0.8; }}
      .dm {{ stroke: {C['dim']}; stroke-width: 1.2; marker-start: url(#a); marker-end: url(#a); }}
      .dt {{ font-size: 13px; font-weight: 700; fill: {C['dim']}; }}
    """
    width, height = 1640, 1720
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
           f'<defs><marker id="a" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           f'<path d="M0,0 L10,5 L0,10 z" fill="{C["dim"]}"/></marker></defs>',
           f'<style>{style}</style>',
           f'<rect width="{width}" height="{height}" fill="{C["bg"]}"/>',
           f'<text x="40" y="54" style="font-size:30px;font-weight:800">SpeechCam: how everything fits</text>',
           f'<text x="40" y="80" class="vs">Twin-lens reflex enclosure · all dimensions in mm · drawn to scale ({S} px = 1 mm)</text>']
    svg += [v.svg() for v in views]
    svg.append(legend(180, 1420))
    svg.append("</svg>")
    out = Path(__file__).resolve().parent.parent / "docs" / "layout.svg"
    out.write_text("\n".join(svg))
    print(out)


if __name__ == "__main__":
    main()

// =====================================================================
//  SPEECHCAM - Club Speech Recorder enclosure
//  Styled after a 1950s twin-lens reflex (Rolleiflex / Flexaret type):
//  leatherette box, front lens standard with two stacked lenses,
//  waist-level finder hood, focus knob (RECORD) and crank (MODE).
//
//  A Raspberry Pi Camera Module 3 (standard lens) sits behind the lower
//  "taking" lens. The upper "viewing" lens is decorative - glue a 28 mm
//  glass cabochon into it for a real-glass look.
//
//  Coordinates (assembled):  x = width, left->right as seen from the FRONT
//                            y = depth, 0 = body front face, D = back face
//                            z = height, 0 = bottom
//
//  Render one part:   openscad -D 'part="body"' -o body.stl speechcam.scad
//  Parts: assembly, body, standard, door, hood, knob, crank
// =====================================================================

part = "assembly";

// ---------- Body ------------------------------------------------------
W      = 96;     // width
D      = 80;     // depth (body only; lenses add ~23 mm in front)
H      = 136;    // height (hood adds 24 mm on top)
corner = 4;      // vertical edge radius
wall   = 2.6;
btn_d  = 16.2;   // 16 mm panel-mount push buttons (RECORD, MODE, POWER)
led_d  = 5.2;    // 5 mm LEDs
screw_pilot = 2.5;   // M3 self-tapping
screw_clear = 3.4;

// ---------- Camera Module 3 (measure yours; the bore allows +-1.5 mm) --
cam_w       = 25;     // board width
cam_h       = 24;     // board height
cam_lens_top= 9.5;    // board top edge -> lens centre
cam_hole_dx = 21;     // M2 hole spacing, horizontal
cam_hole_top= [2, 14.5];  // M2 hole rows, from board top edge
cam_lens_h  = 6.5;    // board front -> front of lens housing
cam_lens_sq = 11;     // clearance for the square lens housing
fov_half    = 38.5;   // Camera Module 3 standard: 75 deg diagonal

// ---------- Front standard (lens board) -------------------------------
T      = 10;     // standard thickness
std_w  = 70;
std_z  = [14, 126];
z_t    = 46;     // taking lens (camera) centre height
z_v    = 98;     // viewing lens centre height
tl_len = 13;     // taking barrel length in front of the standard
cx     = W / 2;

$fn = 64;

// ---------- Derived -----------------------------------------------------
lens_front_y = -(1.2 + cam_lens_h);           // camera lens front (y)
bore_y1      = -(T + tl_len);                  // barrel mouth
function bore_r(L) = 4 + L * tan(fov_half);    // L = distance from lens
mouth_r      = bore_r(lens_front_y - bore_y1);
std_screws   = [[cx - 29, 30], [cx + 29, 30], [cx - 29, 112], [cx + 29, 112]];
tally_xz     = [cx - 27, 22];
side_btn     = [D * 0.42, H * 0.64];          // y,z of RECORD (left) and MODE (right)
hood         = [80, 66, 24];                   // w, d, h
hood_y0      = 7;
lights_x     = [cx - 17, cx, cx + 17];         // green, yellow, red
lights_z     = H + 12;
door_x       = [corner, W - corner];
door_z       = [3, H - 3];
boss_off     = wall + 7;                       // screw centre from the outer edges
door_screws  = [[boss_off, boss_off], [W - boss_off, boss_off],
                [boss_off, H - boss_off], [W - boss_off, H - boss_off]];

echo(str("Body ", W, " x ", D, " x ", H, " mm;  taking-lens bore mouth dia ", 2 * mouth_r));

// ---------- Helpers ---------------------------------------------------
module rrect(x, y, r) { translate([r, r]) offset(r) square([x - 2*r, y - 2*r]); }
// 2D shape on the XZ plane at y = 0, extruded towards -y by t
module on_front(t) { rotate([90, 0, 0]) linear_extrude(t) children(); }
// ...and towards +y
module on_back(t)  { rotate([-90, 0, 0]) mirror([0, 1, 0]) linear_extrude(t) children(); }
module ycyl(r, y0, y1, fn = 64) {   // cylinder along y between y0 and y1
    translate([0, min(y0, y1), 0]) rotate([-90, 0, 0]) cylinder(r = r, h = abs(y1 - y0), $fn = fn);
}
module knurl_ring(r, h, n = 48, depth = 0.8) {
    difference() {
        cylinder(r = r, h = h);
        for (a = [0:360/n:359]) rotate([0, 0, a]) translate([r, 0, -1])
            rotate([0, 0, 45]) cube([depth * 1.4, depth * 1.4, h + 2], center = true);
    }
}
// text bent around a circle, centred at the top
module ring_text(s, r, size, font = "DejaVu Sans:style=Bold", spacing = 1.0) {
    n = len(s);
    step = size * 0.78 * spacing / r * 180 / PI;
    for (i = [0:n-1]) rotate([0, 0, 90 + (n - 1) * step / 2 - i * step])
        translate([r, 0]) rotate([0, 0, -90]) text(s[i], size = size, font = font, halign = "center");
}

// ---------- BODY --------------------------------------------------------
module body_outer() {
    hull() {
        translate([0, 0, 1]) linear_extrude(H - 2) rrect_xy(W, D, corner);
        translate([1, 1, 0]) linear_extrude(H) rrect_xy(W - 2, D - 2, corner - 1);
    }
}
module rrect_xy(x, y, r) { rrect(x, y, r); }

module body() {
    difference() {
        union() {
            difference() {
                body_outer();
                translate([wall, wall, wall]) linear_extrude(H - 2*wall) rrect(W - 2*wall, D - 2*wall, max(0.5, corner - wall));
                // back opening (the door laps over the rim)
                translate([15, D - wall - 1, 15]) cube([W - 30, wall + 2, H - 30]);
            }
            // door screw bosses in the back corners, full depth so they print
            // without support when the body prints front-down
            for (s = door_screws) translate([s.x, wall, s.y]) rotate([-90, 0, 0])
                hull() {
                    cylinder(r = 6.5, h = D - wall);
                    translate([(s.x < W/2 ? -1 : 1) * 6.5, -(s.y < H/2 ? -1 : 1) * 6.5, 0])
                        cylinder(r = 1.5, h = D - wall);
                }
            tripod_boss();
            trims();
        }
        // camera board + ribbon opening behind the taking lens
        translate([cx - 16, -1, z_t - 22]) cube([32, wall + 2, 36]);
        // tally LED clearance (LED + bent leads)
        translate([tally_xz.x, -1, tally_xz.y]) rotate([-90, 0, 0]) cylinder(d = 9, h = wall + 2);
        // standard screws (from inside)
        for (s = std_screws) translate([s.x, -1, s.y]) rotate([-90, 0, 0]) cylinder(d = screw_clear, h = wall + 2);
        // RECORD (left side, under the focus knob) and MODE (right, under the crank)
        translate([-1, side_btn.x, side_btn.y]) rotate([0, 90, 0]) cylinder(d = btn_d, h = wall + 2);
        translate([W - wall - 1, side_btn.x, side_btn.y]) rotate([0, 90, 0]) cylinder(d = btn_d, h = wall + 2);
        // LED wires up into the hood
        translate([cx, hood_y0 + 14, H - wall - 1]) cylinder(d = 10, h = wall + 2);
        // door screw pilots
        for (s = door_screws) translate([s.x, D - 15, s.y]) rotate([-90, 0, 0]) cylinder(d = screw_pilot, h = 16);
        // tripod 1/4"-20 bolt + nut trap
        translate([cx, D/2, -1]) cylinder(d = 6.8, h = wall + 9);
        translate([cx, D/2, wall + 8 - 5.8]) cylinder(d = 11.4 / cos(30), h = 6, $fn = 6);
    }
}
module tripod_boss() {
    // front side chamfered 45 deg for front-down printing
    hull() {
        translate([cx, D/2, wall - 0.01]) cylinder(r = 10, h = 8);
        translate([cx - 10, D/2 - 18, wall - 0.01]) cube([20, 0.01, 0.01]);
    }
}
module trims() {
    // raised "chrome" bands around the sides - paint them silver
    for (sx = [-0.6, W - 0.2], ty = [corner + 2.5, D - corner - 4.5])
        translate([sx, ty, 3]) cube([0.8, 2, H - 6]);
}

// ---------- FRONT STANDARD (lens board) ----------------------------------
module standard() {
    lip = 1.5;
    difference() {
        union() {
            // board with chamfered front edge
            hull() {
                on_front(T - lip) translate([cx - std_w/2, std_z[0]]) rrect(std_w, std_z[1] - std_z[0], 6);
                on_front(T) translate([cx - std_w/2 + lip, std_z[0] + lip]) rrect(std_w - 2*lip, std_z[1] - std_z[0] - 2*lip, 6 - lip);
            }
            // taking lens: shutter ring + barrel + bezel
            translate([cx, 0, z_t]) {
                ycyl(25, -T + 0.01, -T - 4);
                translate([0, -T, 0]) rotate([90, 0, 0]) knurl_ring(25.6, 2.5, 72, 0.6);
                ycyl(18.5, -T - 4, -T - tl_len + 1.5);
                ycyl(19.5, -T - tl_len + 1.5, -T - tl_len);
            }
            // viewing lens: bezel ring + barrel
            translate([cx, 0, z_v]) {
                ycyl(20, -T + 0.01, -T - 3);
                ycyl(17, -T - 3, -T - 9);
                ycyl(18, -T - 9, -T - 10);
            }
            // aperture / speed wheels between the lenses
            for (sx = [-26, 26]) translate([cx + sx, -T, (z_t + z_v)/2 + 2.5]) rotate([90, 0, 0]) {
                knurl_ring(6.5, 5, 24, 0.7);
                cylinder(r = 3, h = 6);
            }
            // nameplate above the viewing lens
            translate([0, -T, 0]) on_front(0.8) translate([cx - 26, z_v + 20.6]) rrect(52, 7, 1.5);
            translate([0, -T - 0.8, 0]) on_front(0.6) translate([cx, z_v + 21.8])
                text("SPEECHCAM", size = 4.6, font = "DejaVu Serif:style=Bold", halign = "center");
            // tally "flash socket" bezel
            translate([tally_xz.x, -T + 0.01, tally_xz.y]) rotate([90, 0, 0]) cylinder(r = 4.6, h = 2);
        }
        // camera bore: conical, apex at the camera lens
        translate([cx, lens_front_y, z_t]) rotate([90, 0, 0])
            cylinder(r1 = bore_r(0), r2 = bore_r(lens_front_y - bore_y1 + 1), h = lens_front_y - bore_y1 + 1, $fn = 96);
        // lens housing clearance
        translate([cx - cam_lens_sq/2, lens_front_y - 0.5, z_t - cam_lens_sq/2]) cube([cam_lens_sq, -lens_front_y + 1, cam_lens_sq]);
        // board recess and component clearance, from the back
        translate([cx - cam_w/2 - 0.3, -1.2, z_t + cam_lens_top - cam_h - 0.3]) cube([cam_w + 0.6, 2, cam_h + 0.6]);
        translate([cx - 11, -4.2, z_t - 9]) cube([22, 5, 18]);
        // ribbon cable exits downward
        translate([cx - 9, -2.2, z_t + cam_lens_top - cam_h - 6]) cube([18, 3, 8]);
        // M2 board screws
        for (sx = [-cam_hole_dx/2, cam_hole_dx/2], hz = cam_hole_top)
            translate([cx + sx, 1, z_t + cam_lens_top - hz]) rotate([90, 0, 0]) cylinder(d = 1.8, h = 8, $fn = 16);
        // shutter-speed scale engraved on the shutter ring
        translate([cx, -T - 4 + 0.5, z_t]) rotate([90, 0, 0]) linear_extrude(1)
            ring_text("B 1 2 4 8 15 30 60 125 250 500", 21.6, 2.3, spacing = 0.95);
        // viewing lens: pocket for a 28 mm glass cabochon (or leave as is)
        translate([cx, 0, z_v]) ycyl(14.2, -T - 10 - 1, -T - 10 + 3.5);
        // lens name engraved on the viewing bezel
        translate([cx, -T - 3 + 0.5, z_v]) rotate([90, 0, 0]) linear_extrude(1)
            ring_text("SPEECH-ANASTIGMAT 1:2.8  f=80mm", 18.1, 1.6, spacing = 1.12);
        // tally LED
        translate([tally_xz.x, 1, tally_xz.y]) rotate([90, 0, 0]) cylinder(d = led_d, h = T + 4);
        // mounting screw pilots from the back
        for (s = std_screws) translate([s.x, 1, s.y]) rotate([90, 0, 0]) cylinder(d = screw_pilot, h = 8);
    }
    // fake glass: dark dome sitting in the viewing pocket
    translate([cx, -T - 10 + 3.5, z_v]) intersection() {
        ycyl(13.6, 0.4, -2.5);   // sinks 0.4 into the pocket floor so it fuses cleanly
        translate([0, 30, 0]) sphere(r = 32.4, $fn = 96);
    }
}

// ---------- WAIST-LEVEL FINDER HOOD --------------------------------------
module hood() {
    hw = hood.x; hd = hood.y; hh = hood.z;
    x0 = cx - hw/2;
    translate([x0, hood_y0, H]) difference() {
        union() {
            difference() {
                cube([hw, hd, hh]);
                translate([2, 2, -1]) cube([hw - 4, hd - 4, hh - 1]);
            }
            // lid seam
            translate([-0.6, -0.6, hh - 3]) cube([hw + 1.2, hd + 1.2, 1.2]);
            // jewel bezels for the timing lights
            for (lx = lights_x) translate([lx - x0, 0.01, lights_z - H]) rotate([90, 0, 0]) cylinder(r = 4.6, h = 1.6);
        }
        for (lx = lights_x) translate([lx - x0, 3, lights_z - H]) rotate([90, 0, 0]) cylinder(d = led_d, h = 6);
        // engraved fold lines on the sides (the hood "folds" like the real one)
        for (sx = [-0.5, hw - 0.5]) translate([sx, 0, 0]) {
            hull() { translate([0, 4, 3]) cube([1, 1, 0.8]); translate([0, hd/2, hh - 6]) cube([1, 1, 0.8]); }
            hull() { translate([0, hd - 5, 3]) cube([1, 1, 0.8]); translate([0, hd/2, hh - 6]) cube([1, 1, 0.8]); }
        }
        // magnifier window outline on the lid
        translate([hw/2, hd/2, hh - 0.6]) linear_extrude(1) difference() {
            square([hw - 16, hd - 16], center = true);
            square([hw - 18.4, hd - 18.4], center = true);
        }
        translate([hw/2, hd/2, hh - 0.6]) cylinder(r = 9, h = 1);
    }
}

// ---------- BACK DOOR (Pi Zero, amp and speaker mount on the inside) ----
pi_xz  = [21.5, 33.5];            // first Pi Zero hole (Pi stands upright)
spk    = [68, 104];                // speaker centre
module door() {
    dw = door_x[1] - door_x[0]; dh = door_z[1] - door_z[0];
    difference() {
        union() {
            translate([0, D, 0]) on_back(3) translate([door_x[0], door_z[0]]) rrect(dw, dh, 3);
            // raised trim frame on the outside
            translate([0, D + 3, 0]) on_back(0.8) translate([door_x[0], door_z[0]]) difference() {
                rrect(dw, dh, 3); translate([3, 3]) rrect(dw - 6, dh - 6, 1.5);
            }
            // Pi Zero standoffs (23 x 58 mm M2.5 pattern), inside
            for (dx = [0, 23], dz = [0, 58]) translate([pi_xz.x + dx, D, pi_xz.y + dz]) ycyl(2.8, 0.01, -5, 24);
            // PAM8302 cradle
            translate([52, D - 4, 26]) difference() { cube([24, 4.01, 19]); translate([1.5, -1, 1.5]) cube([21, 3, 16]); }
            // speaker ring
            translate([spk.x, D, spk.y]) difference() { ycyl(22, 0.01, -3); ycyl(20.6, 1, -4); }
        }
        for (s = door_screws) translate([s.x, D - 1, s.y]) ycyl(screw_clear / 2, 0, 6, 20);
        for (dx = [0, 23], dz = [0, 58]) translate([pi_xz.x + dx, D + 1, pi_xz.y + dz]) ycyl(1.15, 0, -8, 16);
        // speaker grille
        translate([spk.x, D - 1, spk.y]) for (ring = [0:3]) for (a = [0:360/max(1, 6*ring):359])
            rotate([0, a, 0]) translate([ring * 4.4, 0, 0]) ycyl(1.4, 0, 6, 16);
        // POWER button and USB-C inlet
        translate([66, D - 1, 62]) ycyl(btn_d / 2, 0, 6);
        translate([66, D - 1, 22]) rotate([-90, 0, 0]) linear_extrude(6) offset(1.2) square([7.4, 1.6], center = true);
        // engraved labels
        translate([66, D + 2.4, 75]) rotate([90, 0, 180]) linear_extrude(1)
            text("POWER", size = 4, font = "DejaVu Serif:style=Bold", halign = "center");
        translate([66, D + 2.4, 30]) rotate([90, 0, 180]) linear_extrude(1)
            text("5V IN", size = 4, font = "DejaVu Serif:style=Bold", halign = "center");
    }
}

// ---------- FOCUS KNOB (rings the RECORD button) -------------------------
module knob() {
    difference() {
        union() {
            knurl_ring(17, 7, 60, 0.9);
            translate([0, 0, 7]) cylinder(r1 = 16.5, r2 = 14, h = 2);
            cylinder(r = 18.5, h = 1.6);      // base flange
        }
        translate([0, 0, -1]) cylinder(d = 20.6, h = 12);
    }
}

// ---------- ADVANCE CRANK (rings the MODE button) ------------------------
module crank() {
    difference() {
        union() {
            cylinder(r = 14, h = 4);
            knurl_ring(14.6, 2, 40, 0.6);
            hull() { cylinder(r = 6, h = 3.5); translate([30, 0, 0]) cylinder(r = 4, h = 3.5); }
            translate([30, 0, 0]) { cylinder(r = 2.6, h = 11); translate([0, 0, 11]) sphere(r = 4); }
        }
        translate([0, 0, -1]) cylinder(d = 20.6, h = 12);
    }
}

// ---------- Output -------------------------------------------------------
module assembly() {
    color([0.26, 0.25, 0.24]) body();
    color([0.32, 0.31, 0.30]) standard();
    color("Silver") hood();
    color([0.30, 0.29, 0.28]) door();
    color("Silver") translate([-0.5, side_btn.x, side_btn.y]) rotate([0, -90, 0]) knob();
    color("Silver") translate([W + 0.5, side_btn.x, side_btn.y]) rotate([0, 90, 0]) crank();
}

if (part == "assembly") assembly();
if (part == "body")     rotate([90, 0, 0]) body();                                   // front face down
if (part == "standard") rotate([-90, 0, 0]) standard();                              // back face down
if (part == "door")     translate([0, 0, D + 3.8]) rotate([-90, 0, 0]) door();      // outside face down
if (part == "hood")     translate([0, 0, H + hood.z]) rotate([180, 0, 0]) hood();   // lid down
if (part == "knob")     knob();
if (part == "crank")    crank();

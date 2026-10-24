// =====================================================================
//  SPEECHCAM - Club Speech Recorder enclosure
//  Styled after a 1920s hand-crank cine camera: wooden box, brass
//  faceplate, offset lens, twin film reels on top and a side crank.
//
//  Coordinates (assembled):  x = width, left->right as seen from the FRONT
//                            y = depth, 0 = front face, D = back face
//                            z = height, 0 = bottom
//
//  Render one part:   openscad -D 'part="body"' -o body.stl speechcam.scad
//  Parts: assembly, body, back, faceplate, lens, reel, reel_stand,
//         axle_cap, crank, tray, rails
// =====================================================================

part = "assembly";

// ---------- MEASURE THESE ON YOUR PHONE (mm) --------------------------
// Defaults are iPhone 6s Plus, no case. With a case on, measure the case.
phone_len     = 158.2;  // long side
phone_hgt     = 77.9;   // short side (phone lies landscape)
phone_thk     = 7.3;    // thickness
cam_from_end  = 10.0;   // phone short edge  -> centre of rear lens
cam_from_edge = 10.0;   // phone long edge   -> centre of rear lens

// ---------- Fit / layout ---------------------------------------------
wall       = 2.6;    // shell wall
clr        = 1.0;    // side clearance around phone
left_bay   = 26;     // room for the Lightning Digital AV adapter plug
right_bay  = 24;     // room between lens end of phone and right wall
pad_h      = 3;      // phone stands on pads (keeps volume keys free)
insert_gap = 6;      // lift room to tilt phone in past the lips
D          = 90;     // outer depth
fp_t       = 3;      // faceplate thickness
btn_d      = 16.2;   // panel-mount push button hole (16 mm buttons)
led_d      = 5.2;    // 5 mm LED (use 8.2 for chrome LED bezels)
screw_pilot= 2.5;    // M3 self-tapping pilot
screw_clear= 3.4;

// Lens optics: iPhone 6s Plus video FOV is ~60 deg horizontal, ~67 deg
// diagonal. Bore half-angle 36 deg + 3 mm alignment tolerance = no vignette.
bore_r0    = 6;      // bore radius at the phone lens (lens 3 + tolerance 3)
bore_ang   = 36;
barrel_len = 22;     // how far the lens sticks out of the faceplate

$fn = 64;

// ---------- Derived ---------------------------------------------------
W        = 2*wall + left_bay + 2*clr + phone_len + right_bay;
px0      = wall + left_bay + clr;            // phone left end (front view)
px1      = px0 + phone_len;                  // phone right end (lens end)
pz0      = wall + pad_h;                     // phone bottom edge
lens_x   = px1 - cam_from_end;
lens_z   = pz0 + phone_hgt - cam_from_edge;
comp_h   = pad_h + phone_hgt + insert_gap;   // phone compartment height
shelf_z  = wall + comp_h;                    // shelf underside
// Size the electronics bay so the lens ends up at mid-height
bay_h    = max(45, 2*lens_z - (shelf_z + 2*wall));
H        = shelf_z + wall + bay_h + wall;
bay_z0   = shelf_z + wall;                   // bay floor
lip_y    = wall + phone_thk + 1.2;           // retaining lip face

function bore_r(d) = bore_r0 + d * tan(bore_ang);  // d = dist. from phone lens
spigot_r = bore_r(wall + fp_t) + 1.8;

reel_r    = 34;
reel_y    = [8, D - 8];
stand_x0  = W/2 - 10;
axle_z    = H + 40;
shutter_xy= [lens_x, D - 24];
tally_xz  = [lens_x, H - 22];
lights_x  = 22;
lights_z  = [bay_z0 + 40, bay_z0 + 26, bay_z0 + 12]; // red, yellow, green (in the bay, above the shelf)
side_btn  = [D/2 + 4, bay_z0 + bay_h/2];          // y,z on right wall (crank / MODE)
speaker   = [D/2, bay_z0 + bay_h/2];              // y,z on left wall
usb_xz    = [W - 75, bay_z0 + bay_h/2];           // power inlet on back
pwr_xz    = [W - 40, bay_z0 + bay_h/2];           // power button on back

echo(str("Outer size W x D x H = ", W, " x ", D, " x ", H, " mm"));
echo(str("Lens centre x=", lens_x, " z=", lens_z, "  bay height=", bay_h));

// ---------- Helpers ---------------------------------------------------
module rrect(x, y, r) {          // 2D rounded rectangle at origin corner
    translate([r, r]) offset(r) square([x - 2*r, y - 2*r]);
}
module chamfer_box(s, c) {       // box with chamfered edges
    hull() {
        translate([c, 0, c]) cube([s.x - 2*c, s.y, s.z - 2*c]);
        translate([0, c, c]) cube([s.x, s.y - 2*c, s.z - 2*c]);
        translate([c, c, 0]) cube([s.x - 2*c, s.y - 2*c, s.z]);
    }
}
// shape on the XZ plane at y = 0, extruded towards -y by t
module on_front(t) { rotate([90, 0, 0]) linear_extrude(t) children(); }

// ---------- BODY -------------------------------------------------------
module body() {
    difference() {
        union() {
            difference() {
                chamfer_box([W, D, H], 2);
                translate([wall, wall, wall]) cube([W - 2*wall, D, H - 2*wall]);
            }
            // shelf between phone compartment and electronics bay
            difference() {
                translate([wall, wall - 0.01, shelf_z]) cube([W - 2*wall, D - wall, wall]);
                // cable pass-through above the AV adapter (HDMI plug fits through)
                translate([wall + 8.5, wall + 16, shelf_z - 1]) cube([22, D - wall - 34, wall + 2]);
            }
            // corner screw bosses for the back panel (full depth = no supports)
            for (bx = [wall, W - wall - 8], bz = [wall, shelf_z - 8, bay_z0, H - wall - 8])
                translate([bx, wall, bz]) cube([8, D - wall, 8]);
            phone_cradle();
            tripod_boss();
            side_trim();
        }
        // lens spigot hole
        translate([lens_x, wall + 1, lens_z]) rotate([90, 0, 0]) cylinder(r = spigot_r + 0.2, h = wall + 2);
        // indicator LEDs through front wall
        for (lz = lights_z) translate([lights_x, wall + 1, lz]) rotate([90, 0, 0]) cylinder(d = led_d, h = wall + 2);
        translate([tally_xz.x, wall + 1, tally_xz.y]) rotate([90, 0, 0]) cylinder(d = led_d, h = wall + 2);
        // shutter (RECORD) button on top
        translate([shutter_xy.x, shutter_xy.y, H - wall - 1]) cylinder(d = btn_d, h = wall + 2);
        // MODE button under the crank, right side
        translate([W - wall - 1, side_btn.x, side_btn.y]) rotate([0, 90, 0]) cylinder(d = btn_d, h = wall + 2);
        // speaker grille, left side
        translate([-1, speaker.x, speaker.y]) rotate([0, 90, 0]) speaker_holes();
        // reel stand peg holes
        for (py = [22, D - 22]) translate([stand_x0 + 3, py, H - wall - 1]) cylinder(d = 4.4, h = wall + 2);
        // back panel screw pilots
        for (s = screw_pos()) translate([s.x, D - 16, s.y]) rotate([-90, 0, 0]) cylinder(d = screw_pilot, h = 17);
        // tripod bolt
        translate([W/2, D/2 + 10, -1]) cylinder(d = 6.8, h = wall + 9);
        // locating grooves for the glued-in phone retaining rails
        translate([px0 + 3.8, lip_y - 0.1, wall - 1]) cube([phone_len - 7.6, 3.2, 1.01]);
        translate([px0 + 3.8, lip_y - 0.1, shelf_z - 0.01]) cube([phone_len - 7.6, 3.2, 1.01]);
        translate([W/2, D/2 + 10, wall + 8 - 5.8]) cylinder(d = 11.4 / cos(30), h = 6, $fn = 6);
    }
}

function screw_pos() = [
    [wall + 4, wall + 4], [W - wall - 4, wall + 4],
    [wall + 4, shelf_z - 4], [W - wall - 4, shelf_z - 4],
    [wall + 4, bay_z0 + 4], [W - wall - 4, bay_z0 + 4],
    [wall + 4, H - wall - 4], [W - wall - 4, H - wall - 4]];

module speaker_holes() {
    cylinder(d = 3, h = wall + 2, $fn = 16);
    for (ring = [1:3]) for (a = [0:360/(6*ring):359])
        rotate([0, 0, a]) translate([ring * 4.6, 0, 0]) cylinder(d = 3, h = wall + 2, $fn = 16);
}

module phone_cradle() {
    // pads: keep clear of the volume / mute keys, which sit 15-65 mm
    // from the lens end on the bottom edge in this orientation
    translate([px0 + 8, wall - 0.01, wall - 0.01]) cube([80, lip_y - wall, pad_h]);
    translate([px1 - 13, wall - 0.01, wall - 0.01]) cube([10, lip_y - wall, pad_h]);
    // retaining lips are separate "rails" glued into grooves (a lip printed
    // in place would start mid-air when the body prints front-down)
    // end stop at the lens end of the phone
    translate([px1 + clr, wall - 0.01, wall - 0.01]) cube([2, lip_y - wall + 1, 22]);
    translate([px1 + clr, wall - 0.01, shelf_z - 16]) cube([2, lip_y - wall + 1, 16.01]);
}
module tripod_boss() {
    // 1/4"-20 nut trap; front side chamfered 45 deg for front-down printing
    hull() {
        translate([W/2, D/2 + 10, wall - 0.01]) cylinder(r = 10, h = 8);
        translate([W/2 - 10, D/2 + 10 - 10 - 8, wall - 0.01]) cube([20, 0.01, 0.01]);
    }
}
module side_trim() {
    // rivets along the side edges (brass-strap look)
    for (sx = [-0.01, W + 0.01], ry = [10:16:D - 6], rz = [6, H - 6])
        translate([sx, ry, rz]) sphere(r = 1.4, $fn = 16);
}
// wood-plank grooves on the sides and top
module plank_grooves() {
    for (gz = [H * 0.25, H * 0.5, H * 0.75]) {
        translate([-1, 4, gz]) cube([1.6, D - 8, 0.8]);
        translate([W - 0.6, 4, gz]) cube([1.6, D - 8, 0.8]);
    }
}
module body_final() { difference() { body(); plank_grooves(); } }

// ---------- FACEPLATE (print in brass / gold PLA) ----------------------
module faceplate() {
    in = 5;
    difference() {
        union() {
            on_front(fp_t) translate([in, in]) rrect(W - 2*in, H - 2*in, 6);
            // raised border
            translate([0, -fp_t, 0]) on_front(1.2) difference() {
                translate([in, in]) rrect(W - 2*in, H - 2*in, 6);
                translate([in + 3.5, in + 3.5]) rrect(W - 2*in - 7, H - 2*in - 7, 3);
            }
            // nameplate
            translate([0, -fp_t, 0]) on_front(1.2) translate([36, H - 46]) rrect(104, 28, 3);
            translate([0, -fp_t - 1.2, 0]) on_front(1) translate([88, H - 33]) {
                text("SPEECHCAM", size = 11, font = "DejaVu Serif:style=Bold", halign = "center", valign = "center");
            }
            translate([0, -fp_t - 1.2, 0]) on_front(0.8) translate([88, H - 42]) {
                text("CLUB SPEECH RECORDER  ·  No. 1", size = 3.6, font = "DejaVu Serif", halign = "center", valign = "center");
            }
            // jewel bezels for the timing lights + tally
            for (lz = lights_z) translate([0, -fp_t, 0]) on_front(2) translate([lights_x, lz]) circle(r = 6);
            translate([0, -fp_t, 0]) on_front(2) translate(tally_xz) circle(r = 6);
            // art-deco sunburst rings around the lens
            translate([0, -fp_t, 0]) on_front(0.8) translate([lens_x, lens_z]) difference() {
                circle(r = 38); circle(r = 35.5);
            }
            // speed lines between the lights and the lens
            for (i = [0:2]) translate([0, -fp_t, 0]) on_front(0.8)
                translate([36, lens_z - 30 + i * 7]) square([lens_x - 36 - 42, 2.2]);
            // labels
            translate([0, -fp_t, 0]) on_front(0.8) translate([lights_x, lights_z[2] - 12])
                text("TIME", size = 3.4, font = "DejaVu Serif:style=Bold", halign = "center");
            translate([0, -fp_t, 0]) on_front(0.8) translate([tally_xz.x + 9, tally_xz.y - 1.5])
                text("REC", size = 3.4, font = "DejaVu Serif:style=Bold");
        }
        translate([lens_x, 1, lens_z]) rotate([90, 0, 0]) cylinder(r = spigot_r + 0.2, h = 20);
        for (lz = lights_z) translate([lights_x, 1, lz]) rotate([90, 0, 0]) cylinder(d = led_d, h = 20);
        translate([tally_xz.x, 1, tally_xz.y]) rotate([90, 0, 0]) cylinder(d = led_d, h = 20);
    }
}

// ---------- LENS BARREL (print front-down, black PLA) ------------------
// Local coords: z = 0 at faceplate surface, +z = forward.
module lens_local() {
    d0 = wall + fp_t;                     // phone lens -> faceplate surface
    difference() {
        union() {
            rotate_extrude($fn = 96) polygon([
                [spigot_r, -(d0 - 0.6)], [spigot_r, 0],
                [29, 0], [29, 2.5], [23.5, 8],             // flange, 45 deg underside
                [23.5, 9], [25.5, 9], [25.5, 15],          // focus ring
                [23.5, 17], [23.5, 18], [28, 18],          // bezel
                [29, 19], [29, barrel_len], [bore_r(d0 + barrel_len) + 0.3, barrel_len],
                [bore_r(-0.6 + 0.01), -(d0 - 0.6)]]);
            // knurling on the focus ring
            for (a = [0:7.5:359]) rotate([0, 0, a]) translate([25.2, -0.6, 9.5]) cube([1.3, 1.2, 5]);
        }
        // conical bore, apex side at the phone lens
        translate([0, 0, -d0]) cylinder(r1 = bore_r(0), r2 = bore_r(d0 + barrel_len + 0.02), h = d0 + barrel_len + 0.02, $fn = 96);
        // engraved index ring on the bezel face
        translate([0, 0, barrel_len - 0.6]) difference() { cylinder(r = 28, h = 1); cylinder(r = 27.3, h = 1); }
    }
}
module lens_assembled() { translate([lens_x, -fp_t, lens_z]) rotate([90, 0, 0]) lens_local(); }

// ---------- FILM REELS --------------------------------------------------
reel_t = 5;
module reel() {
    difference() {
        union() {
            cylinder(r = reel_r, h = 2.4);
            difference() { cylinder(r = reel_r, h = reel_t); translate([0, 0, -1]) cylinder(r = reel_r - 2.2, h = reel_t + 2); }
            cylinder(r = 8, h = reel_t + 2);
        }
        translate([0, 0, -1]) cylinder(d = 6.5, h = reel_t + 4);
        for (a = [0, 120, 240]) rotate([0, 0, a]) translate([19, 0, -1]) cylinder(r = 10, h = reel_t + 2);
        for (a = [60, 180, 300]) rotate([0, 0, a]) translate([25, 0, -1]) cylinder(r = 3.2, h = reel_t + 2);
        // square drive hole like a real spool
        translate([0, 0, -1]) linear_extrude(reel_t + 4) offset(0.6) square(4.5, center = true);
    }
}
module reel_stand() {
    // fin in the YZ plane, axles point +x. Prints lying on its -x face.
    translate([stand_x0, 0, 0]) {
        translate([0, 14, H]) cube([20, D - 28, 3]);
        hull() {
            translate([0, 16, H]) cube([6, D - 32, 3]);
            for (yy = reel_y) translate([0, yy, axle_z]) rotate([0, 90, 0]) cylinder(r = 9, h = 6);
        }
        for (yy = reel_y) translate([6, yy, axle_z]) rotate([0, 90, 0]) {
            cylinder(r = 4.5, h = 1);                       // spacer
            cylinder(d = 6, h = 1 + reel_t + 2 + 0.5 + 2);  // axle
        }
        for (py = [22, D - 22]) translate([3, py, H - wall + 0.01]) cylinder(d = 4, h = wall);
    }
}
module axle_cap() {
    difference() { cylinder(r = 6, h = 3.5); translate([0, 0, 1.5]) cylinder(d = 6.15, h = 3); }
}

// ---------- CRANK (decorative, rings the MODE button) -------------------
module crank() {
    difference() {
        union() {
            cylinder(r = 15, h = 3);
            hull() { cylinder(r = 7, h = 4); translate([42, 0, 0]) cylinder(r = 5, h = 4); }
            translate([42, 0, 0]) { cylinder(r = 3.5, h = 22); translate([0, 0, 22]) sphere(r = 5.5); }
        }
        translate([0, 0, -1]) cylinder(d = 20.4, h = 10);   // fits around a 16 mm button bezel
    }
}

// ---------- BACK PANEL ---------------------------------------------------
module back_panel() {
    scr_x = px0 + phone_len/2;              // screen centre (mirrored view from back)
    scr_z = pz0 + phone_hgt/2;
    win = [126, 71];
    translate([0, D, 0]) difference() {
        union() {
            rotate([-90, 0, 0]) mirror([0, 1, 0]) linear_extrude(3) rrect(W, H, 2);
            // ground-glass frame molding
            translate([0, 3, 0]) rotate([-90, 0, 0]) mirror([0, 1, 0]) linear_extrude(2)
                translate([scr_x - win.x/2 - 6, scr_z - win.y/2 - 6]) difference() {
                    rrect(win.x + 12, win.y + 12, 6);
                    translate([6, 6]) rrect(win.x, win.y, 3);
                }
            // bezels for button and power inlet
            for (p = [pwr_xz, usb_xz]) translate([p.x, 3, p.y]) rotate([-90, 0, 0]) cylinder(r = 13, h = 1.2);
        }
        translate([scr_x - win.x/2, -1, scr_z - win.y/2]) rotate([-90, 0, 0]) mirror([0, 1, 0])
            linear_extrude(10) rrect(win.x, win.y, 3);
        for (s = screw_pos()) translate([s.x, -1, s.y]) rotate([-90, 0, 0]) cylinder(d = screw_clear, h = 10);
        translate([pwr_xz.x, -1, pwr_xz.y]) rotate([-90, 0, 0]) cylinder(d = btn_d, h = 10);
        // USB-C breakout inlet slot
        translate([usb_xz.x, -1, usb_xz.y]) rotate([-90, 0, 0]) linear_extrude(10) offset(1.2) square([7.4, 1.6], center = true);
        // vents over the electronics bay
        for (i = [0:5]) translate([30 + i * 12, -1, bay_z0 + 10]) cube([3, 10, bay_h - 20]);
        // engraved labels
        translate([pwr_xz.x, 2.4, pwr_xz.y + 14]) rotate([90, 0, 180]) linear_extrude(1)
            text("POWER", size = 4, font = "DejaVu Serif:style=Bold", halign = "center");
        translate([usb_xz.x, 2.4, usb_xz.y + 14]) rotate([90, 0, 180]) linear_extrude(1)
            text("5V IN", size = 4, font = "DejaVu Serif:style=Bold", halign = "center");
    }
}

// ---------- ELECTRONICS TRAY (sits on the shelf) -----------------------
module tray() {
    tw = 150; td = D - wall - 10;
    difference() {
        union() {
            linear_extrude(2) rrect(tw, td, 3);
            // Pi Zero standoffs (58 x 23 mm M2.5 pattern)
            for (x = [10, 68], y = [10, 33]) translate([x, y, 0]) cylinder(d = 5.5, h = 6);
            // PAM8302 cradle
            translate([90, 8, 0]) difference() { cube([24, 19, 4]); translate([1.5, 1.5, 2]) cube([21, 16, 3]); }
        }
        for (x = [10, 68], y = [10, 33]) translate([x, y, -1]) cylinder(d = 2.3, h = 8);
        // zip-tie slots for the capture dongle and USB hub
        for (x = [20, 60, 100, 130], y = [48, 64]) translate([x, y, -1]) cube([3.5, 1.8, 4]);
    }
}

// ---------- PHONE RETAINING RAILS (glue into the floor/shelf grooves) ---
rail_bot_h = pad_h + 4;    // above the floor
rail_top_h = 9;            // below the shelf
module rail(h) { cube([phone_len - 8, 3, h + 1]); }
module rails_print() {     // both rails, lying flat
    rotate([90, 0, 0]) rail(rail_bot_h);
    translate([0, 14, 0]) rotate([90, 0, 0]) rail(rail_top_h);
}

// ---------- Output ------------------------------------------------------
module assembly() {
    color("SaddleBrown") body_final();
    color("Goldenrod") faceplate();
    color("DimGray") lens_assembled();
    color("DarkGoldenrod") back_panel();
    color("Goldenrod") reel_stand();
    for (i = [0:1]) color("DimGray") translate([stand_x0 + 7, reel_y[i], axle_z]) rotate([0, 90, 0]) reel();
    color("Goldenrod") translate([W + 0.5, side_btn.x, side_btn.y]) rotate([0, 90, 0]) crank();
    color("Goldenrod") translate([px0 + 4, lip_y, wall - 1]) rail(rail_bot_h);
    color("Goldenrod") translate([px0 + 4, lip_y, shelf_z - rail_top_h]) rail(rail_top_h);
    // phone, for reference
    %translate([px0, wall, pz0]) cube([phone_len, phone_thk, phone_hgt]);
}

if (part == "assembly")   assembly();
if (part == "body")       rotate([90, 0, 0]) body_final();                       // print front face down
if (part == "back")       rotate([90, 0, 0]) translate([0, -D, 0]) back_panel();   // inside face down
if (part == "faceplate")  rotate([-90, 0, 0]) faceplate();                        // back face down
if (part == "lens")       translate([0, 0, barrel_len]) mirror([0, 0, 1]) lens_local(); // front down
if (part == "reel")       reel();
if (part == "reel_stand") rotate([0, -90, 0]) translate([-stand_x0, 0, 0]) reel_stand();
if (part == "axle_cap")   axle_cap();
if (part == "crank")      crank();
if (part == "tray")       tray();
if (part == "rails")      rails_print();

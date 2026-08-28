// ====================================================================
// GUARDIAN X-1 — TACTICAL HYBRID DRONE-ROVER
// Dual amber-ring eyes • folding struts • IN-LINE N20 AXLE DRIVE • FDM READY
// Master File Location: mechanical/guardian_x1.scad
// BOM: CF-PETG • PA6-CF • TPU 95A • 2807/7" • Pi • ToF • N20
// ====================================================================
$fn = 48;

/* [Render Mode & Kinematics] */
render_part   = "ALL_ASSEMBLED"; // ["ALL_ASSEMBLED", "PRINT_LAYOUT", "CHASSIS", "FASCIA", "STRUT", "TYRE", "HUB"]
deploy_wheels = true;
deploy_angle  = 0;               // 0 = Ground Mode, 90 = Flight Fold Mode
wheel_spin    = 0;               // [0:360] Animate wheels rolling on the X-axis
drawer_open   = 0;               // 0 = closed, 1 = extended aft
secret_drawer = 0;               // 0 = closed, 1 = deployed (95-deg)
servo_lock    = 1;               // 0 = unlocked, 1 = locked

/* [Geometry & Clearances] */
fit_tol     = 0.2; // Standard 0.4mm nozzle FDM print clearance
m3          = 3.3;
cw          = 150; 
cl          = 200; 
ch          = 40;
center_w    = 86;
rail_w      = (cw - center_w) / 2;
be          = cw / 2;

motor_y     = 90;  // Propeller station Y-offset (±90mm)
motor_reach = 62;  // Arm extension (mm)
strut_l     = 32;  // Strut vertical drop (mm)
tyre_d      = 66;  // Outer tyre diameter (mm)
tyre_w      = 24;  // Tyre width (mm)
wy_f        = 42;  // Front wheel station (+42mm)
wy_r        = -42; // Rear wheel station (-42mm)
pivot_z     = 14;  // Y-axis fold pivot Z-height
wheel_out   = 16;  // Strut extension offset (mm)

module m3h(h=16) cylinder(d=m3, h=h, center=true);
module box(s) cube(s, center=true);

module bom_pi()    { color([0.1,0.45,0.15]) translate([0,14,11]) box([86,58,14]); }
module bom_stack() { color([0.4,0.1,0.1]) translate([0,-14,15]) box([32,32,12]); }
module bom_batt()  { color([0.12,0.12,0.16]) translate([0,-48,10]) box([70,54,20]); }

module mag_disc_stack(n=2) {
    color([0.15,0.15,0.18])
    for (i=[0:n-1])
        translate([0,0, i*3-(n-1)*1.5]) cylinder(d=8, h=2.8, center=true);
}

module center_floor() {
    color([0.22,0.23,0.25])
    difference() {
        union() {
            translate([0,0,3.5]) box([center_w, cl, 7]);
            translate([0, -cl/2+4, ch/2]) box([cw-2, 8, ch-2]);
            translate([0, -48, 10])
                difference() {
                    box([76, 60, 22]);
                    translate([0,0,2]) box([66, 50, 20]);
                    translate([0, -24, -8]) box([34, 14, 12]);
                }
            translate([0, 10, 8])
                difference() {
                    box([center_w-8, 72, 14]);
                    translate([0,0,2]) box([center_w-14, 64, 12]);
                }
            translate([center_w/2-5, -8, 11]) box([11, 40, 16]);
        }
        translate([0, 10, 8]) box([center_w-14, 64, 10]);
        translate([center_w/2-3, -8, 11]) box([9, 32, 12]);
        translate([0, cl/2-6, 14]) box([center_w-26, 8, 20]);
        for (sx=[-1,1]) translate([sx*(center_w/2-3), 0, 7]) box([2, cl-18, 1.5]);
        for (x=[-16,0,16], y=[-54,-42]) translate([x,y,1]) box([6,5,8]);
        for (x=[-22,22], y=[-50,-18,18,50]) translate([x,y,0]) m3h(14);
        for (x=[-20,20]) translate([x, 44, 8]) box([8.6, 3.2, 8.6]);
    }
    if (render_part=="ALL_ASSEMBLED") { bom_pi(); bom_stack(); bom_batt(); }
}

module main_drawer() {
    ext = drawer_open * 58;
    color([0.18,0.19,0.20])
    translate([0, 10 - ext, 7]) {
        difference() {
            box([center_w-16, 62, 10]);
            translate([0,0,2]) box([center_w-22, 54, 9]);
            translate([0, 28, 0]) box([18, 8, 6]);
            for (x=[-20,20]) translate([x, 30, 0]) box([8.6, 3.2, 8.6]);
        }
        for (x=[-(center_w/2-14), center_w/2-14]) translate([x,0,-2]) box([3,58,2]);
        for (x=[-20,20]) translate([x,30,0]) rotate([90,0,0]) mag_disc_stack(2);
    }
    for (x=[-20,20]) translate([x,44,8]) rotate([90,0,0]) mag_disc_stack(2);
}

module drawer_servo_lock() {
    pin = servo_lock * 6;
    color([0.25,0.26,0.28])
    translate([0, 48, 14]) {
        box([12, 16, 10]);
        color([0.55,0.55,0.58]) translate([0, -6-pin, -2]) box([3,8,3]);
    }
    color([0.2,0.21,0.22])
    translate([0, 10-drawer_open*58+28, 10]) box([10,4,6]);
}

module secret_drawer() {
    color([0.22,0.23,0.24])
    translate([center_w/2-5, -8, 11]) {
        difference() {
            box([11, 40, 16]);
            translate([2,0,0]) box([9, 32, 12]);
            for (y=[-12,12]) translate([0,y,0]) rotate([0,90,0]) m3h(12);
            translate([4,16,0]) box([3,6.4,6.4]);
        }
        translate([0,0,9]) { box([9,10,5]); color([0.28,0.3,0.22]) translate([0,0,2]) box([7,7,3]); }
        translate([4,16,0]) rotate([0,90,0]) mag_disc_stack(1);
    }
    ang = secret_drawer * 95;
    color([0.17,0.18,0.19])
    translate([center_w/2+1, -8, 11])
    rotate([0,0,ang]) translate([4.5,0,0])
    difference() {
        union() {
            box([2.5, 36, 14]);
            for (y=[-12,12]) translate([-1,y,0]) rotate([0,90,0]) cylinder(d=5.5, h=3.5, center=true);
            translate([1,16,0]) box([2,6,6]);
        }
        for (y=[-12,12]) translate([-1,y,0]) rotate([0,90,0]) m3h(7);
    }
}

module front_fascia() {
    cy = cl/2;
    color([0.10,0.11,0.12])
    translate([0, cy-1, 13]) {
        difference() {
            hull() {
                box([center_w-4, 14, 34]);
                translate([0,5,-1]) box([center_w-14, 6, 26]);
                translate([0,3,-11]) box([center_w-20, 8, 12]);
            }
            translate([0,8,13]) box([28,16,3]);
            translate([-14,8,4]) rotate([90,0,0]) cylinder(d=16, h=16, center=true);
            translate([ 14,8,4]) rotate([90,0,0]) cylinder(d=16, h=16, center=true);
            translate([0,8,-7]) rotate([90,0,0]) cylinder(d=12, h=16, center=true);
            translate([0,-5,0]) box([center_w-16, 8, 26]);
        }
        color([0.0,0.72,0.88]) translate([0,9.5,13]) box([26,2,2.5]);
        color([0.02,0.02,0.03]) {
            translate([-14,9,4]) rotate([90,0,0]) cylinder(d=12, h=3, center=true);
            translate([ 14,9,4]) rotate([90,0,0]) cylinder(d=12, h=3, center=true);
        }
        color([1.0,0.55,0.05]) {
            for (x=[-14,14])
                translate([x,9.5,4]) rotate([90,0,0])
                    difference() { cylinder(d=16.5,h=2,center=true); cylinder(d=12.5,h=3,center=true); }
        }
        color([0.01,0.01,0.02]) translate([0,9,-7]) rotate([90,0,0]) cylinder(d=9.5,h=3,center=true);
        color([0.0,0.72,0.88]) translate([0,9.5,-2.2]) box([8,2,2]);
    }
}

module front_door_rails() {
    color([0.2,0.21,0.22])
    for (x=[-(center_w/2-6), center_w/2-6])
        translate([x, cl/2-3, 15]) box([2,2,18]);
}

module side_rail(left=true) {
    sm = left ? 1 : -1;
    color([0.24,0.25,0.27])
    difference() {
        union() {
            translate([0,0,ch/2])
                hull() {
                    box([rail_w, cl-8, ch]);
                    translate([sm*4,0,2]) box([rail_w-6, cl-30, ch-8]);
                }
            for (y=[-motor_y, motor_y])
                translate([sm*(rail_w/2+8), y, ch/2+8])
                    hull() {
                        box([20, 30, 24]);
                        translate([sm*6,0,2]) box([8, 20, 14]);
                    }
            for (y=[wy_f, wy_r]) {
                translate([sm*(rail_w/2+26), y, 12]) box([3, 58, 26]);
                translate([sm*(rail_w/2+12), y+28, 11]) box([24, 3, 22]);
                translate([sm*(rail_w/2+12), y-28, 11]) box([24, 3, 22]);
                translate([sm*(rail_w/2+1), y, pivot_z])
                    rotate([90,0,0]) cylinder(d=14, h=12, center=true);
            }
        }
        for (y=[wy_f, wy_r]) {
            translate([sm*(rail_w/2+14), y, 12]) box([42, 54, 30]);
            translate([sm*(rail_w/2+14), y, -1]) box([42, 50, 14]);
            translate([sm*(rail_w/2+5), y, pivot_z]) box([14, 46, 24]);
            translate([sm*(rail_w/2+1), y, pivot_z])
                rotate([90,0,0]) cylinder(d=10.2, h=14, center=true);
        }
        translate([sm*1.5, 0, ch/2+1]) box([rail_w-10, cl-34, ch-10]);
        for (y=[-60,-40,-20,20,40,60])
            translate([sm*(rail_w/2-1), y, ch/2+5]) box([rail_w-6, 2.2, 6]);
        for (y=[wy_f, wy_r])
            translate([sm*(rail_w/2+1), y, pivot_z]) rotate([90,0,0]) m3h(18);
        for (y=[-motor_y, motor_y], dy=[-7,7])
            translate([sm*(rail_w/2+3), y+dy, ch/2+8]) rotate([0,90,0]) m3h(16);
    }
}

module top_hull() {
    color([0.20,0.21,0.23])
    difference() {
        union() {
            translate([0,0,27])
                hull() {
                    box([cw-6, cl-8, 6]);
                    translate([0,0,7])  box([cw-20, cl-24, 5]);
                    translate([0,0,13]) box([cw-42, cl-44, 4]);
                    translate([0,0,16]) box([cw-64, cl-66, 3]);
                }
            translate([0, -cl/2+4, 18]) box([cw-4, 8, ch-6]);
            for (x=[-12,-6,0,6,12]) translate([x,-10,36]) box([2,22,3]);
            for (x=[-8,8]) translate([x,-18,42]) cylinder(d=5, h=4, center=true);
        }
        translate([0,0,25])
            hull() {
                box([cw-14, cl-16, 5]);
                translate([0,0,11]) box([cw-58, cl-60, 3]);
            }
        for (sx=[-1,1]) translate([sx*(center_w/2-2), 0, 16]) box([2, cl-22, 1.6]);
        for (y=[-14,-2,10,22]) translate([0,y,40]) box([30,2,4]);
        for (x=[-be+12, be-12], y=[-cl/2+12, 0, cl/2-18])
            translate([x,y,15]) m3h(44);
    }
    color([0.08,0.08,0.09])
    for (x=[-8,8]) {
        translate([x,-18,44]) cylinder(d=3, h=14);
        translate([x,-18,58]) cylinder(d1=3, d2=1.2, h=4);
    }
}

module wing_arm(left=true) {
    sm = left ? 1 : -1;
    color([0.19,0.20,0.22])
    difference() {
        union() {
            translate([-sm*8,0,0])
                hull() {
                    box([20, 30, 20]);
                    translate([-sm*6,0,0]) box([8, 22, 14]);
                }
            hull() {
                box([7, 22, 14]);
                translate([sm*(motor_reach-10),0,0]) box([12, 18, 12]);
            }
            translate([sm*motor_reach,0,0]) box([14, 20, 14]);
        }
        for (z=[-3,3])
            translate([sm*(motor_reach/2),0,z])
                rotate([0,90,0]) cylinder(d=5, h=motor_reach-14, center=true);
        translate([-sm*5, 8,0]) rotate([0,90,0]) m3h(20);
        translate([-sm*5,-8,0]) rotate([0,90,0]) m3h(20);
        translate([sm*motor_reach,0,0]) m3h(16);
    }
}

module motor_2807(left=true) {
    sm = left ? 1 : -1;
    color([0.14,0.15,0.16])
    difference() {
        union() {
            cylinder(d=32, h=16, center=true);
            translate([-sm*10,0,0])
                hull() {
                    box([14,16,12]);
                    translate([-4,0,0]) box([3,12,8]);
                }
        }
        cylinder(d=5, h=28, center=true);
        for (r=[0,90,180,270])
            rotate([0,0,r]) translate([9,0,0]) m3h(14);
    }
}

module n20_gearmotor() {
    color([0.72,0.73,0.75]) box([15, 12, 10]); 
    color([0.82,0.68,0.22]) translate([12,0,0]) box([9, 12, 10]); 
    color([0.78,0.78,0.80]) translate([20,0,0]) rotate([0,90,0]) cylinder(d=3, h=10, center=true); 
}

module wheel_strut(left=true) {
    sm = left ? 1 : -1;
    color([0.20,0.21,0.23])
    difference() {
        union() {
            rotate([90,0,0]) cylinder(d=12, h=10, center=true);
            hull() {
                rotate([90,0,0]) cylinder(d=10, h=8, center=true);
                translate([sm*wheel_out, 0, -strut_l])
                    rotate([0,90,0]) cylinder(d=18, h=10, center=true);
            }
            translate([sm*(wheel_out - 8), 0, -strut_l])
                rotate([0,90,0]) box([14, 15, 20]);
        }
        rotate([90,0,0]) cylinder(d=m3, h=16, center=true);
        translate([sm*(wheel_out - 8), 0, -strut_l])
            rotate([0,90,0]) box([10.2 + fit_tol, 12.2 + fit_tol, 24]);
        translate([sm*wheel_out, 0, -strut_l])
            rotate([0,90,0]) cylinder(d=3.5, h=40, center=true);
    }

    translate([sm*(wheel_out - 8), 0, -strut_l])
        rotate([0, sm > 0 ? 0 : 180, 0])
            rotate([0, 90, 0])
                n20_gearmotor();
}

module tyre() {
    color([0.08,0.09,0.09])
    difference() {
        union() {
            cylinder(d=tyre_d, h=tyre_w, center=true);
            for (i=[0:15])
                rotate([0,0,i*22.5])
                    for (z=[-6,0,6])
                        translate([tyre_d/2-1.2, 0, z]) box([2.6, 2, 3]);
        }
        cylinder(d=28 + fit_tol, h=tyre_w+4, center=true);
    }
}

module wheel_hub() {
    color([0.18,0.19,0.20])
    difference() {
        union() {
            cylinder(d=28, h=tyre_w-2, center=true);
            translate([0,0, tyre_w/2-1]) cylinder(d=32, h=2, center=true);
            translate([0,0,-tyre_w/2+1]) cylinder(d=32, h=2, center=true);
        }
        difference() {
            cylinder(d=3.0 + fit_tol, h=tyre_w+4, center=true);
            translate([1.2 + fit_tol/2, 0, 0]) box([1, 4, tyre_w+6]);
        }
        for (a=[0:60:300])
            rotate([0,0,a]) translate([8,0,0]) cylinder(d=5, h=tyre_w+4, center=true);
    }
}

module powered_wheel(left=true) {
    sm = left ? 1 : -1;
    color([0.65,0.65,0.68])
        rotate([0,90,0]) cylinder(d=3, h=28, center=true);
        
    translate([sm*12, 0, 0]) rotate([0,90,0]) {
        wheel_hub();
        tyre();
    }
}

module rest_block(left=true, y=0) {
    sm = left ? 1 : -1;
    color([0.28,0.29,0.30])
    translate([sm*(rail_w/2-5), y, 5]) {
        box([6, 8, 5]);
        translate([0,0,3]) rotate([90,0,0]) cylinder(d=5, h=7, center=true);
    }
}

module prop(cw=true) {
    p = cw ? 14 : -14;
    color([0.11,0.12,0.13])
    difference() {
        union() {
            cylinder(d=11, h=5, center=true);
            translate([0,0,2.5]) cylinder(d1=11, d2=3.5, h=3.5);
            for (a=[0,120,240]) {
                rotate([0,0,a]) rotate([p,0,0])
                hull() {
                    translate([6,0,0]) box([3,8,1.2]);
                    translate([28,-2,0]) box([20,11,0.85]);
                    translate([52,-5,0]) box([3,5,0.4]);
                }
            }
        }
        cylinder(d=5, h=16, center=true);
    }
}

// ====================================================================
// RENDER & PRINT LAYOUT CONTROLLER
// ====================================================================

if (render_part == "PRINT_LAYOUT") {
    translate([0, 0, 7.5]) rotate([-90,0,0]) wheel_strut(true);
    translate([45, 0, tyre_w/2]) tyre();
    translate([-45, 0, tyre_w/2-1]) wheel_hub();
    translate([0, 50, 6.5]) rotate([0,90,0]) front_fascia();
}

if (render_part == "CHASSIS")   center_floor();
if (render_part == "FASCIA")    front_fascia();
if (render_part == "STRUT")     wheel_strut(true);
if (render_part == "TYRE")      tyre();
if (render_part == "HUB")       wheel_hub();

if (render_part == "ALL_ASSEMBLED") {
    center_floor();
    main_drawer();
    drawer_servo_lock();
    translate([ center_w/2 + rail_w/2 - 0.1, 0, 0]) side_rail(true);
    translate([-center_w/2 - rail_w/2 + 0.1, 0, 0]) side_rail(false);
    top_hull();
    secret_drawer();
    front_door_rails();
    front_fascia();

    for (y=[-motor_y, motor_y]) {
        translate([be-3, y, ch/2+6]) {
            wing_arm(true);
            translate([motor_reach,0,0]) {
                rotate([0,0,180]) motor_2807(true);
                translate([0,0,10]) prop(y>0);
            }
        }
    }
    
    for (y=[wy_f, wy_r]) {
        ang = deploy_wheels ? -deploy_angle : -90;
        rest_block(true, y);
        translate([be-1, y, pivot_z]) rotate([0, ang, 0]) {
            wheel_strut(true);
            translate([wheel_out, 0, -strut_l]) 
                rotate([wheel_spin, 0, 0]) 
                    powered_wheel(true);
        }
    }
    
    for (y=[-motor_y, motor_y]) {
        translate([-be+3, y, ch/2+6]) {
            wing_arm(false);
            translate([-motor_reach,0,0]) {
                motor_2807(false);
                translate([0,0,10]) prop(y<0);
            }
        }
    }
    
    for (y=[wy_f, wy_r]) {
        ang = deploy_wheels ? deploy_angle : 90;
        rest_block(false, y);
        translate([-be+1, y, pivot_z]) rotate([0, ang, 0]) {
            wheel_strut(false);
            translate([-wheel_out, 0, -strut_l]) 
                rotate([-wheel_spin, 0, 0]) 
                    powered_wheel(false);
        }
    }
}
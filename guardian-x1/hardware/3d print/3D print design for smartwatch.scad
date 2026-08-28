// Guardian X-1: Ultra-Light Titanium-Polymer Hybrid Smart Glasses Frame
// Features integrated side temple arm hinges, waveguide optic housing bay, and micro-stepper motor mount.

$fn = 64;

// Frame Dimensions
frame_width = 142.0;
bridge_gap = 18.0;
lens_width = 52.0;
lens_height = 38.0;
frame_thickness = 5.5;

// Motorized Pop-Up Optic Bay Cavity
optic_bay_width = 28.0;
optic_bay_depth = 8.0;
stepper_mount_dia = 6.0;

module glasses_frame() {
    difference() {
        union() {
            // Main Eyewear Front Frame Chassis
            translate([0, 0, 0])
                cube([frame_width, frame_thickness, lens_height + 8], center = true);
            
            // Right Temple Motor & Gear Box Enclosure
            translate([(frame_width/2) - 8, 8, 4])
                cube([16, 16, 14], center = true);

            // Left Temple Arm Hinge Mount
            translate([-(frame_width/2) + 4, 4, 0])
                cube([8, 10, lens_height + 6], center = true);
        }

        # Left Eye Lens Cutout
        translate([-(bridge_gap/2 + lens_width/2), 0, 0])
            rotate([90, 0, 0])
                cylinder(h = frame_thickness + 2, r1 = lens_width/2, r2 = lens_height/2, center = true);

        // Right Eye Lens Cutout
        translate([(bridge_gap/2 + lens_width/2), 0, 0])
            rotate([90, 0, 0])
                cylinder(h = frame_thickness + 2, r1 = lens_width/2, r2 = lens_height/2, center = true);

        // Center Nose Bridge Relief Arc
        translate([0, 0, -(lens_height/2)])
            rotate([90, 0, 0])
                cylinder(h = frame_thickness + 2, d = bridge_gap, center = true);

        // Motorized Waveguide Pop-Up Slide Track (Right Brow Section)
        translate([(bridge_gap/2 + lens_width/2), 0, (lens_height/2) + 1])
            cube([optic_bay_width, frame_thickness + 4, optic_bay_depth], center = true);

        // Micro-Stepper Drive Shaft Bore
        translate([(frame_width/2) - 8, 8, 4])
            rotate([0, 90, 0])
                cylinder(h = 20, d = stepper_mount_dia, center = true);

        // Internal Ribbon Cable Wire Routing Channels
        translate([0, frame_thickness/4, (lens_height/2) + 2])
            cube([frame_width - 10, 2.0, 2.5], center = true);
    }
}

glasses_frame();
```markdown
# Guardian X-1 Mechanical Assembly & 3D Printing Guide

This guide covers material specifications, print profiles, and step-by-step mechanical integration for the Guardian X-1 chassis ($685 spec configuration).

---

## 3D Printing Profiles

All primary structural components are engineered for printing in **Carbon Fiber PETG (CF-PETG)** for high stiffness-to-weight ratio, with tires printed in **TPU 95A**.

| Part ID | Material | Walls | Infill % | Layer Height | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `chassis_floor` | CF-PETG | 4 | 35% | 0.20mm | Core structural deck with M3 heat-set inserts |
| `top_hull` | CF-PETG | 3 | 30% | 0.20mm | Sensor mount deck with antenna cutouts |
| `front_fascia` | CF-PETG | 4 | 35% | 0.20mm | Camera and ToF sensor bezel |
| `side_rail_left` | CF-PETG | 5 | 40% | 0.20mm | High-stress structural spine |
| `side_rail_right`| CF-PETG | 5 | 40% | 0.20mm | High-stress structural spine |
| `wing_arm` (x4) | CF-PETG | 5 | 45% | 0.16mm | Motor boom arm (requires per-layer cooling) |
| `wheel_strut` (x4)| CF-PETG | 4 | 40% | 0.20mm | N20 gearmotor enclosure |
| `wheel_hub` (x4) | CF-PETG | 4 | 35% | 0.20mm | Axle coupler with D-shaft press fit |
| `tyre` (x4) | TPU 95A | 3 | 25% | 0.20mm | Flexible treaded rover tire |
| `main_drawer` | CF-PETG | 4 | 35% | 0.20mm | Aft battery & power distribution tray |
| `secret_drawer` | CF-PETG | 3 | 30% | 0.20mm | Payload compartment |

---

## Assembly Sequence

### Step 1: Chassis Frame & Heat-Set Inserts
1. Heat brass M3 x 4mm x 5mm heat-set inserts into mounting locations on `chassis_floor`, `side_rail_left`, and `side_rail_right` using a soldering iron set to 240°C.
2. Bolt `side_rail_left` and `side_rail_right` to `chassis_floor` using M3 x 10mm button-head screws.

### Step 2: Ground Drivetrain Struts
1. Press-fit 4x N20 gearmotors into their respective `wheel_strut` housings.
2. Secure `wheel_hub` components to N20 D-shaft axles using M2.5 set screws.
3. Stretch TPU `tyre` prints over `wheel_hub` rims.
4. Mount the 4 strut assemblies to the lower pivot points of the chassis frame.

### Step 3: Aerial Booms & Flight Motors
1. Fasten 4x EMAX ECO II 2207 brushless motors to `wing_arm` booms using M3 x 6mm motor screws.
2. Attach `wing_arm` booms to the 4 corners of the chassis frame using M3 x 14mm bolts and nylon lock nuts.
3. Route motor phase wires internally through the arm wire guides into the main central deck.

### Step 4: Core Compute & Flight Controller Stack
1. Mount the **SpeedyBee F405 V4 Stack** to the lower center mounting pattern using M3 TPU vibration dampening bobbins.
2. Install the **Raspberry Pi 5** on the upper deck platform using standard 11mm brass standoffs.
3. Attach the M.2 HAT and NVMe SSD onto the Pi 5 PCIe ribbon interface, followed by the Hailo-8L NPU card.

### Step 5: Sensors, Optics & eSIM Module
1. Mount the **RPLIDAR A1M8** to the top center of `top_hull.stl`.
2. Secure the Arducam ToF and IMX219 RGB camera modules into `front_fascia.stl`.
3. Mount the LTE/eSIM modem module into the dedicated side slot, routing U.FL antenna cables to the chassis SMA bulkheads on `top_hull.stl`.
4. Slide `main_drawer` and `secret_drawer` into their respective tracks.

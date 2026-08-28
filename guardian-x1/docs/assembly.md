# Guardian X-1 Physical & Thermal Assembly Guide

## 1. Chassis Architecture & Electronics Stack

The structural assembly is designed around a three-tier vertical mounting stack to isolate high-frequency mechanical vibrations from the NPU and optical sensors:

```text
================================================================================
TIER 3: SENSOR DOME & ANTENNA ASSEMBLY
- Custom Top Hull (3D Printed top_hull.scad)
- ESP32 Dual Antenna Array (Wi-Fi 2.4GHz + LTE External Dipole)
- Low-latency Dual Stereo Camera Mount
================================================================================
TIER 2: COMPUTE STACK & STORAGE BAY
- Raspberry Pi 5 Core Processor
- Hailo-8L M.2 HAT + Heatsink Fan Unit
- Verbatim Vx500 240GB External SSD (Vibration Damping Silicon Cradle)
================================================================================
TIER 1: DRIVETRAIN & POWER MANAGEMENT
- Dual H-Bridge DC Motor Controllers
- 3S 2200mAh LiPo Battery Enclosure
- Custom Chassis Floor Plate (chassis_floor.scad)
================================================================================
FRONT FACIA: HUD DISPLAY ASSEMBLY
- 1.51" Transparent OLED (SSD1309 SPI) Mounted on front_fascia.scad
================================================================================

2. Thermal Management & Dissipation Plan
Hailo-8L NPU: Thermal pad (3.0 W/mK) directly coupled to aluminum heatsink chassis. Max operational threshold: 75°C. Active cooling fan kicks in when temperature exceeds 60°C.

Raspberry Pi 5 Broadcom SoC: Active Cooler fan integrated into compute stack. Forced airflow directed through chassis top vents.

Verbatim Vx500 SSD: Enclosed in heat-conductive rubber sleeve mounted flush against the lower chassis intake channel to prevent thermal throttling during high-bandwidth ROS 2 bag recordings (target write speed: > 350 MB/s).


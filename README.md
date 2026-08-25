# Tactical Drone-Rover (`drone_rover.scad`)

A parametric, 3D-printable OpenSCAD platform for a hybrid ground-and-air vehicle. Features deployable wheel struts with co-axial direct-drive motor housings, modular chassis rails, payload bays, and direct integration with a SIM-enabled Smartwatch for remote telemetry and control.

---

## Key Features

* **Dual Kinematics**: Y-axis folding wheel struts transition seamlessly between Ground Mode (0°) and Flight Fold Mode (90°).
* **Co-Axial Direct Drive**: Micro N20 gearmotors reside inside the strut body along the X-axis, driving 3mm D-shaft wheel hubs directly.
* **Quad-Rotor Flight**: Integrated mounting arms for 2807 brushless motors with 7" propellers.
* **Cellular Smartwatch Connectivity**: LTE/eSIM-enabled smartwatch interface for remote real-time telemetry polling and command execution over cellular data.
* **Onboard Electronics Bay**: Modular housing for Raspberry Pi, flight controller/ESC stack, 4S/6S battery pack, and front ToF optical sensors.
* **Payload Mechanisms**: Servo-locked primary drawer and hidden secondary storage tray.
* **FDM Print Optimized**: Preset single-part isolation modes and pre-oriented flat layouts at Z=0 for support-free printing.

---

## Smartwatch LTE Connectivity & Control

The onboard Raspberry Pi communicates with a SIM/eSIM-enabled cellular smartwatch over an encrypted MQTT/WebSockets broker over cellular networks.

### Architecture
```text
[ Smartwatch (eSIM/LTE) ] <---> [ Cloud MQTT / WebSockets Broker ] <---> [ 4G LTE HAT / Pi Onboard ]

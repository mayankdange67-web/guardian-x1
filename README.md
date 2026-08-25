# Guardian X-1: Hybrid Rover & Aerial Flight Platform

Guardian X-1 is a modular, dual-mode autonomous vehicle platform capable of differential ground rovers driving and multirotor aerial flight. Powered by a Raspberry Pi 5 companion computer working in tandem with a SpeedyBee F405 flight controller, the vehicle features dynamic payload deployment, active ToF/IMU hazard detection, and serial MSP control bridging.

---

## Key Features

* **Hybrid Kinematics:** Seamless transition between differential N20 ground drive and quadcopter flight states.
* **Low-Latency Hardware Control:** Direct Linux `gpiod` integration for motor driver H-bridges and payload locking servos.
* **Flight Controller Bridge:** MSP v2 protocol implementation over high-speed UART (`921600` baud) for raw RC pulse override and arming routines.
* **Safety & Sensor Fusion:** Real-time obstacle avoidance via VL53L1X ToF rangefinder and BNO085 9-DOF IMU telemetry.
* **Declarative Parameter Config:** Fully customizable hardware, control, and safety thresholds defined in centralized YAML files.

---

## Repository Structure

```text
guardian-x1/
├── README.md
├── .gitignore
├── config/
│   └── control_params.yaml    # Master system hardware & control parameters
└── firmware/
    └── control/
        ├── __init__.py
        ├── flight_bridge.py   # MSP v2 UART protocol interface to SpeedyBee FC
        ├── rover_controller.py# Differential drive control via gpiod
        └── state_machine.py   # System state engine & failsafe manager

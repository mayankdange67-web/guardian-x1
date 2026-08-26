# Guardian X-1 System Architecture (v1.2.0)

The Guardian X-1 features a distributed, edge-computed ROS 2 system architecture designed for dual-mode aerial/ground operations, real-time vision inference, and wide-area cellular telemetry failover.

---

## System Topology Diagram

```text
┌────────────────────────────────────────────────────────┐
│                   Wearer / Operator                    │
│   [Smartwatch (eSIM/BLE)]  ◄──►  [Mobile / Web UI]     │
└───────────────────────────┬────────────────────────────┘
                            │ Cellular LTE / MQTT / WebSocket
                            ▼
┌────────────────────────────────────────────────────────┐
│                   Guardian X-1 Core                    │
│                                                        │
│  ┌───────────────────────┐   ┌──────────────────────┐  │
│  │   Raspberry Pi 5 (8GB)│   │   Hailo-8L NPU (13T) │  │
│  │   - ROS 2 Humble      │   │   - YOLOv8 / Face ID │  │
│  │   - State Machine     │   │   - Local Inference  │  │
│  └──────────┬────────────┘   └──────────┬───────────┘  │
│             │                           │              │
│             ├───────────┬───────────────┴───┐          │
│             ▼           ▼                   ▼          │
│       [RPLIDAR]    [Arducam ToF]    [Cellular / eSIM]  │
│       (Mapping)    (Depth Sensing)  (LTE Telemetry)    │
│             │           │                   │          │
│             └───────────┴───────────────┬───┘          │
│                                         ▼              │
│                                 [Flight Stack]         │
│                                 (SpeedyBee F405)       │
└─────────────────────────────────────────┬──────────────┘
                                          ▼
                               [Propulsion & Drivetrain]
                               (EMAX Motors & N20 Wheels)

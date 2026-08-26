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


/hailo_yolo_node ───────► /guardian/vision/detections (DetectionArray)
                                     │
/rplidar_node ──────────► /scan (LaserScan) ──┐
                                             ▼
/arducam_tof_node ──────► /depth/points ────► /state_machine
                                             │
/cellular_manager ──────► /guardian/cellular ┘
                                             │
                                             ├─► /flight_bridge ──► MAVLink (/dev/ttyAMA0)
                                             └─► /rover_controller ─► GPIO / PWM (TB6612FNG)"








                                             
/state_machine: Central arbitration node executing high-level mode switches (GROUND_ROVER, AERIAL_FLIGHT, EMERGENCY_RTL, FAILSAFE_LAND).

/flight_bridge: MAVLink serial translator communicating with the SpeedyBee F405 V4 flight controller over UART6 (/dev/ttyAMA0 @ 921600 baud).

/cellular_manager: Connection supervisor checking network interfaces (wwan0), monitoring signal strength, and bridging local ROS 2 topics to remote MQTT brokers (mqtt.guardian-ecosystem.io:8883).

/voice_ai_node: Local voice processing pipeline wrapping Speech-to-Text (base.en), Ollama LLM (llama3.2:3b), and Text-to-Speech synthesis.

/watch_node: Wearable interaction node processing biometric streams and emergency gesture overrides over BLE or eSIM.

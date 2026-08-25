# Guardian X-1 Autonomous Platform (v1.2.0)

The **Guardian X-1** is an open-source, dual-mode hybrid rover-drone engineered for edge AI autonomy, local computer vision inference, and wide-area eSIM/LTE cellular failover.

---

## Features

- **Edge AI Processing:** Raspberry Pi 5 (8GB) paired with Hailo-8L NPU (13 TOPS) for local YOLOv8 detection and visual depth processing.
- **Dual-Mode Mobility:** Aerial flight (SpeedyBee F405 stack + EMAX ECO II motors) coupled with ground drive (N20 gearmotors).
- **Ecosystem Sync & eSIM Failover:** Real-time telemetry sync over local Wi-Fi mesh with automatic failover to LTE/eSIM for out-of-range operations.
- **Smartwatch & Wearable Integration:** Wearer biometric monitoring and remote override capability over cellular MQTT.

---

## Quick Build & System Specs

- **Total Target Budget:** $685 USD
- **Primary Compute:** Raspberry Pi 5 (8GB RAM) + Hailo-8L NPU
- **Storage:** M.2 HAT + 128GB NVMe SSD
- **Flight Controller:** SpeedyBee F405 V4 55A Stack
- **Sensors:** RPLIDAR A1M8, Arducam ToF Depth Sensor, IMX219 RGB Camera
- **Connectivity:** Dual LTE/eSIM Modules (Robot Core + Smartwatch)

---

## Directory Structure

```text
guardian-x1/
├── config/
│   └── control_params.yaml      # System settings, GPIO pins, and cellular APN settings
├── docs/
│   ├── architecture.md          # System architecture diagrams and topology
│   ├── assembly.md              # 3D printing parameters and mechanical assembly guide
│   └── wiring.md                # Pinouts, power distribution, and modem connections
├── hardware/
│   └── 3d_prints/               # OpenSCAD parametric sources and STL files
├── scripts/
│   ├── actuate_test.py          # Actuator verification script
│   └── test_llama.py            # Local LLM voice integration test
├── src/
│   ├── ai_engine/               # Hailo-8L NPU inference wrapper
│   ├── guardian_x1/             # Core state machine, flight bridge, cellular manager, web server
│   ├── smart_glasses/           # AR glasses display node
│   ├── smartwatch/              # Wearer biometric telemetry node
│   └── voice_ai/                # Local STT/TTS and Ollama voice assistant modules
├── web_ui/
│   ├── app.js                   # WebSocket telemetry client
│   ├── index.html               # Control panel interface
│   └── styles.css               # Dashboard styling
├── BOM.csv                      # Itemized bill of materials
├── requirements.txt             # Python environment dependencies
└── run.sh                       # Ecosystem master startup script


Getting Started
Prerequisites
Ubuntu 24.04 LTS (ARM64) or Raspberry Pi OS (Bookworm).

ROS 2 Humble Hawksbill installed and sourced.

Ollama server installed for local voice AI tasks (llama3.2:3b).

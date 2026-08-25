🛡️ Guardian X-1: Hybrid Autonomous Platform. An open-source, dual-mode hybrid rover-drone engineered for edge AI autonomy, wide-area eSIM/LTE failover, and real-time operator mesh sync.🌟 Overview: The Guardian X-1 is a high-performance, modular robotic platform built to bridge the gap between aerial surveillance and ground traversal. Powered by a Raspberry Pi 5 (8GB) paired with a Hailo-8L NPU (13 TOPS), the platform performs local object detection, depth segmentation, and autonomous state arbitration without relying on cloud round trips.Version v1.2.0 introduces dual eSIM/LTE cellular integration across both the robot core and operator smartwatch, ensuring zero-latency telemetry failover when moving outside local Wi-Fi mesh range.🏗️ System Architecture┌────────────────────────────────────────────────────────┐
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
📦 Bill of Materials Summary ($685 Optimized Spec)SubsystemKey ComponentsStatusEst. Cost (USD)Compute & AIRaspberry Pi 5 (8GB) + Hailo-8L NPUIntegrated & Tested$150StorageM.2 HAT + 128GB NVMe SSDFlashed & Booted$45Flight StackSpeedyBee F405 V4 55A StackWired & Bench-Tested$75Aerial Propulsion4x EMAX ECO II 2207 MotorsMounted to Booms$56Ground Drivetrain4x N20 Gearmotors + WheelsAssembled in Struts$28Chassis FrameHybrid Carbon + CF-PETG EnclosuresFully Assembled$50Power & Energy1x CNHL 4S 2200mAh LiPo + UBECCommissioned & Fused$35Mapping & SensorsRPLIDAR A1M8, ToF, RGB CameraROS 2 Communicating$181Connectivity2x Cellular LTE/eSIM Modules (Robot + Watch)Integrated$45Hardware / WiringFasteners, Inserts, HarnessesInstalled$20TOTAL$685📁 Repository StructurePlaintextguardian-x1/
├── config/
│   └── control_params.yaml      # System parameters, pins, and cellular APN settings
├── docs/
│   ├── architecture.md          # Detailed system diagrams & data flow
│   ├── assembly.md              # 3D print guide & hardware mechanical assembly
│   └── wiring.md                # Pinouts, power distribution, and eSIM wiring notes
├── hardware/
│   └── 3d_prints/               # OpenSCAD models and STL exports
├── scripts/
│   ├── actuate_test.py          # Actuator and drive verification harness
│   └── test_llama.py            # Local LLM integration validation script
├── src/
│   ├── ai_engine/               # Hailo NPU object detection nodes
│   ├── guardian_x1/             # Core flight bridge, state machine, cellular manager, web server
│   ├── smart_glasses/           # AR smart glasses sensor & display node
│   ├── smartwatch/              # Wearer biometric & eSIM telemetry node
│   └── voice_ai/                # Local STT, TTS, and Ollama voice assistant wrappers
├── web_ui/
│   ├── app.js                   # WebSocket dashboard client logic
│   ├── index.html               # Control panel & live cellular status dashboard
│   └── styles.css               # Dark-mode telemetry styling
├── BOM.csv                      # Full itemized bill of materials
├── LICENSE                      # MIT Open Source License
├── README.md                    # Project documentation
├── requirements.txt             # Python environment dependencies
└── run.sh                       # Ecosystem master launch script
🚀 Getting Started & Installation1. PrerequisitesOS: Ubuntu Server 24.04 LTS (ARM64) or Raspberry Pi OS (Bookworm)ROS 2 Distribution: Humble HawksbillAI Engine Runtime: HailoRT drivers and Ollama running locally (http://localhost:11434)2. Clone & Install DependenciesBashgit clone https://github.com/your-username/guardian-x1.git
cd guardian-x1
pip install -r requirements.txt
3. Launch the EcosystemUse the master launch script to spin up Ollama, the cellular manager, the smartwatch bridge, the web telemetry server, and the core ROS 2 state machine:Bashchmod +x run.sh
./run.sh
🌐 Web Control DashboardOnce the system is running, access the local control web server from any browser on your mesh network:URL: http://<robot_ip>:8080Features: Live camera feed, LiDAR mapping preview, eSIM signal status, and manual state overrides.📜 LicenseThis project is licensed under the terms of the MIT License.

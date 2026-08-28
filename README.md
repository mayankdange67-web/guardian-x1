# GUARDIAN X-1: Tactical Cybernetic Reconnaissance & Kinetic Autonomous Platform

[![ROS 2 - Humble](https://img.shields.io/badge/ROS%202-Humble%20Hawksbill-blue?style=for-the-badge&logo=ros)](https://docs.ros.org/en/humble/)
[![NPU Acceleration](https://img.shields.io/badge/NPU-Hailo--8L%2026%20TOPS-brightgreen?style=for-the-badge)](https://hailo.ai/)
[![MCU Bridge](https://img.shields.io/badge/Bridge-ESP32--S3-orange?style=for-the-badge&logo=espressif)](https://www.espressif.com/)
[![License](https://img.shields.io/badge/License-Responsible%20AI%20%2F%20Open-red?style=for-the-badge)](LICENSE)

**Guardian X-1** is an autonomous hybrid ground-air tactical platform integrated with a multi-device wearable telemetry and augmented reality ecosystem. Powered by a Deep Reinforcement Learning (DRL) Soft Actor-Critic (SAC) kinetic planner, 26 TOPS Hailo-8L neural inference engine, ESP32-S3 Wi-Fi CSI through-wall radar, smart glasses optical waveguide HUD, and an ambulatory blood pressure monitoring (ABPM) tactical smartwatch.

---

## 🚀 Key Features & Capabilities

### 🛡️ Core Platform & Hybrid Dynamics
- **Ground-to-Air Kinetic Switching:** High-speed 50 Hz ONNX inference (`sac_mode_policy.onnx`) executing real-time mode transitions between differential skid-steer ground locomotion and multirotor aerial flight.
- **PINN Flight Control:** Physics-Informed Neural Network (PINN) for aerial disturbance rejection under severe crosswinds and turbulent urban micro-climates.
- **Adaptive Ground Friction Estimation:** Vision Transformer (`terrain_vit_nano.onnx`) and strain-compliant GRF wheel struts for real-time terrain friction coefficient prediction.

### 🧠 Edge AI Engine & Neural Sensing
- **Hailo-8L Zero-Copy Object Detection:** Hardware-accelerated 26 TOPS 8-bit quantized YOLOv8 tactical target tracker running at low latency.
- **Wi-Fi CSI Through-Wall Occupancy Grid:** ESP32-S3 dual-core Wi-Fi Channel State Information (CSI) sub-GHz RF sensing for 2D occupant/threat detection behind solid barriers.
- **Localized Voice LLM & Face Embeddings:** On-device Llama-3.2 1B tool-calling model combined with persistent facial recognition and adaptive dialogue personality profiling (`user_profiles.json`).

### 👓 Smart Glasses Waveguide HUD Subsystem
- **Motorized Pop-Up Optics:** PWM stepper motor driver controlling deployment and stowing of the optical waveguide AR bay.
- **Tactical AR Rendering:** Real-time 640x400 heads-up overlay projecting target lock-on reticles, pitch ladder indicators, through-wall target vectors, and kinetic mode status directly into the operator's field of view.

### ⌚ Smartwatch & Biometric Telemetry Subsystem
- **Ambulatory Blood Pressure (ABPM):** Oscillometric micro-air pump and piezoelectric cuff controller for operational stress and vitals monitoring.
- **LRA Haptic Tactile Alerts:** Linear Resonant Actuator pattern driver providing distinct pulse tactile feedback when targets are detected through walls or critical warnings fire.
- **Earbud Dock & eSIM Supervisor:** TWS earbud charging supervisor with pop-up dial spring latch control and independent cellular LTE / Wi-Fi mesh automatic failover.

---

## 📁 System Architecture & Directory Layout

```text
guardian-x1/
├── config/
│   ├── control_params.yaml          # Neural PID gains, ESP32-S3 UART bridge, AP vs LTE thresholds
│   ├── ml_config.yaml               # DRL hyperparams, handoff model rules, Hailo-8L latency caps
│   └── user_profiles.json           # Dynamic store for facial embeddings and personalized dialogue profiles
├── docs/
│   ├── architecture.md              # Edge compute topology and ESP32-S3 dual-core routing specs
│   ├── assembly.md                  # Thermal specs, ESP32-S3-1U mounting, micro-cuff watch specs
│   ├── ml_pipeline.md               # DRL training architecture and Hailo HEF compilation workflow
│   └── wiring.md                    # Camera interfaces, ESP32 serial bus, SIM AT-command pinouts
├── firmware/
│   └── esp32_network_bridge/
│       ├── esp32_network_bridge.ino # Hybrid firmware for Wi-Fi CSI radar & ESP-NOW failover
│       └── sdkconfig                # Xtensa LX7 vector optimizations & high-throughput buffer config
├── hardware/
│   └── 3d_prints/
│       ├── chassis_floor.scad        # Vibration mounts, NPU heatsink, ESP32 carrier, SSD cradle
│       ├── front_fascia.scad         # 1.51-inch transparent OLED bezel & stereo camera bracket
│       ├── glasses_frame.scad        # Titanium-polymer hybrid frame with motorized optic bay
│       ├── guardian_x1.scad          # Master assembly clearance model
│       ├── side_rail.scad            # Generative topology-optimized chassis side rails
│       ├── top_hull.scad             # Sensor dome & dual IPEX 5dBi antenna mount
│       ├── watch_cuff_chassis.scad   # Alloy smartwatch housing with pump cavity & TWS dock
│       └── wheel_strut.scad          # Strain-compliant flexure design for GRF estimation
├── models/
│   ├── hailo/
│   │   └── yolov8n_tactical.hef     # Quantized 8-bit model for 26 TOPS Hailo-8L NPU
│   └── onnx/
│       ├── sac_mode_policy.onnx     # Soft Actor-Critic ground-flight kinetic switching policy
│       └── terrain_vit_nano.onnx    # ViT model for real-time surface friction prediction
├── scripts/
│   ├── actuate_test.py              # Actuator safety boundary verification against policy predictions
│   ├── memory_cleaner.py            # ROS log bag, bytecode cache, and OS page cache maintenance
│   ├── test_llama.py                # Local Ollama LLM context window & latency benchmark
│   └── train_sac_agent.py           # Isaac Sim reinforcement learning training with domain randomization
├── src/
│   ├── ai_engine/                   # Face recognition, Hailo YOLO, dialogue, LLM & CSI radar nodes
│   ├── display/                     # SSD1309 transparent OLED HUD driver
│   ├── guardian_x1/                 # Kinetic state machine, rover controller, flight bridge, cellular link
│   ├── smartglasses/                # Waveguide AR optical renderer & motorized pop-up optic nodes
│   └── smartwatch/                  # ABPM pump control, LRA haptics, eSIM manager, AMOLED UI
├── web_ui/
│   ├── app.js                       # WebGL 3D visualizer & real-time telemetry renderer
│   ├── index.html                   # Tactical dashboard displaying NPU usage & link status
│   └── styles.css                   # High-contrast dark-mode HUD styling
├── BOM.csv                          # System Bill of Materials (optical, cellular, structural)
├── LICENSE                          # Responsible AI & Autonomous Safety License
├── README.md                        # Master system architectural manual
├── requirements.txt                 # Python dependency manifest (PyTorch, ONNXRuntime, ROS 2, Luma)
└── run.sh                           # Master startup script (storage mount, drivers, cache flush, launch)


⚡ Quickstart & Deployment
1. Prerequisites
OS: Ubuntu 22.04 LTS (ROS 2 Humble Hawksbill)

Accelerator Drivers: HailoRT v4.17+ drivers and PCIe firmware installed

Python Dependencies: Python 3.10+

2. Environment Setup
Clone the repository into your ROS 2 workspace and install Python dependencies:

mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone [https://github.com/your-org/guardian-x1.git](https://github.com/your-org/guardian-x1.git)
cd guardian-x1
pip install -r requirements.txt


Compile and flash the firmware onto the ESP32-S3 co-processor using ESP-IDF or Arduino IDE:

cd firmware/esp32_network_bridge
# Flash esp32_network_bridge.ino with dual-core CSI sensing & ESP-NOW enabled

4. Build Workspace
Build the ROS 2 packages using colcon:

cd ~/ros2_ws
colcon build --symlink-install --packages-select ai_engine display guardian_x1 smartglasses smartwatch
source install/setup.bash

5. Launch System Stack
Run the master boot script to purge stale logs, initialize NPU contexts, start the WebSockets bridge, and launch all platform ROS 2 nodes:

chmod +x run.sh
./run.sh

Access the live WebGL tactical telemetry dashboard at http://localhost:8080 (or http://<PLATFORM_IP>:8080).

🛠 Hardware CAD & 3D Fabrication
All mechanical components are located under hardware/3d_prints/ in OpenSCAD format:

Glasses Frame (glasses_frame.scad): Open glasses_frame.scad in OpenSCAD to adjust lens width, nose bridge width, or stepper motor gear tolerances. Render and export to .STL for high-resolution SLA/DLP resin printing.

Smartwatch Housing (watch_cuff_chassis.scad): Contains internal cavities for the 5V micro-air pump, LRA vibration motor, piezo pressure transducer, and TWS earbud charging pins.

Platform Chassis (chassis_floor.scad, front_fascia.scad): Provides thermal heatsink channels for the Hailo-8L PCIe card and mounting vibration dampeners for the main compute board.

To render the complete master platform assembly:

openscad -o hardware/3d_prints/guardian_x1.stl hardware/3d_prints/guardian_x1.scad

📄 Licensing & Responsible AI Use Clause
Guardian X-1 is released under the Open-Source Responsible AI License contained in LICENSE.

Important Usage Restriction: Redistribution or deployment of this software for offensive autonomous kinetic strike operations without human-in-the-loop (HITL) oversight, targeting of non-combatants, or unlawful biometric surveillance is strictly prohibited under the terms of the platform license.

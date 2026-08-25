# 🛡️ Guardian X-1: Hybrid Autonomous Platform (v1.2.0)

The **Guardian X-1** is an open-source, hybrid autonomous rover-drone platform featuring dual-mode mobility (aerial flight + ground drive), local edge AI inference (Raspberry Pi 5 + Hailo-8L NPU), and wide-area **eSIM/LTE cellular failover** across both the robot core and operator smartwatch.

## 📦 Quick Build Summary
* **Target Budget:** $685 (Optimized Lean Spec)
* **Core Compute:** Raspberry Pi 5 (8GB) + Hailo-8L NPU (13 TOPS)
* **Connectivity:** Local Wi-Fi Mesh + Dual LTE/eSIM Modules (Robot & Watch)
* **Chassis:** Hybrid Carbon Fiber + CF-PETG Enclosures & TPU Tires
* **Sensors:** RPLIDAR A1M8, Arducam ToF, IMX219 Optical Camera

## 🚀 Getting Started
Clone the repository and launch the ecosystem:
```bash
git clone [https://github.com/your-repo/guardian-x1.git](https://github.com/your-repo/guardian-x1.git)
cd guardian-x1
pip install -r requirements.txt
./run.sh

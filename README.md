# Guardian X-1 Ecosystem 🚁🤖

Guardian X-1 is an autonomous, hybrid rover/drone robotics platform. It runs completely offline using a local AI voice engine (Llama 3.2 via Ollama on a Raspberry Pi 5 / Jetson), a real-time WebSocket web server, smartwatch gesture parsing, and smart glasses HUD telemetry.

## Features
- **Local AI Voice Control:** Powered by Whisper (STT) and Llama 3.2 1B/3B (SLM).
- **Hybrid Autonomy:** Unified code for quadrotor flight and differential ground drive.
- **Hardware Integrations:** Hailo-8L NPU Vision, Smartwatch disarms, and Web dashboard.
- **Parametric 3D Prints:** OpenSCAD files included for vibration-damped hardware mounts.

## Quick Start
```bash
git clone [https://github.com/YOUR_USERNAME/guardian-x1.git](https://github.com/YOUR_USERNAME/guardian-x1.git)
cd guardian-x1
pip install -r requirements.txt
curl -fsSL [https://ollama.com/install.sh](https://ollama.com/install.sh) | sh
ollama pull llama3.2:1b
chmod +x run.sh
./run.sh

# Guardian X-1 Machine Learning Pipeline & NPU Operations

## 1. Models & Compute Allocations

| Model Identifier | Architecture | Primary Device | Latency Budget | Output Function |
|---|---|---|---|---|
| `yolov8n_tactical.hef` | YOLOv8 Nano (Quantized INT8) | Hailo-8L NPU (26 TOPS) | `< 15.0 ms` | Real-time object classification and bounding boxes |
| `sac_mode_policy.onnx` | Soft Actor-Critic (SAC) DRL | Host CPU / ONNX Runtime | `< 5.0 ms` | Adaptive switching between ground rover & aerial flight modes |
| `terrain_vit_nano.onnx` | Vision Transformer (ViT-Nano) | Host CPU / Hailo-8L | `< 10.0 ms` | Friction coefficient prediction and wheel slip mitigation |
| `link_quality_predictor.onnx`| Multi-Layer Perceptron (MLP) | ESP32 Micro-NPU / Host | `< 2.0 ms` | Network drop prediction for proactive LTE failover |

---

## 2. Hailo-8L Quantization & Compilation Workflow

To run target recognition model `yolov8n_tactical` on the 26 TOPS Hailo-8L NPU:

```text
+----------------------+      ONNX Export      +-------------------------+
| PyTorch Model        |---------------------->| Quantization Dataset    |
| YOLOv8 Nano Training |                       | 1000 Operational Images |
+----------------------+                       +------------+------------+
                                                            |
                                                            v
+----------------------+      HEF Output       +-------------------------+
| Hailo-8L Executable  |<----------------------| Hailo Dataflow Compiler |
| yolov8n_tactical.hef |                       | (INT8 Optimization)     |
+----------------------+                       +-------------------------+

Execution Protocol inside ROS 2 Node (hailo_yolo_node.py)
Camera frame captured via V4L2 zero-copy memory buffer.

Tensor passed directly to HailoRT stream without host-side array copy.

Post-processing decodes output vectors to bounding box coordinates.

Telemetry overlay rendered directly to the front 1.51" Transparent OLED HUD via SSD1309 display driver

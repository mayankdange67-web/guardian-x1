# Guardian X-1 System Architecture

## 1. System Overview & Compute Topology

The **Guardian X-1** relies on a distributed edge-compute topology designed to isolate heavy neural processing, real-time vehicle dynamics, and cellular network telemetry across dedicated hardware units:

```text
+-----------------------------------------------------------------------------------+
|                                 GUARDIAN X-1 CORE                                 |
|                                                                                   |
|  +--------------------+       UART (921k)      +-------------------------------+  |
|  |  ESP32 Network     |<---------------------->| Raspberry Pi 5 (Primary Host) |  |
|  |  Co-Processor      |                        | - ROS 2 Jazzy Engine          |  |
|  +---------+----------+                        | - System State Machine        |  |
|            |                                   +---------------+---------------+  |
|   +--------+--------+                                          |                  |
|   |                 |                                    PCIe  |  USB 3.2       |
|   v                 v                                          v  v               |
| [Wi-Fi AP]      [SIM LTE]                             +------------------+        |
| Local Link      Failover                              | Hailo-8L NPU     |        |
| Direct UDP      AT Command                            | (26 TOPS Engine) |        |
|                                                       +------------------+        |
|                                                       | Verbatim Vx500   |        |
|                                                       | 240GB SSD        |        |
|                                                       +------------------+        |
+-----------------------------------------------------------------------------------+


2. ESP32 Network Co-Processor & Dual-Path Routing
To preserve Pi 5 CPU cycles and free up GPIO pins for hardware peripherals, an ESP32 co-processor handles network interface arbitration, RSSI monitoring, and AT-command parsing for the 4G/LTE SIM modem.

+----------------------------------+
               |     Incoming Remote Control      |
               +----------------+-----------------+
                                |
                                v
               +----------------------------------+
               |   ESP32 Link Quality Evaluator   |
               +----------------+-----------------+
                                |
         +----------------------+----------------------+
         | RSSI >= -78 dBm                             | RSSI < -78 dBm
         v                                             v
+------------------+                          +------------------+
|  Custom Wi-Fi    |                          | 4G/LTE SIM Modem |
|  Direct UDP Link |                          | MQTT / PPP Route |
+--------+---------+                          +--------+---------+
         |                                             |
         +----------------------+----------------------+
                                | Packet Encapsulation
                                v
                 +------------------------------+
                 | UART Stream (/dev/ttyAMA0)   |
                 | Baud: 921600                 |
                 +--------------+---------------+
                                |
                                v
                 +------------------------------+
                 | ROS 2 `esp32_comm_bridge`    |
                 +------------------------------+

Network Handoff Logic
Primary Path (Custom Local Network): Uses direct UDP sockets over ESP32 Wi-Fi Access Point mode (or ESP-NOW for low-latency point-to-point command frame streaming). Latency budget: < 8 ms.

Fallback Path (Cellular SIM): Active when local RSSI drops below -78 dBm or heartbeats drop for standard timeout (150 ms). The ESP32 switches packet routing over serial AT-commands to the SIM modem via MQTT/UDP tunnel. Latency budget: < 65 ms.

Pi 5 Interface: The Pi 5 receives clean, unified binary command frames over /dev/ttyAMA0 regardless of which network interface received the data.

3. Storage & Machine Learning Ingest Pipeline
The Verbatim Vx500 240GB External SSD (USB 3.2 Gen 2) handles continuous telemetry logging, raw video stream dumping, and local model inference caching:

/mnt/verbatim_vx500/
├── cache/
│   └── inferences/          # Zero-copy NPU tensor log frames
├── logs/
│   └── rosbags/             # MCAP format ROS 2 high-frequency sensor bags
└── models/                  # Backup dynamic ONNX weights for local policy reload


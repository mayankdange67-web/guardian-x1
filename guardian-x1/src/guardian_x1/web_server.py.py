#!/usr/bin/env python3
"""
Guardian X-1 WebSockets Telemetry & Video Streaming Server
----------------------------------------------------------
Streams real-time robot pose, NPU metrics, facial recognition locks, and bounding boxes
to the web tactical interface over WebSockets.
"""

import asyncio
import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
from sensor_msgs.msg import BatteryState
from vision_msgs.msg import Detection2DArray

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False


class WebServerNode(Node):
    def __init__(self):
        super().__init__("web_server_node")

        self.telemetry = {
            "mode": "ROVER",
            "user": "Unknown",
            "battery": 100.0,
            "npu_load": 0.0,
            "targets": 0
        }

        self.create_subscription(String, "/guardian_x1/kinetic_mode", lambda m: self.update_tel("mode", m.data), 10)
        self.create_subscription(String, "/ai/identified_person", lambda m: self.update_tel("user", m.data), 10)
        self.create_subscription(BatteryState, "/guardian_x1/battery", lambda m: self.update_tel("battery", m.percentage), 10)
        self.create_subscription(Float32, "/guardian_x1/npu_utilization", lambda m: self.update_tel("npu_load", m.data), 10)
        self.create_subscription(Detection2DArray, "/ai/detections", lambda m: self.update_tel("targets", len(m.detections)), 10)

        self.get_logger().info(f"[INIT] Web Server Node started (WebSockets Available: {WEBSOCKETS_AVAILABLE})")

    def update_tel(self, key, value):
        self.telemetry[key] = value


def main(args=None):
    rclpy.init(args=args)
    node = WebServerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
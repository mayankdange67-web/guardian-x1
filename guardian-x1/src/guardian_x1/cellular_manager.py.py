#!/usr/bin/env python3
"""
Guardian X-1 Predictive Cellular & Wi-Fi Link Manager Node
-----------------------------------------------------------
Monitors signal RSSI, evaluates network packet latency, and signals the ESP32-S3
co-processor to switch seamlessly between local Wi-Fi AP and LTE/5G cellular failover.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32, Bool


class CellularManagerNode(Node):
    def __init__(self):
        super().__init__("cellular_manager_node")

        self.declare_parameter("rssi_threshold", -82.0)
        self.declare_parameter("ping_latency_cap_ms", 150.0)

        self.rssi_thresh = self.get_parameter("rssi_threshold").get_parameter_value().double_value
        self.latency_cap = self.get_parameter("ping_latency_cap_ms").get_parameter_value().double_value

        self.create_subscription(Float32, "/network/wifi_rssi", self.rssi_callback, 10)
        self.create_subscription(Float32, "/network/ping_latency", self.latency_callback, 10)

        self.pub_network_cmd = self.create_publisher(String, "/esp32/network_mode", 10)

        self.current_mode = "WIFI_AP"
        self.get_logger().info("[INIT] Cellular Manager Node online. Target RSSI limit: %.1f dBm", self.rssi_thresh)

    def rssi_callback(self, msg: Float32):
        rssi = msg.data
        if rssi < self.rssi_thresh and self.current_mode == "WIFI_AP":
            self.current_mode = "LTE_CELLULAR"
            self._send_mode_switch("LTE")
            self.get_logger().warn(f"[FAILOVER] Wi-Fi RSSI dropped ({rssi:.1f} dBm). Switching to LTE Cellular.")
        elif rssi > (self.rssi_thresh + 10.0) and self.current_mode == "LTE_CELLULAR":
            self.current_mode = "WIFI_AP"
            self._send_mode_switch("WIFI")
            self.get_logger().info(f"[RESTORE] Wi-Fi RSSI recovered ({rssi:.1f} dBm). Reverting to local AP.")

    def latency_callback(self, msg: Float32):
        latency = msg.data
        if latency > self.latency_cap and self.current_mode == "WIFI_AP":
            self.get_logger().warn(f"[LATENCY WARNING] Ping latency {latency:.1f} ms exceeds cap.")

    def _send_mode_switch(self, mode: str):
        msg = String()
        msg.data = mode
        self.pub_network_cmd.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CellularManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
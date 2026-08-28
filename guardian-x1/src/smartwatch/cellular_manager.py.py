#!/usr/bin/env python3
"""
Guardian X-1 Smartwatch: Embedded eSIM & Independent Cellular Manager
---------------------------------------------------------------------
Supervises the smartwatch's standalone eSIM profile switcher, monitors LTE RSSI/RSRP
signal quality, and manages automated network failover between the tactical
mesh Wi-Fi link and direct cellular fallback.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32MultiArray
from std_srvs.srv import Trigger


class WatchCellularManagerNode(Node):
    def __init__(self):
        super().__init__("watch_cellular_manager_node")

        self.declare_parameter("primary_profile_id", "ESIM_TACTICAL_PRI")
        self.declare_parameter("secondary_profile_id", "ESIM_BACKUP_LTE")
        self.declare_parameter("rssi_failover_threshold_dbm", -95.0)

        self.active_profile = self.get_parameter("primary_profile_id").get_parameter_value().string_value
        self.rssi_threshold = self.get_parameter("rssi_failover_threshold_dbm").get_parameter_value().double_value

        self.current_rssi = -72.0  # dBm
        self.current_rsrp = -98.0  # dBm
        self.connection_state = "CONNECTED"

        self.pub_esim_status = self.create_publisher(String, "/smartwatch/esim_status", 10)
        self.pub_metrics = self.create_publisher(Float32MultiArray, "/smartwatch/cellular_metrics", 10)
        self.create_service(Trigger, "/smartwatch/switch_esim_profile", self.handle_switch_profile)

        self.create_timer(1.0, self.monitor_cellular_link)
        self.get_logger().info("[CELLULAR] Embedded eSIM Supervisor online.")

    def handle_switch_profile(self, request, response):
        pri = self.get_parameter("primary_profile_id").get_parameter_value().string_value
        sec = self.get_parameter("secondary_profile_id").get_parameter_value().string_value

        self.active_profile = sec if self.active_profile == pri else pri
        response.success = True
        response.message = f"Active eSIM profile switched to: {self.active_profile}"
        self.get_logger().info(f"[eSIM] Manual profile handoff executed -> {self.active_profile}")
        return response

    def monitor_cellular_link(self):
        status_msg = String()
        status_msg.data = f"{self.active_profile}:{self.connection_state}"
        self.pub_esim_status.publish(status_msg)

        metrics_msg = Float32MultiArray()
        metrics_msg.data = [float(self.current_rssi), float(self.current_rsrp)]
        self.pub_metrics.publish(metrics_msg)

        if self.current_rssi < self.rssi_threshold and self.connection_state == "CONNECTED":
            self.get_logger().warn(f"[eSIM] Low RSSI ({self.current_rssi} dBm). Initiating auto-failover link switch...")
            self.active_profile = self.get_parameter("secondary_profile_id").get_parameter_value().string_value


def main(args=None):
    rclpy.init(args=args)
    node = WatchCellularManagerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
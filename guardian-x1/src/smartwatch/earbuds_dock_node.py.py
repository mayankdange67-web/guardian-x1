#!/usr/bin/env python3
"""
Guardian X-1 Pop-Up Dial & TWS Earbud Dock Controller
------------------------------------------------------
Manages the spring-loaded pop-up watch cover latch mechanism, monitors earbud
magnetic docking presence, wireless charge levels, and audio connection state.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32MultiArray, Bool


class EarbudsDockNode(Node):
    def __init__(self):
        super().__init__("earbuds_dock_node")

        self.pub_earbud_status = self.create_publisher(Float32MultiArray, "/smartwatch/earbuds/battery", 10)
        self.pub_cover_state = self.create_publisher(String, "/smartwatch/cover_latch_state", 10)
        self.create_subscription(Bool, "/smartwatch/trigger_popup_dial", self.popup_callback, 10)

        self.cover_open = False
        self.left_battery = 100.0
        self.right_battery = 98.0

        self.create_timer(1.0, self.publish_telemetry)
        self.get_logger().info("[WATCH BUDS] Dial Pop-Up & TWS Dock Node online.")

    def popup_callback(self, msg: Bool):
        if msg.data:
            self.cover_open = not self.cover_open
            state_str = "OPEN" if self.cover_open else "CLOSED"
            self.get_logger().info(f"[WATCH BUDS] Dial latch button actuated. Cover state: {state_str}")

            state_msg = String()
            state_msg.data = state_str
            self.pub_cover_state.publish(state_msg)

    def publish_telemetry(self):
        bat_msg = Float32MultiArray()
        bat_msg.data = [self.left_battery, self.right_battery]
        self.pub_earbud_status.publish(bat_msg)


def main(args=None):
    rclpy.init(args=args)
    node = EarbudsDockNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
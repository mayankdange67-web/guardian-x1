#!/usr/bin/env python3
"""
Guardian X-1 Central State Machine & Safety Arbiter
----------------------------------------------------
Monitors system anomalies, manages state transitions between ROVER, HYBRID, and AERIAL modes,
and triggers emergency overrides when safety thresholds are breached.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from sensor_msgs.msg import BatteryState


class StateMachineNode(Node):
    def __init__(self):
        super().__init__("state_machine_node")

        self.current_state = "ROVER"

        self.create_subscription(String, "/guardian_x1/kinetic_mode_cmd", self.mode_cmd_callback, 10)
        self.create_subscription(BatteryState, "/guardian_x1/battery", self.battery_callback, 10)
        self.create_subscription(Bool, "/guardian_x1/emergency_stop", self.estop_callback, 10)

        self.pub_state = self.create_publisher(String, "/guardian_x1/kinetic_mode", 10)
        self.pub_estop = self.create_publisher(Bool, "/guardian_x1/emergency_stop", 10)

        self.create_timer(1.0, self.publish_state)
        self.get_logger().info("[INIT] State Machine Safety Arbiter active. Mode: ROVER")

    def mode_cmd_callback(self, msg: String):
        req_mode = msg.data.upper()
        if req_mode in ["ROVER", "HYBRID", "AERIAL"]:
            self.current_state = req_mode
            self.get_logger().info(f"[STATE MACHINE] Transitioned to kinetic mode: {self.current_state}")

    def battery_callback(self, msg: BatteryState):
        if msg.percentage < 10.0 and self.current_state == "AERIAL":
            self.get_logger().warn("[CRITICAL] Low battery in AERIAL mode! Forcing return-to-ground ROVER mode.")
            self.current_state = "ROVER"

    def estop_callback(self, msg: Bool):
        if msg.data:
            self.current_state = "ESTOP"
            self.get_logger().error("[EMERGENCY] System state locked in E-STOP condition.")

    def publish_state(self):
        msg = String()
        msg.data = self.current_state
        self.pub_state.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = StateMachineNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
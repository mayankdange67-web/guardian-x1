#!/usr/bin/env python3
"""
Guardian X-1 Smartwatch: Through-Wall Haptic Alert & Vision Bridge Node
------------------------------------------------------------------------
Evaluates polar target vectors published by the AI Engine radar stack. Triggers
pattern-coded LRA haptic wrist alerts when human targets are detected behind walls
and forwards threat status directly to the smartwatch display and smart glasses HUD.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, String


class ThroughWallVisionNode(Node):
    def __init__(self):
        super().__init__("through_wall_vision_node")

        self.declare_parameter("min_alert_confidence", 0.50)
        self.min_confidence = self.get_parameter("min_alert_confidence").get_parameter_value().double_value

        self.last_alert_time = 0.0
        self.target_present = False

        self.create_subscription(Float32MultiArray, "/smartwatch/through_wall_feed", self.radar_feed_callback, 10)

        self.pub_haptic = self.create_publisher(String, "/smartwatch/haptic_trigger", 10)
        self.pub_threat_status = self.create_publisher(String, "/smartwatch/threat_alert", 10)

        self.get_logger().info("[SMARTWATCH] Through-Wall Haptic Vision Supervisor active.")

    def radar_feed_callback(self, msg: Float32MultiArray):
        if len(msg.data) < 4:
            return

        dist, angle, confidence, attenuation = msg.data

        if confidence >= self.min_confidence and not self.target_present:
            self.target_present = True

            haptic_msg = String()
            haptic_msg.data = "THREAT_ALERT"
            self.pub_haptic.publish(haptic_msg)

            threat_msg = String()
            threat_msg.data = f"TARGET DETECTED: {dist:.1f}m @ {int(angle)}°"
            self.pub_threat_status.publish(threat_msg)

            self.get_logger().warn(f"[HAPTIC ALERT] Threat behind obstacle at {dist:.1f}m ({int(angle)}°)")
        elif confidence < (self.min_confidence - 0.15):
            self.target_present = False


def main(args=None):
    rclpy.init(args=args)
    node = ThroughWallVisionNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
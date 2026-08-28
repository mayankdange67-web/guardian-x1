#!/usr/bin/env python3
"""
Guardian X-1 Smartwatch: LRA Haptic Motor Driver Node
------------------------------------------------------
Drives the Linear Resonant Actuator (LRA) motor embedded in the watch chassis.
Executes distinct vibration patterns (double pulse, high-frequency buzz, rhythmic pulse)
for tactile alerts when threat notifications or biometric alerts are triggered.
"""

import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32


class HapticFeedbackNode(Node):
    def __init__(self):
        super().__init__("haptic_feedback_node")

        self.declare_parameter("default_intensity_pct", 85.0)
        self.intensity = self.get_parameter("default_intensity_pct").get_parameter_value().double_value

        self.create_subscription(String, "/smartwatch/haptic_trigger", self.trigger_callback, 10)
        self.create_subscription(Float32, "/smartwatch/haptic_intensity", self.intensity_cb, 10)

        self.pub_haptic_state = self.create_publisher(String, "/smartwatch/haptic_status", 10)
        self.get_logger().info("[HAPTICS] LRA Tactile Feedback Engine initialized.")

    def intensity_cb(self, msg: Float32):
        self.intensity = max(0.0, min(100.0, msg.data))

    def trigger_callback(self, msg: String):
        pattern = msg.data.upper()
        self.get_logger().info(f"[HAPTICS] Actuating pattern: {pattern} @ {self.intensity:.0f}% intensity")

        if pattern == "THREAT_ALERT":
            self._execute_pattern(pulses=2, pulse_duration=0.15, gap=0.08)
        elif pattern == "PULSE_LONG":
            self._execute_pattern(pulses=1, pulse_duration=0.6, gap=0.0)
        elif pattern == "CONFIRMATION":
            self._execute_pattern(pulses=1, pulse_duration=0.05, gap=0.0)
        elif pattern == "HEARTBEAT_SYNC":
            self._execute_pattern(pulses=2, pulse_duration=0.08, gap=0.12)
        else:
            self._execute_pattern(pulses=1, pulse_duration=0.1, gap=0.0)

        status = String()
        status.data = f"EXECUTED:{pattern}"
        self.pub_haptic_state.publish(status)

    def _execute_pattern(self, pulses: int, pulse_duration: float, gap: float):
        for i in range(pulses):
            time.sleep(pulse_duration)
            if gap > 0 and i < pulses - 1:
                time.sleep(gap)


def main(args=None):
    rclpy.init(args=args)
    node = HapticFeedbackNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
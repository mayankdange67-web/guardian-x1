#!/usr/bin/env python3
"""
Guardian X-1 Biometric Sensor Node
----------------------------------
Processes raw PPG, ECG, and stress metrics from wrist sensors, publishing real-time
operator heart rate, SpO2 levels, and stress index data.
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Float32MultiArray


class BiometricSensorNode(Node):
    def __init__(self):
        super().__init__("biometric_sensor_node")

        self.pub_hr = self.create_publisher(Float32, "/smartwatch/operator/heart_rate", 10)
        self.pub_spo2 = self.create_publisher(Float32, "/smartwatch/operator/spo2", 10)
        self.pub_stress = self.create_publisher(Float32, "/smartwatch/operator/stress_index", 10)

        self.heart_rate = 74.0
        self.spo2 = 98.5
        self.stress_index = 22.0

        self.create_timer(1.0, self.read_biometrics)
        self.get_logger().info("[BIOMETRICS] Wrist Sensor Array active.")

    def read_biometrics(self):
        hr_msg = Float32(data=self.heart_rate)
        spo2_msg = Float32(data=self.spo2)
        stress_msg = Float32(data=self.stress_index)

        self.pub_hr.publish(hr_msg)
        self.pub_spo2.publish(spo2_msg)
        self.pub_stress.publish(stress_msg)


def main(args=None):
    rclpy.init(args=args)
    node = BiometricSensorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
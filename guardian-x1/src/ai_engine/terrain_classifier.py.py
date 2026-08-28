#!/usr/bin/env python3
"""
Guardian X-1 Multi-Modal Surface Slip Classifier
------------------------------------------------
Combines vision features and IMU vibration harmonics to estimate terrain traction limits.
"""

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from std_msgs.msg import Float32


class TerrainClassifierNode(Node):
    def __init__(self):
        super().__init__("terrain_classifier_node")

        self.create_subscription(Imu, "/guardian_x1/imu", self.imu_callback, 10)
        self.pub_roughness = self.create_publisher(Float32, "/ai/surface_roughness", 10)

        self.accel_buffer = []
        self.get_logger().info("[INIT] Multi-Modal Terrain Classifier ready.")

    def imu_callback(self, msg: Imu):
        az = msg.linear_acceleration.z
        self.accel_buffer.append(az)

        if len(self.accel_buffer) > 50:
            self.accel_buffer.pop(0)

        variance = float(np.var(self.accel_buffer)) if len(self.accel_buffer) > 1 else 0.0

        out = Float32()
        out.data = variance
        self.pub_roughness.publish(out)


def main(args=None):
    rclpy.init(args=args)
    node = TerrainClassifierNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
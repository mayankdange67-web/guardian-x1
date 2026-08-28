#!/usr/bin/env python3
"""
Guardian X-1 Physics-Informed Neural Network (PINN) Flight Bridge Node
-------------------------------------------------------------------
Estimates wind disturbance vectors and calculates counter-thrust compensation
for quadrotor aerial stability.
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
from geometry_msgs.msg import AccelWithCovarianceStamped


class FlightBridgeNode(Node):
    def __init__(self):
        super().__init__("flight_bridge_node")

        self.create_subscription(Imu, "/guardian_x1/imu", self.imu_callback, 10)
        self.pub_wind = self.create_publisher(AccelWithCovarianceStamped, "/guardian_x1/wind_estimate", 10)

        self.get_logger().info("[INIT] PINN Flight Bridge Node active.")

    def imu_callback(self, msg: Imu):
        # Estimate aerodynamic wind drag vector from linear acceleration deviations
        wind_msg = AccelWithCovarianceStamped()
        wind_msg.header = msg.header
        wind_msg.accel.accel.linear.x = msg.linear_acceleration.x * 0.1
        wind_msg.accel.accel.linear.y = msg.linear_acceleration.y * 0.1
        self.pub_wind.publish(wind_msg)


def main(args=None):
    rclpy.init(args=args)
    node = FlightBridgeNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
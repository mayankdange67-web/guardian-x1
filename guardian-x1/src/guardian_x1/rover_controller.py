#!/usr/bin/env python3
"""
Guardian X-1 Ground Drivetrain Controller Node
Drives TB6612FNG motor driver pins over gpiod (/dev/gpiochip4) on Raspberry Pi 5.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class RoverControllerNode(Node):
    def __init__(self):
        super().__init__('rover_controller_node')
        self.get_logger().info("Initializing TB6612FNG Ground Drivetrain Controller...")

        self.declare_parameter('pins.gpio_chip', '/dev/gpiochip4')
        self.declare_parameter('pins.motor_left_dir', 17)
        self.declare_parameter('pins.motor_left_pwm', 12)
        self.declare_parameter('pins.motor_right_dir', 27)
        self.declare_parameter('pins.motor_right_pwm', 13)

        self.subscription = self.create_subscription(
            Twist, '/cmd_vel', self.cmd_vel_callback, 10
        )

    def cmd_vel_callback(self, msg: Twist):
        linear_x = msg.linear.x
        angular_z = msg.angular.z

        # Differential drive kinematic calculation
        left_speed = linear_x - angular_z
        right_speed = linear_x + angular_z
        self.get_logger().debug(f"[ROVER DRIVE] L: {left_speed:.2f}, R: {right_speed:.2f}")

def main(args=None):
    rclpy.init(args=args)
    node = RoverControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

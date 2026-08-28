#!/usr/bin/env python3
"""
Guardian X-1 Neural Adaptive Differential Rover Controller
----------------------------------------------------------
Computes wheel slip-compensated motor velocities for precise skid-steering locomotion.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import JointState
from std_msgs.msg import Float32


class RoverControllerNode(Node):
    def __init__(self):
        super().__init__("rover_controller_node")

        self.track_width = 0.42  # meters between left and right wheels
        self.wheel_radius = 0.085  # meters

        self.surface_friction = 0.85  # Default asphalt

        self.create_subscription(Twist, "/guardian_x1/cmd_vel", self.cmd_callback, 10)
        self.create_subscription(Float32, "/ai/terrain_friction", self.friction_callback, 10)

        self.pub_joints = self.create_publisher(JointState, "/guardian_x1/wheel_commands", 10)

        self.get_logger().info("[INIT] Rover Differential Controller online.")

    def friction_callback(self, msg: Float32):
        self.surface_friction = max(0.1, msg.data)

    def cmd_callback(self, msg: Twist):
        v = msg.linear.x
        omega = msg.angular.z

        # Differential kinematics with slip compensation factor (1 / friction)
        slip_comp = 1.0 / self.surface_friction
        v_left = (v - (omega * self.track_width / 2.0)) * slip_comp
        v_right = (v + (omega * self.track_width / 2.0)) * slip_comp

        w_left = v_left / self.wheel_radius
        w_right = v_right / self.wheel_radius

        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name = ["left_wheel_joint", "right_wheel_joint"]
        js.velocity = [float(w_left), float(w_right)]
        self.pub_joints.publish(js)


def main(args=None):
    rclpy.init(args=args)
    node = RoverControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
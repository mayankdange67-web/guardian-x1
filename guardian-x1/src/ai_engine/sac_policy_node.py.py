#!/usr/bin/env python3
"""
Guardian X-1 SAC Kinetic Mode Policy Node
-----------------------------------------
Executes ONNX SAC policy at 50 Hz to select real-time ground/aerial drive commands
and execute seamless mode switching (Rover / Hybrid / Aerial).
"""

import os
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from sensor_msgs.msg import Imu, JointState, BatteryState
from std_msgs.msg import String, Float32
import onnxruntime as ort


class SACPolicyNode(Node):
    def __init__(self):
        super().__init__("sac_policy_node")

        self.declare_parameter("onnx_path", "models/onnx/sac_mode_policy.onnx")
        onnx_path = self.get_parameter("onnx_path").get_parameter_value().string_value

        self.get_logger().info(f"[INIT] Loading SAC Kinetic Policy ONNX model from: {onnx_path}")
        if os.path.exists(onnx_path):
            self.ort_session = ort.InferenceSession(onnx_path, providers=["CPUExecutionProvider"])
        else:
            self.get_logger().error(f"[ERROR] SAC ONNX file not found at '{onnx_path}'")
            self.ort_session = None

        self.state_vector = np.zeros((1, 18), dtype=np.float32)

        # Subscriptions
        self.create_subscription(Odometry, "/guardian_x1/odom", self.odom_callback, 10)
        self.create_subscription(Imu, "/guardian_x1/imu", self.imu_callback, 10)
        self.create_subscription(JointState, "/guardian_x1/joint_states", self.joint_callback, 10)
        self.create_subscription(BatteryState, "/guardian_x1/battery", self.battery_callback, 10)
        self.create_subscription(Float32, "/ai/terrain_friction", self.friction_callback, 10)

        # Publishers
        self.pub_cmd = self.create_publisher(Twist, "/guardian_x1/cmd_vel", 10)
        self.pub_mode = self.create_publisher(String, "/guardian_x1/kinetic_mode", 10)

        # 50 Hz Execution Timer Loop
        self.create_timer(0.02, self.control_loop)

        self.mode_labels = ["ROVER", "HYBRID", "AERIAL"]

    def odom_callback(self, msg: Odometry):
        self.state_vector[0, 0] = msg.pose.pose.position.x
        self.state_vector[0, 1] = msg.pose.pose.position.y
        self.state_vector[0, 2] = msg.pose.pose.position.z
        self.state_vector[0, 3] = msg.twist.twist.linear.x
        self.state_vector[0, 4] = msg.twist.twist.linear.y
        self.state_vector[0, 5] = msg.twist.twist.linear.z

    def imu_callback(self, msg: Imu):
        qx, qy, qz, qw = msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w
        roll = np.arctan2(2.0 * (qw * qx + qy * qz), 1.0 - 2.0 * (qx * qx + qy * qy))
        pitch = np.arcsin(np.clip(2.0 * (qw * qy - qz * qx), -1.0, 1.0))
        yaw = np.arctan2(2.0 * (qw * qz + qx * qy), 1.0 - 2.0 * (qy * qy + qz * qz))

        self.state_vector[0, 6] = roll
        self.state_vector[0, 7] = pitch
        self.state_vector[0, 8] = yaw
        self.state_vector[0, 9] = msg.angular_velocity.x
        self.state_vector[0, 10] = msg.angular_velocity.y
        self.state_vector[0, 11] = msg.angular_velocity.z

    def joint_callback(self, msg: JointState):
        if len(msg.velocity) >= 4:
            self.state_vector[0, 12:16] = np.clip(msg.velocity[:4], 0.0, 1.0)

    def battery_callback(self, msg: BatteryState):
        self.state_vector[0, 16] = msg.percentage

    def friction_callback(self, msg: Float32):
        self.state_vector[0, 17] = msg.data

    def control_loop(self):
        if self.ort_session is None:
            return

        inputs = {"robot_state": self.state_vector}
        action_mean, action_log_std, mode_probs = self.ort_session.run(None, inputs)

        cmd = Twist()
        cmd.linear.x = float(action_mean[0, 0] * 2.0)
        cmd.linear.y = float(action_mean[0, 1] * 2.0)
        cmd.linear.z = float(action_mean[0, 2] * 2.0)
        cmd.angular.z = float(action_mean[0, 5] * 1.5)
        self.pub_cmd.publish(cmd)

        selected_mode_idx = int(np.argmax(mode_probs[0]))
        mode_msg = String()
        mode_msg.data = self.mode_labels[selected_mode_idx]
        self.pub_mode.publish(mode_msg)


def main(args=None):
    rclpy.init(args=args)
    node = SACPolicyNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()x
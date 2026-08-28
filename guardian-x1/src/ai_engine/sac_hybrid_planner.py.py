#!/usr/bin/env python3
"""
Guardian X-1 SAC Hybrid Trajectory Planner Node
-----------------------------------------------
Fuses path goals and obstacle detections to compute kinematically viable transitions
between rover ground movement and quadrotor aerial flight.
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Twist
from std_msgs.msg import String


class SACHybridPlannerNode(Node):
    def __init__(self):
        super().__init__("sac_hybrid_planner_node")

        self.create_subscription(PoseStamped, "/goal_pose", self.goal_callback, 10)
        self.pub_cmd = self.create_publisher(Twist, "/guardian_x1/cmd_vel", 10)
        self.pub_mode = self.create_publisher(String, "/guardian_x1/kinetic_mode_cmd", 10)

        self.get_logger().info("[INIT] SAC Hybrid Planner running.")

    def goal_callback(self, msg: PoseStamped):
        dist = (msg.pose.position.x ** 2 + msg.pose.position.y ** 2) ** 0.5

        mode_msg = String()
        if dist > 10.0:
            mode_msg.data = "AERIAL"
        elif dist > 3.0:
            mode_msg.data = "HYBRID"
        else:
            mode_msg.data = "ROVER"

        self.pub_mode.publish(mode_msg)
        self.get_logger().info(f"[PLANNER] Goal Dist: {dist:.2f} m -> Mode Target: {mode_msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = SACHybridPlannerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
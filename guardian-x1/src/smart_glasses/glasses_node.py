#!/usr/bin/env python3
"""
Guardian X-1 AR Smart Glasses Head-Up Display Node
Streams real-time HUD telemetry, battery status, and target lock reticles to operator AR glasses.
"""

import json
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class SmartGlassesNode(Node):
    def __init__(self):
        super().__init__('smart_glasses_node')
        self.get_logger().info("Initializing AR Smart Glasses HUD Telemetry Node...")

        self.hud_publisher = self.create_publisher(String, '/ecosystem/glasses/hud', 10)
        self.subscription = self.create_subscription(
            String, '/guardian/state_machine/status', self.state_callback, 10
        )

    def state_callback(self, msg: String):
        try:
            robot_state = json.loads(msg.data)
            hud_payload = {
                "display": "AR_HUD_V1",
                "robot_mode": robot_state.get("mode"),
                "robot_batt": robot_state.get("battery_v"),
                "reticle_status": "LOCKED"
            }
            hud_msg = String()
            hud_msg.data = json.dumps(hud_payload)
            self.hud_publisher.publish(hud_msg)
        except Exception:
            pass

def main(args=None):
    rclpy.init(args=args)
    node = SmartGlassesNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

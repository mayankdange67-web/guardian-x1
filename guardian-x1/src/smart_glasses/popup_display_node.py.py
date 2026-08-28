#!/usr/bin/env python3
"""
Guardian X-1 Smart Glasses: Motorized Pop-Up Optic Bay Driver Node
------------------------------------------------------------------
Controls the micro-stepper motor and optoelectronic end-stops embedded in the
glasses frame. Actuates the optical waveguide element between STOWED (folded upper frame)
and DEPLOYED (in front of operator eye line) positions.
"""

import time
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String
from std_srvs.srv import Trigger


class PopupDisplayNode(Node):
    def __init__(self):
        super().__init__("popup_display_node")

        self.declare_parameter("stepper_step_pin", 18)
        self.declare_parameter("stepper_dir_pin", 19)
        self.declare_parameter("travel_time_sec", 0.45)

        self.travel_time = self.get_parameter("travel_time_sec").get_parameter_value().double_value

        self.state = "DEPLOYED"  # Possible states: STOWED, DEPLOYING, DEPLOYED, RETRACTING

        # Publishers & Services
        self.pub_state = self.create_publisher(String, "/smartglasses/popup_state", 10)
        self.create_subscription(Bool, "/smartglasses/cmd_popup", self.command_callback, 10)
        self.create_service(Trigger, "/smartglasses/toggle_popup", self.handle_toggle_service)

        self.create_timer(0.2, self.publish_state)
        self.get_logger().info("[SMARTGLASSES MOTOR] Waveguide Pop-up Actuator Node ready.")

    def handle_toggle_service(self, request, response):
        target_deploy = (self.state == "STOWED")
        self._actuate_waveguide(target_deploy)
        response.success = True
        response.message = f"Waveguide optic bay transitioned to: {self.state}"
        return response

    def command_callback(self, msg: Bool):
        if msg.data and self.state == "STOWED":
            self._actuate_waveguide(deploy=True)
        elif not msg.data and self.state == "DEPLOYED":
            self._actuate_waveguide(deploy=False)

    def _actuate_waveguide(self, deploy: bool):
        if deploy:
            self.state = "DEPLOYING"
            self.publish_state()
            self.get_logger().info("[SMARTGLASSES] Engaging stepper driver -> DEPLOYING optic bay...")
            time.sleep(self.travel_time)
            self.state = "DEPLOYED"
        else:
            self.state = "RETRACTING"
            self.publish_state()
            self.get_logger().info("[SMARTGLASSES] Engaging stepper driver -> STOWING optic bay...")
            time.sleep(self.travel_time)
            self.state = "STOWED"

        self.get_logger().info(f"[SMARTGLASSES] Optic bay movement complete. State: {self.state}")

    def publish_state(self):
        msg = String()
        msg.data = self.state
        self.pub_state.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = PopupDisplayNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
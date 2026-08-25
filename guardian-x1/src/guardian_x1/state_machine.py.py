#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class GuardianStateMachine(Node):
    def __init__(self):
        super().__init__('state_machine')
        self.get_logger().info("Guardian X-1 State Machine Initialized ($600 Config)")

        # Load parameters matching control_params.yaml
        self.declare_parameter('sensors.thermal_enabled', False)
        self.declare_parameter('sensors.radar_enabled', False)

        self.thermal_active = self.get_parameter('sensors.thermal_enabled').value
        self.radar_active = self.get_parameter('sensors.radar_enabled').value

        # Conditional subscriptions based on hardware tier
        if self.thermal_active:
            self.get_logger().info("Thermal sensor subscription active.")
        else:
            self.get_logger().info("Thermal sensor omitted in current budget build.")

        if self.radar_active:
            self.get_logger().info("Radar sensor subscription active.")
        else:
            self.get_logger().info("Radar sensor omitted in current budget build.")


def main(args=None):
    rclpy.init(args=args)
    node = GuardianStateMachine()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
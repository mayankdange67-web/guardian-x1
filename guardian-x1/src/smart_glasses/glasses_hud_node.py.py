#!/usr/bin/env python3
"""
Guardian X-1 Smart Glasses: Optical Waveguide HUD Renderer Node
---------------------------------------------------------------
Projects tactical AR overlays directly into the operator's field of view via
the pop-up waveguide optical engine. Visualizes real-time through-wall radar
target reticles, threat vectors, recognized target identity cards, and kinetic
mode status.
"""

import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32MultiArray, String
from PIL import Image, ImageDraw, ImageFont


class GlassesHudNode(Node):
    def __init__(self):
        super().__init__("glasses_hud_node")

        self.declare_parameter("waveguide_res_x", 640)
        self.declare_parameter("waveguide_res_y", 400)
        self.declare_parameter("hud_refresh_rate_hz", 30.0)

        self.res_x = self.get_parameter("waveguide_res_x").get_parameter_value().integer_value
        self.res_y = self.get_parameter("waveguide_res_y").get_parameter_value().integer_value
        refresh_hz = self.get_parameter("hud_refresh_rate_hz").get_parameter_value().double_value

        # State Telemetry Buffers
        self.kinetic_mode = "ROVER"
        self.threat_text = ""
        self.person_name = "UNIDENTIFIED"
        self.radar_target = {"dist": 0.0, "angle": 0.0, "conf": 0.0, "atten": 0}
        self.hud_deployed = True

        # Subscriptions
        self.create_subscription(String, "/guardian_x1/kinetic_mode", lambda m: setattr(self, "kinetic_mode", m.data), 10)
        self.create_subscription(String, "/smartwatch/threat_alert", lambda m: setattr(self, "threat_text", m.data), 10)
        self.create_subscription(String, "/ai_engine/dialogue_target", lambda m: setattr(self, "person_name", m.data), 10)
        self.create_subscription(Float32MultiArray, "/smartwatch/through_wall_feed", self.radar_callback, 10)
        self.create_subscription(String, "/smartglasses/popup_state", self.popup_state_callback, 10)

        # HUD Stream Publisher
        self.pub_hud_status = self.create_publisher(String, "/smartglasses/hud_status", 10)

        self.font = ImageFont.load_default()
        self.create_timer(1.0 / refresh_hz, self.render_hud_frame)
        self.get_logger().info(f"[SMARTGLASSES HUD] Waveguide Optical Renderer initialized ({self.res_x}x{self.res_y} @ {int(refresh_hz)}Hz).")

    def popup_state_callback(self, msg: String):
        self.hud_deployed = (msg.data == "DEPLOYED")

    def radar_callback(self, msg: Float32MultiArray):
        if len(msg.data) >= 4:
            self.radar_target["dist"] = msg.data[0]
            self.radar_target["angle"] = msg.data[1]
            self.radar_target["conf"] = msg.data[2]
            self.radar_target["atten"] = int(msg.data[3])

    def render_hud_frame(self):
        if not self.hud_deployed:
            return

        # Create monochrome high-contrast optical mask frame
        img = Image.new("1", (self.res_x, self.res_y), 0)
        draw = ImageDraw.Draw(img)

        # Draw Corner Bounding Reticles (Tactical Frame)
        draw.line([(10, 10), (40, 10)], fill=1, width=2)
        draw.line([(10, 10), (10, 40)], fill=1, width=2)
        draw.line([(self.res_x - 40, 10), (self.res_x - 10, 10)], fill=1, width=2)
        draw.line([(self.res_x - 10, 10), (self.res_x - 10, 40)], fill=1, width=2)

        # Top Center System Header
        draw.text((self.res_x // 2 - 80, 12), f"MODE: {self.kinetic_mode} | TARGET: {self.person_name}", font=self.font, fill=1)
        draw.line([(self.res_x // 2 - 100, 26), (self.res_x // 2 + 100, 26)], fill=1)

        # Center Crosshair & Pitch Ladder
        cx, cy = self.res_x // 2, self.res_y // 2
        draw.line([(cx - 15, cy), (cx + 15, cy)], fill=1)
        draw.line([(cx, cy - 15), (cx, cy + 15)], fill=1)

        # Through-Wall Target Visual Overlay
        if self.radar_target["conf"] > 0.4:
            ang_rad = math.radians(self.radar_target["angle"] - 90.0)
            norm_dist = min(1.0, self.radar_target["dist"] / 12.0)
            target_x = cx + int((norm_dist * 180) * math.cos(ang_rad))
            target_y = cy + int((norm_dist * 120) * math.sin(ang_rad))

            # Draw Target Reticle Circle & Bearing Line
            draw.ellipse([(target_x - 12, target_y - 12), (target_x + 12, target_y + 12)], fill=0, outline=1)
            draw.line([(cx, cy), (target_x, target_y)], fill=1)
            draw.text(
                (target_x + 15, target_y - 6),
                f"WALL TGT {self.radar_target['dist']:.1f}m ({int(self.radar_target['angle'])}°)",
                font=self.font, fill=1
            )

        # Active Threat Banner
        if self.threat_text:
            draw.rectangle([(cx - 140, self.res_y - 50), (cx + 140, self.res_y - 20)], outline=1, fill=0)
            draw.text((cx - 120, self.res_y - 42), f"ALERT: {self.threat_text}", font=self.font, fill=1)

        status = String()
        status.data = f"RENDERING:TGT_CONF={self.radar_target['conf']:.2f}"
        self.pub_hud_status.publish(status)


def main(args=None):
    rclpy.init(args=args)
    node = GlassesHudNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
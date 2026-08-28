#!/usr/bin/env python3
"""
Guardian X-1 Light & Slick AMOLED Watch Display Node
---------------------------------------------------
Renders dynamic high-density telemetry UI combining ABPM blood pressure,
TWS earbuds charge status, eSIM network link, and real-time polar radar feeds.
"""

import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32, Float32MultiArray
from PIL import Image, ImageDraw, ImageFont


class WatchDisplayNode(Node):
    def __init__(self):
        super().__init__("watch_display_node")

        self.width = 128
        self.height = 128

        self.mode = "ROVER"
        self.heart_rate = 74.0
        self.systolic = 120
        self.diastolic = 80
        self.left_bud = 100
        self.right_bud = 98
        self.esim_status = "LTE"
        self.tw_target = {"dist": 0.0, "angle": 0.0, "conf": 0.0, "atten": 0}

        self.create_subscription(String, "/guardian_x1/kinetic_mode", lambda m: setattr(self, "mode", m.data), 10)
        self.create_subscription(Float32, "/smartwatch/operator/heart_rate", lambda m: setattr(self, "heart_rate", m.data), 10)
        self.create_subscription(Float32MultiArray, "/smartwatch/health/blood_pressure", self.bp_cb, 10)
        self.create_subscription(Float32MultiArray, "/smartwatch/earbuds/battery", self.buds_cb, 10)
        self.create_subscription(String, "/smartwatch/esim_status", lambda m: setattr(self, "esim_status", m.data), 10)
        self.create_subscription(Float32MultiArray, "/smartwatch/through_wall_feed", self.tw_cb, 10)

        self.font_sm = ImageFont.load_default()
        self.create_timer(1.0 / 20.0, self.render_frame)
        self.get_logger().info("[DISPLAY] Slick Hybrid Watch AMOLED UI driver active.")

    def bp_cb(self, msg: Float32MultiArray):
        if len(msg.data) >= 2:
            self.systolic = int(msg.data[0])
            self.diastolic = int(msg.data[1])

    def buds_cb(self, msg: Float32MultiArray):
        if len(msg.data) >= 2:
            self.left_bud = int(msg.data[0])
            self.right_bud = int(msg.data[1])

    def tw_cb(self, msg: Float32MultiArray):
        if len(msg.data) >= 4:
            self.tw_target["dist"] = msg.data[0]
            self.tw_target["angle"] = msg.data[1]
            self.tw_target["conf"] = msg.data[2]
            self.tw_target["atten"] = int(msg.data[3])

    def render_frame(self):
        img = Image.new("1", (self.width, self.height), 0)
        draw = ImageDraw.Draw(img)

        # Header Bar
        draw.rectangle([(0, 0), (127, 12)], fill=1)
        draw.text((3, 2), "G-X1 HYBRID WATCH", font=self.font_sm, fill=0)
        draw.text((98, 2), f"{self.esim_status[:3]}", font=self.font_sm, fill=0)

        # Health & Earbuds Status
        draw.text((4, 16), f"BP : {self.systolic}/{self.diastolic} mmHg", font=self.font_sm, fill=1)
        draw.text((4, 27), f"BUDS L:{self.left_bud}% R:{self.right_bud}%", font=self.font_sm, fill=1)
        draw.text((4, 38), f"HR  : {int(self.heart_rate)} BPM | {self.mode}", font=self.font_sm, fill=1)

        # Polar Radar View
        draw.line([(0, 50), (127, 50)], fill=1)
        center_x, center_y = 64, 88
        radius = 32

        draw.arc([(center_x - radius, center_y - radius), (center_x + radius, center_y + radius)], start=180, end=360, fill=1)
        draw.line([(center_x - radius, center_y - 10), (center_x + radius, center_y - 10)], fill=1)

        if self.tw_target["conf"] > 0.25:
            scaled_r = int((self.tw_target["dist"] / 12.0) * radius)
            ang_rad = math.radians(self.tw_target["angle"] - 90.0)
            tx = center_x + int(scaled_r * math.cos(ang_rad))
            ty = center_y + int(scaled_r * math.sin(ang_rad))

            draw.ellipse([(tx - 3, ty - 3), (tx + 3, ty + 3)], fill=1)
            draw.text((4, 114), f"TGT:{self.tw_target['dist']:.1f}m | {self.tw_target['atten']}dB", font=self.font_sm, fill=1)
        else:
            draw.text((32, 114), "RADAR CLEAR", font=self.font_sm, fill=1)


def main(args=None):
    rclpy.init(args=args)
    node = WatchDisplayNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Guardian X-1 Local LLM Ollama Voice Command Node
------------------------------------------------
Interfaces with local `ollama/llama3.2:1b` over REST API to convert natural language
voice transcriptions into structured JSON tool calls for autonomy control.
"""

import json
import requests
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
from geometry_msgs.msg import PoseStamped


class OllamaVoiceNode(Node):
    def __init__(self):
        super().__init__("ollama_voice_node")

        self.declare_parameter("ollama_url", "http://localhost:11434/api/generate")
        self.declare_parameter("model_name", "llama3.2:1b")

        self.ollama_url = self.get_parameter("ollama_url").get_parameter_value().string_value
        self.model_name = self.get_parameter("model_name").get_parameter_value().string_value

        self.sub_transcript = self.create_subscription(String, "/audio/voice_command", self.command_callback, 10)
        self.pub_mode_req = self.create_publisher(String, "/guardian_x1/kinetic_mode_cmd", 10)
        self.pub_goal = self.create_publisher(PoseStamped, "/goal_pose", 10)
        self.pub_estop = self.create_publisher(Bool, "/guardian_x1/emergency_stop", 10)

        self.system_prompt = (
            "You are Guardian X-1 Tactical AI. Convert speech commands into JSON tool calls.\n"
            "Valid schemas:\n"
            '1. {"tool": "set_mode", "mode": "rover"|"aerial"|"hybrid"}\n'
            '2. {"tool": "navigate_to", "x": float, "y": float}\n'
            '3. {"tool": "emergency_stop"}\n'
            "Return ONLY valid raw JSON."
        )

        self.get_logger().info(f"[INIT] Ollama Voice AI Node connected to model: {self.model_name}")

    def command_callback(self, msg: String):
        text = msg.data.strip()
        self.get_logger().info(f"[VOICE IN] Command: '{text}'")

        payload = {
            "model": self.model_name,
            "prompt": f"{self.system_prompt}\nUser Command: {text}",
            "stream": False,
            "options": {"temperature": 0.0, "num_ctx": 1024},
        }

        try:
            res = requests.post(self.ollama_url, json=payload, timeout=5.0)
            if res.status_code == 200:
                raw_json = res.json().get("response", "").strip()
                self._dispatch_tool_call(raw_json)
            else:
                self.get_logger().error(f"[ERROR] Ollama server responded with HTTP {res.status_code}")
        except Exception as e:
            self.get_logger().error(f"[EXCEPT] Ollama connection error: {e}")

    def _dispatch_tool_call(self, json_str: str):
        try:
            data = json.loads(json_str)
            tool = data.get("tool")

            if tool == "set_mode":
                mode_msg = String()
                mode_msg.data = str(data.get("mode", "rover")).upper()
                self.pub_mode_req.publish(mode_msg)
                self.get_logger().info(f"[EXEC] Mode Command: {mode_msg.data}")

            elif tool == "navigate_to":
                pose = PoseStamped()
                pose.header.frame_id = "map"
                pose.header.stamp = self.get_clock().now().to_msg()
                pose.pose.position.x = float(data.get("x", 0.0))
                pose.pose.position.y = float(data.get("y", 0.0))
                self.pub_goal.publish(pose)
                self.get_logger().info(f"[EXEC] Waypoint Set: X={pose.pose.position.x}, Y={pose.pose.position.y}")

            elif tool == "emergency_stop":
                stop_msg = Bool()
                stop_msg.data = True
                self.pub_estop.publish(stop_msg)
                self.get_logger().warn("[EXEC] EMERGENCY STOP INITIATED VIA VOICE COMMAND!")

        except json.JSONDecodeError:
            self.get_logger().error(f"[FAIL] Malformed JSON from Ollama: '{json_str}'")


def main(args=None):
    rclpy.init(args=args)
    node = OllamaVoiceNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Guardian X-1 Adaptive Persona & Dynamic Dialogue Node
------------------------------------------------------
Adapts conversational tone, vocabulary, and memory structures dynamically based
on identified user profiles and past interactions.
"""

import os
import json
import requests
import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class AdaptiveDialogueNode(Node):
    def __init__(self):
        super().__init__("adaptive_dialogue_node")

        self.declare_parameter("ollama_url", "http://localhost:11434/api/generate")
        self.declare_parameter("profiles_path", "config/user_profiles.json")

        self.ollama_url = self.get_parameter("ollama_url").get_parameter_value().string_value
        self.profiles_path = self.get_parameter("profiles_path").get_parameter_value().string_value

        self.active_person = "Operator"
        self.profiles = self._load_profiles()

        self.sub_person = self.create_subscription(String, "/ai/identified_person", self.person_callback, 10)
        self.sub_speech = self.create_subscription(String, "/audio/voice_command", self.voice_callback, 10)

        self.pub_audio = self.create_publisher(String, "/audio/tts_output", 10)

        self.get_logger().info("[INIT] Adaptive Persona Dialogue Node active.")

    def _load_profiles(self) -> dict:
        if os.path.exists(self.profiles_path):
            try:
                with open(self.profiles_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.get_logger().error(f"Error loading profile database: {e}")

        return {
            "Operator": {
                "communication_style": "Concise, technical, precise tactical tone.",
                "chat_history": []
            }
        }

    def _save_profiles(self):
        os.makedirs(os.path.dirname(self.profiles_path), exist_ok=True)
        with open(self.profiles_path, "w") as f:
            json.dump(self.profiles, f, indent=2)

    def person_callback(self, msg: String):
        person = msg.data.strip()
        if person and person != self.active_person:
            self.active_person = person
            self.get_logger().info(f"[PERSONA SWITCH] Dialogue engine targeting: '{self.active_person}'")

            if self.active_person not in self.profiles:
                self.profiles[self.active_person] = {
                    "communication_style": "Warm, natural, and highly adaptive.",
                    "chat_history": []
                }
                self._save_profiles()

    def voice_callback(self, msg: String):
        query = msg.data.strip()
        user_data = self.profiles.get(self.active_person, self.profiles["Operator"])
        style = user_data.get("communication_style", "Clear and direct.")
        history = user_data.get("chat_history", [])[-6:]

        prompt_context = (
                f"You are Guardian X-1 Assistant talking to target user '{self.active_person}'.\n"
                f"REQUIRED PERSONALITY STYLE: {style}\n"
                f"Recent Context:\n" + "\n".join(history)
        )

        payload = {
            "model": "llama3.2:1b",
            "prompt": f"{prompt_context}\nUser: {query}\nAI:",
            "stream": False,
            "options": {"temperature": 0.65}
        }

        try:
            res = requests.post(self.ollama_url, json=payload, timeout=8.0)
            if res.status_code == 200:
                answer = res.json().get("response", "").strip()

                user_data.setdefault("chat_history", []).extend([f"User: {query}", f"AI: {answer}"])
                self._save_profiles()

                reply_msg = String()
                reply_msg.data = answer
                self.pub_audio.publish(reply_msg)
                self.get_logger().info(f"[RESPONSE TO {self.active_person}] {answer}")

        except Exception as e:
            self.get_logger().error(f"[FAIL] Dialogue generation failed: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = AdaptiveDialogueNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
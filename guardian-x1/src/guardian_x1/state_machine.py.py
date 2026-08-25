#!/usr/bin/env python3
import logging
import time
from guardian_x1.memory_manager import CacheCleanerEngine
from guardian_x1.flight_bridge import FlightBridge
from guardian_x1.drone_controller import DroneController
from guardian_x1.rover_controller import RoverController
from ai_engine.inference_node import VisionAIEngine
from smart_glasses.glasses_node import SmartGlassesNode
from smartwatch.watch_node import SmartwatchNode
from voice_ai.voice_assistant import LocalVoiceAssistant

logging.basicConfig(level=logging.INFO, format="[MASTER_STATE] %(asctime)s - %(message)s")

class GuardianMasterSystem:
    def __init__(self):
        self.memory_mgr = CacheCleanerEngine()
        self.flight_bridge = FlightBridge()
        self.drone = DroneController()
        self.rover = RoverController()
        self.vision_ai = VisionAIEngine()
        self.glasses = SmartGlassesNode()
        self.watch = SmartwatchNode()
        self.voice_ai = LocalVoiceAssistant()
        self.state = "IDLE"

    def execute_tool_action(self, tool_call: dict):
        action = tool_call.get("tool")
        if action == "takeoff":
            alt = tool_call.get("altitude_m", 2.0)
            self.flight_bridge.arm()
            self.drone.takeoff(alt)
            self.state = "DRONE_FLIGHT"
        elif action == "land":
            self.drone.land()
            self.flight_bridge.disarm()
            self.state = "LANDED"
        elif action == "move":
            dx = tool_call.get("distance_m", 1.0)
            direction = tool_call.get("direction", "forward")
            dy = dx if direction == "right" else (-dx if direction == "left" else 0.0)
            dx = dx if direction == "forward" else (-dx if direction == "backward" else 0.0)
            self.drone.navigate_vector(dx, dy)
        elif action == "disarm":
            self.drone.disarm_motors()
            self.flight_bridge.disarm()
            self.rover.emergency_brake()
            self.state = "EMERGENCY_STOP"

    def run_step(self, user_command: str = None):
        self.memory_mgr.optimize_memory()
        if user_command:
            decision = self.voice_ai.query_local_llama(user_command)
            self.execute_tool_action(decision.get("tool_call", {}))

if __name__ == "__main__":
    sys_core = GuardianMasterSystem()
    sys_core.run_step("take off to 3 meters and hover")
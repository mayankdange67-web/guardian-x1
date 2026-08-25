#!/usr/bin/env python3
import json, time
class SmartGlassesNode:
    def build_hud_frame(self, battery: float):
        return json.dumps({"device": "smart_glasses", "hud": {"battery": f"{battery}%"}})
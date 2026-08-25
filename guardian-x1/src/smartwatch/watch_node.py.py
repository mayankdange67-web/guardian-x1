#!/usr/bin/env python3
import json, logging
class SmartwatchNode:
    def process_watch_event(self, raw_json: str):
        if "DISARM" in raw_json:
            logging.warning("Watch triggered DISARM")
        return {"status": "ACK"}
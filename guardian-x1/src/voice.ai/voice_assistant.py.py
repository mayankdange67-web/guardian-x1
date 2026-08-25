#!/usr/bin/env python3
import json, ollama, logging
class LocalVoiceAssistant:
    def query_local_llama(self, cmd: str) -> dict:
        try:
            res = ollama.chat(
                model="llama3.2:1b",
                messages=[
                    {"role": "system", "content": "Reply in JSON: {\"tool_call\": {\"tool\": \"takeoff\", \"altitude_m\": 3.0}}"},
                    {"role": "user", "content": cmd}
                ],
                format="json"
            )
            return json.loads(res['message']['content'])
        except Exception as e:
            return {"tool_call": {"tool": "none"}}
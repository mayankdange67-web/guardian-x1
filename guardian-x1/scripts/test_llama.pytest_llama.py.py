#!/usr/bin/env python3
"""
Guardian X-1 Local Ollama LLM Voice Benchmark
----------------------------------------------
Tests local `ollama/llama3.2:1b` model latency, context window processing,
and tool-calling JSON schema parsing for voice commands.
"""

import time
import json
import requests

OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

SYSTEM_PROMPT = """
You are Guardian X-1 Tactical AI. Convert voice commands into structured JSON tool calls.
Available tools:
1. set_mode(mode: "ground" | "aerial" | "hybrid")
2. navigate_to(x: float, y: float, speed: float)
3. emergency_stop()

Respond ONLY with valid JSON matching {"tool": "<name>", "params": {...}}.
"""

TEST_PROMPTS = [
    "Switch to aerial mode and move to coordinates 5.5, 12.0 at 1.5 meters per second.",
    "Stop immediately!",
    "Engage ground rover mode."
]


def test_ollama_benchmark():
    print("==========================================================")
    print(f"OLLAMA VOICE AI BENCHMARK: {MODEL_NAME}")
    print("==========================================================")

    for i, prompt in enumerate(TEST_PROMPTS, 1):
        payload = {
            "model": MODEL_NAME,
            "prompt": f"{SYSTEM_PROMPT}\nUser Command: {prompt}",
            "stream": False,
            "options": {
                "temperature": 0.0,
                "num_ctx": 2048
            }
        }

        start_time = time.perf_counter()
        try:
            response = requests.post(OLLAMA_ENDPOINT, json=payload, timeout=10.0)
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            if response.status_code == 200:
                result = response.json()
                raw_text = result.get("response", "").strip()
                eval_count = result.get("eval_count", 1)
                eval_duration_ns = result.get("eval_duration", 1)
                tok_per_sec = (eval_count / (eval_duration_ns / 1e9)) if eval_duration_ns > 0 else 0.0

                print(f"[TEST {i}] Command: '{prompt}'")
                print(f"         Latency  : {elapsed_ms:.1f} ms | Throughput: {tok_per_sec:.1f} tok/sec")
                print(f"         JSON Output: {raw_text}\n")
            else:
                print(f"[ERROR {i}] HTTP Status {response.status_code}: {response.text}")

        except Exception as e:
            print(f"[FAIL {i}] Could not reach Ollama at {OLLAMA_ENDPOINT}. Error: {e}")
            break


if __name__ == "__main__":
    test_ollama_benchmark()
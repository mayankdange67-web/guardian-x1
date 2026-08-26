#!/usr/bin/env python3
"""
Guardian X-1 Local Voice AI / Ollama Integration Test
Validates connectivity, model availability, and response latency for the local LLM endpoint.
"""

import os
import sys
import time
import requests
import yaml


def load_voice_config():
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'control_params.yaml')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            params = yaml.safe_load(f)
            return params.get('voice_ai', {})
    return {
        'model_name': 'llama3.2:3b',
        'ollama_url': 'http://localhost:11434'
    }


def main():
    print("=== Guardian X-1 Voice AI / Ollama Verification ===")
    config = load_voice_config()
    ollama_url = config.get('ollama_url', 'http://localhost:11434')
    model_name = config.get('model_name', 'llama3.2:3b')

    print(f"[CONFIG] Ollama Server URL: {ollama_url}")
    print(f"[CONFIG] Target Model Name: {model_name}")

    # 1. Health check endpoint
    try:
        resp = requests.get(f"{ollama_url}/api/tags", timeout=5)
        if resp.status_code == 200:
            models = [m['name'] for m in resp.json().get('models', [])]
            print(f"[HEALTH] Server Online. Installed Models: {models}")
            if model_name not in models and f"{model_name}:latest" not in models:
                print(f"[WARN] Model '{model_name}' not found in local Ollama repository.")
                print(f"[HINT] Run: ollama pull {model_name}")
        else:
            print(f"[ERROR] Server responded with status code {resp.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"[ERROR] Could not connect to Ollama at {ollama_url}. Is 'ollama serve' running?")
        sys.exit(1)

    # 2. Inference latency & response generation test
    prompt = "System check: State status, battery check, and current operating mode in 20 words or less."
    print(f"\n[TEST] Transmitting test prompt: '{prompt}'")
    
    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "max_tokens": 50
        }
    }

    start_time = time.time()
    try:
        response = requests.post(f"{ollama_url}/api/generate", json=payload, timeout=15)
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json().get('response', '').strip()
            print(f"[RESULT] Received in {elapsed:.2f} seconds:")
            print(f"         \"{result}\"")
            print("\n[SUCCESS] Local Voice AI LLM integration functional!")
        else:
            print(f"[ERROR] Inference request failed with status code {response.status_code}")
    except Exception as e:
        print(f"[ERROR] Inference failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

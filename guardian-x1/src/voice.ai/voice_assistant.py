#!/usr/bin/env python3
"""
Local LLM (Ollama) Voice Assistant Node for Guardian X-1.
"""

import requests
from .speech_to_text import SpeechToText
from .text_to_speech import TextToSpeech

class VoiceAssistant:
    def __init__(self, model_name: str = "llama3.2:3b", ollama_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.ollama_url = ollama_url
        self.stt = SpeechToText()
        self.tts = TextToSpeech()

    def process_command(self, user_audio_bytes: bytes) -> str:
        query = self.stt.transcribe(user_audio_bytes)
        payload = {
            "model": self.model_name,
            "prompt": f"You are Guardian X-1 Voice AI. Respond to operator: {query}",
            "stream": False
        }
        try:
            resp = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=10)
            if resp.status_code == 200:
                answer = resp.json().get('response', '')
                self.tts.speak(answer)
                return answer
        except Exception as e:
            print(f"[VOICE AI ERROR] {e}")
        return "Voice processing error."

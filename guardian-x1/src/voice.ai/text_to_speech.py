#!/usr/bin/env python3
"""
Text-to-Speech Synthesizer Wrapper for Voice AI pipeline.
"""

class TextToSpeech:
    def __init__(self, voice_id: str = "en_us_male"):
        self.voice_id = voice_id
        print(f"[TTS] Initialized TextToSpeech synthesizer with voice '{self.voice_id}'.")

    def speak(self, text: str):
        print(f"[TTS SPEAK]: \"{text}\"")

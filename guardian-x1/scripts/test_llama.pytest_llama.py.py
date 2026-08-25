#!/usr/bin/env python3
import ollama, json
response = ollama.chat(
    model="llama3.2:1b",
    messages=[
        {"role": "system", "content": "Respond in JSON: {\"tool\": \"takeoff\", \"altitude_m\": float}"},
        {"role": "user", "content": "Takeoff to 3 meters"}
    ],
    format="json"
)
print(response['message']['content'])
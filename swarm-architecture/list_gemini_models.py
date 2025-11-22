#!/usr/bin/env python3
import os
import google.generativeai as genai

api_key = "AIzaSyB3yQZSAlgN_36NwOQMp7rf0f1f75pPmfk"
genai.configure(api_key=api_key)

print("Available Gemini models:")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")
        print(f"    Display: {model.display_name}")
        print(f"    Methods: {', '.join(model.supported_generation_methods)}")
        print()

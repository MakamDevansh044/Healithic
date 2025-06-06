# === File: modules/mood.py ===
from deepface import DeepFace
import numpy as np
import cv2

class MoodDetector:
    def __init__(self):
        pass

    def analyze(self, frame):
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            result = DeepFace.analyze(img_path=rgb_frame, actions=['emotion'], enforce_detection=False)
            if isinstance(result, list):
                dominant_emotion = result[0]['dominant_emotion']
            else:
                dominant_emotion = result['dominant_emotion']
            return dominant_emotion
        except Exception as e:
            print(f"[Mood Detection Error] {e}")
            return "Unknown"

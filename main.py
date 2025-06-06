# === File: main.py ===
import cv2
import threading
import time
import json
import os
import sys
from datetime import datetime
from PIL import Image
import pystray
from queue import Queue

from modules.vision import FaceEyeDetector
from modules.mood import MoodDetector
from modules.notifier import Notifier
from modules.activity import ActivityMonitor
from ui.dashboard import HealithicDashboard
import tkinter as tk

CONFIG_PATH = "config/Healithic_config.json"

default_config = {
    "water_interval_minutes": 45,
    "eye_exercise_interval_minutes": 30,
    "walk_interval_minutes": 60,
    "meal_interval_hours": 4
}

if not os.path.exists(CONFIG_PATH):
    os.makedirs("config", exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(default_config, f, indent=4)

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def create_image():
    try:
        return Image.open("assets/icon.png")
    except Exception as e:
        print(f"[⚠️] Tray icon not loaded: {e}")
        return Image.new('RGB', (64, 64), 'gray')

def run_background(update_queue):
    config = load_config()
    detector = FaceEyeDetector()
    mood = MoodDetector()
    monitor = ActivityMonitor()
    notifier = Notifier(config)
    monitor.start_listening()

    last_water_notify = None
    last_meal_notify = None
    last_walk_notify = None
    last_eye_notify = None

    def task():
        nonlocal last_water_notify, last_meal_notify, last_walk_notify, last_eye_notify

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[ERROR] Webcam not available.")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            face_count, eyes_detected, blink_ratio = detector.detect(frame)
            emotion = mood.analyze(frame)
            idle_time = monitor.get_idle_duration()

            notifier.check_and_notify(idle_time, face_count, eyes_detected, blink_ratio, emotion)

            update = {
                "faces": face_count,
                "eyes": eyes_detected,
                "mood": emotion,
                "blink_ratio": blink_ratio,
                "water_time": notifier.last_water_time,
                "meal_time": notifier.last_meal_time,
                "walk_time": notifier.last_walk_time,
                "eye_exercise_time": notifier.last_eye_exercise_time,
            }

            update_queue.put(update)
            time.sleep(30)

        cap.release()

    threading.Thread(target=task, daemon=True).start()

def start_dashboard():
    update_queue = Queue()

    bg_thread = threading.Thread(target=run_background, args=(update_queue,), daemon=True)
    bg_thread.start()

    app = tk.Tk()
    dashboard_instance = HealithicDashboard(update_queue, master=app)
    dashboard_instance.mainloop()

def setup_tray():
    def on_quit(icon, item):
        icon.stop()
        os._exit(0)

    def on_open_dashboard(icon, item):
        threading.Thread(target=start_dashboard, daemon=True).start()

    icon = pystray.Icon("Healithic", create_image(), "Healithic", menu=pystray.Menu(
        pystray.MenuItem("Open Dashboard", on_open_dashboard),
        pystray.MenuItem("Quit", on_quit)
    ))
    icon.run()

if __name__ == "__main__":
    setup_tray()

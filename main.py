# === File: main.py ===
from modules.vision import FaceEyeDetector
from modules.mood import MoodDetector
from modules.notifier import Notifier
from modules.activity import ActivityMonitor
from ui.dashboard import launch_dashboard

import cv2
import threading
import time
from datetime import datetime
import json
import os
import sys
import pystray
from PIL import Image
import queue

CONFIG_PATH = "config/wellzen_config.json"
gui_queue = queue.Queue()

# Default config initialization
if not os.path.exists(CONFIG_PATH):
    default_config = {
        "water_interval_minutes": 45,
        "eye_exercise_interval_minutes": 30,
        "walk_interval_minutes": 60,
        "meal_interval_hours": 4
    }
    os.makedirs("config", exist_ok=True)
    with open(CONFIG_PATH, 'w') as f:
        json.dump(default_config, f, indent=4)

# Load config
def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

# Tray icon loader
def create_image():
    try:
        return Image.open("assets/icon.png")
    except Exception as e:
        print(f"⚠️ Failed to load tray icon: {e}")
        return Image.new('RGB', (64, 64), 'gray')

# Background thread for monitoring
def run_background():
    config = load_config()
    detector = FaceEyeDetector()
    mood = MoodDetector()
    monitor = ActivityMonitor()
    notifier = Notifier(config)
    monitor.start_listening()

    def task():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Webcam error")
            sys.exit()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            face_count, eyes_detected, blink_ratio = detector.detect(frame)
            emotion = mood.analyze(frame)
            idle_time = monitor.get_idle_duration()
            notifier.check_and_notify(idle_time, face_count, eyes_detected, blink_ratio, emotion)

            time.sleep(30)

        cap.release()

    threading.Thread(target=task, daemon=True).start()

# Tray setup with dashboard trigger
def setup_tray():
    def on_quit(icon, item):
        icon.stop()
        sys.exit()

    def open_dashboard(icon, item):
        gui_queue.put(launch_dashboard)

    icon = pystray.Icon("WellZen", create_image(), "WellZen", menu=pystray.Menu(
        pystray.MenuItem("Open Dashboard", open_dashboard),
        pystray.MenuItem("Quit", on_quit)
    ))
    icon.run()

# GUI loop that runs dashboard safely on main thread
if __name__ == "__main__":
    run_background()

    tray_thread = threading.Thread(target=setup_tray)
    tray_thread.daemon = True
    tray_thread.start()

    # Main thread waits for GUI-related calls
    while True:
        try:
            gui_func = gui_queue.get(timeout=1)
            gui_func()
        except queue.Empty:
            continue

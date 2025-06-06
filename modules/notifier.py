# === File: modules/notifier.py ===
from datetime import datetime, timedelta
from plyer import notification  
import time
import os
from playsound import playsound
import threading


class Notifier:
    def __init__(self, config):
        self.config = config
        self.last_water_time = None
        self.last_eye_exercise_time = None
        self.last_walk_time = None
        self.last_meal_time = None
        self.last_emotion = None
        self.buzzer_enabled = True
        self.last_buzzer_time = None

    def notify(self, message, category):
        timestamp = datetime.now().strftime("%I:%M:%S %p")
        formatted_message = f"{timestamp} - {message}"
        print(f"[NOTIFY] {category}: {formatted_message}")

        # --- System notification (toast) ---
        try:
            notification.notify(
                title=f"WellZen - {category}",
                message=message,
                app_name="WellZen",
                timeout=5  # seconds
            )
        except Exception as e:
            print(f"[WARN] System notification failed: {e}")

    def play_buzzer(self):
        try:
            buzzer_path = os.path.abspath(os.path.join("assets", "buzzer.wav"))
            buzzer_path = buzzer_path.replace("\\", "/")
            # buzzer_path = os.path.join("assets", "buzzer.wav")
            threading.Thread(target=playsound, args=(buzzer_path,), daemon=True).start()
        except Exception as e:
            print(f"[ERROR] Failed to play buzzer: {e}")

    def check_and_notify(self, idle_time, face_count, eyes_detected, blink_ratio, emotion):
        now = datetime.now()

        # --- Hydration reminder ---
        if (self.last_water_time is None or
            now - self.last_water_time >= timedelta(minutes=self.config["water_interval_minutes"])):
            self.notify("💧 Drink some water!", "Hydration Check")
            self.play_buzzer()
            self.last_water_time = now

        # --- Eye exercise reminder ---
        if (self.last_eye_exercise_time is None or
            now - self.last_eye_exercise_time >= timedelta(minutes=self.config["eye_exercise_interval_minutes"])):
            self.notify("👀 Look away from your screen and roll your eyes for a few seconds.", "Eye Exercise")
            self.play_buzzer()
            self.last_eye_exercise_time = now

        # --- Walk reminder ---
        if (self.last_walk_time is None or
            now - self.last_walk_time >= timedelta(minutes=self.config["walk_interval_minutes"])):
            if idle_time > self.config["walk_interval_minutes"] * 60:
                self.notify("🚶‍♂️ You've been idle too long. Take a short walk.", "Idle Alert")
                self.play_buzzer()
                self.last_walk_time = now

        # --- Meal reminder ---
        if (self.last_meal_time is None or
            now - self.last_meal_time >= timedelta(hours=self.config["meal_interval_hours"])):
            self.notify("🍽 It's time for a healthy meal.", "Meal Reminder")
            self.play_buzzer()
            self.last_meal_time = now

        # --- Mood detection notification ---
        if emotion and emotion != self.last_emotion:
            if emotion in ["sad", "angry"] and self.buzzer_enabled:
                if self.last_buzzer_time is None or now - self.last_buzzer_time > timedelta(minutes=3):
                    self.notify(f"😠 You look {emotion}. Wake up or take a breath!", "Mood Buzzer")
                    self.play_buzzer()
                    self.last_buzzer_time = now
            self.last_emotion = emotion

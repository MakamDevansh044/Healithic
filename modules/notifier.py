# === File: modules/notifier.py ===
from datetime import datetime, timedelta
from plyer import notification

class Notifier:
    def __init__(self, config):
        self.config = config
        self.last_water = datetime.min
        self.last_eye = datetime.min
        self.last_walk = datetime.min
        self.last_meal = datetime.min
        self.last_mood_check = datetime.min

    def notify(self, title, message):
        print(f"[NOTIFY] {title}: {message}")
        notification.notify(title=title, message=message, timeout=10)

    def check_and_notify(self, idle_seconds, face_count, eyes_detected, blink_ratio, emotion):
        now = datetime.now()

        # Water reminder
        if (now - self.last_water) > timedelta(minutes=self.config["water_interval_minutes"]):
            self.notify("Hydration Check", "💧 Drink some water!")
            self.last_water = now

        # Eye exercise reminder
        if (now - self.last_eye) > timedelta(minutes=self.config["eye_exercise_interval_minutes"]):
            if blink_ratio is not None and blink_ratio < 0.21:
                self.notify("Eye Strain Alert", "👁 Do an eye exercise (20-20-20 rule)!")
                self.last_eye = now

        # Walk reminder
        if idle_seconds > self.config["walk_interval_minutes"] * 60:
            if (now - self.last_walk) > timedelta(minutes=self.config["walk_interval_minutes"]):
                self.notify("Movement Needed", "🧍‍♂️ Take a short walk or stretch your body!")
                self.last_walk = now

        # Meal reminder
        if (now - self.last_meal) > timedelta(hours=self.config["meal_interval_hours"]):
            self.notify("Meal Reminder", "🍽 It's time for a healthy meal.")
            self.last_meal = now

        # Mood detection based reminder
        if emotion in ["sad", "angry", "tired"] and (now - self.last_mood_check).seconds > 1800:
            self.notify("Mood Booster", f"😊 You look {emotion}. Take a short break, breathe, or listen to music.")
            self.last_mood_check = now

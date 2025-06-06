# === File: modules/activity.py ===
from datetime import datetime
import threading
from pynput import mouse, keyboard

class ActivityMonitor:
    def __init__(self):
        self.last_activity = datetime.now()
        self.lock = threading.Lock()

    def update_activity(self, event=None):
        with self.lock:
            self.last_activity = datetime.now()

    def get_idle_duration(self):
        with self.lock:
            return (datetime.now() - self.last_activity).total_seconds()

    def start_listening(self):
        mouse.Listener(
            on_move=self.update_activity,
            on_click=self.update_activity,
            on_scroll=self.update_activity
        ).start()

        keyboard.Listener(
            on_press=self.update_activity,
            on_release=self.update_activity
        ).start()

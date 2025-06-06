# === File: ui/dashboard.py ===
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json
import os

CONFIG_PATH = "config/wellzen_config.json"

class WellZenDashboard(tk.Frame):
    def __init__(self, update_queue, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("WellZen Health Dashboard")
        self.pack(fill="both", expand=True)
        self.update_queue = update_queue

        self.current_mood = tk.StringVar(value="Unknown")
        self.blink_ratio = tk.DoubleVar(value=0.0)
        self.face_count = tk.IntVar(value=0)
        self.eye_status = tk.StringVar(value="Unknown")
        self.buzzer_enabled = tk.BooleanVar(value=True)

        self.last_water_time = tk.StringVar(value="N/A")
        self.last_meal_time = tk.StringVar(value="N/A")
        self.last_walk_time = tk.StringVar(value="N/A")
        self.last_eye_time = tk.StringVar(value="N/A")
        self.notification_text = tk.StringVar(value="No notifications yet.")

        self.config_data = self.load_config()

        self.create_widgets()
        self.master.after(1000, self.process_updates)

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self.config_data, f, indent=4)

    def create_widgets(self):
        label_font = ("Segoe UI", 12)

        stats_frame = ttk.LabelFrame(self, text="Live Stats")
        stats_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(stats_frame, text="Current Mood:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(stats_frame, textvariable=self.current_mood).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(stats_frame, text="Blink Ratio:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(stats_frame, textvariable=self.blink_ratio).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(stats_frame, text="Faces Detected:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(stats_frame, textvariable=self.face_count).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        reminder_frame = ttk.LabelFrame(self, text="Last Reminders")
        reminder_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(reminder_frame, text="Water:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(reminder_frame, textvariable=self.last_water_time).grid(row=0, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(reminder_frame, text="Meal:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(reminder_frame, textvariable=self.last_meal_time).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(reminder_frame, text="Walk:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(reminder_frame, textvariable=self.last_walk_time).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(reminder_frame, text="Eye Exercise:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        ttk.Label(reminder_frame, textvariable=self.last_eye_time).grid(row=3, column=1, sticky="w", padx=5, pady=5)

        config_frame = ttk.LabelFrame(self, text="Health Reminder Settings")
        config_frame.pack(fill="x", padx=10, pady=10)

        self.config_vars = {}
        row = 0
        for key, label in [
            ("water_interval_minutes", "Water Reminder (min):"),
            ("eye_exercise_interval_minutes", "Eye Exercise Reminder (min):"),
            ("walk_interval_minutes", "Walk Reminder (min):"),
            ("meal_interval_hours", "Meal Reminder (hrs):")
        ]:
            ttk.Label(config_frame, text=label).grid(row=row, column=0, sticky="w", padx=5, pady=5)
            var = tk.IntVar(value=self.config_data.get(key, 0))
            self.config_vars[key] = var
            ttk.Entry(config_frame, textvariable=var).grid(row=row, column=1, padx=5, pady=5)
            row += 1

        ttk.Button(config_frame, text="Save Settings", command=self.update_config).grid(row=row, column=0, columnspan=2, pady=10)

        buzzer_frame = ttk.LabelFrame(self, text="Buzzer Alerts")
        buzzer_frame.pack(fill="x", padx=10, pady=10)
        ttk.Checkbutton(buzzer_frame, text="Enable Buzzer Alerts", variable=self.buzzer_enabled).pack(anchor="w", padx=5, pady=5)

        notify_frame = ttk.LabelFrame(self, text="Recent Notification")
        notify_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(notify_frame, textvariable=self.notification_text, wraplength=400).pack(padx=5, pady=5)

    def update_config(self):
        for key, var in self.config_vars.items():
            self.config_data[key] = var.get()
        self.save_config()

    def process_updates(self):
        try:
            while not self.update_queue.empty():
                update = self.update_queue.get()
                self.apply_update(update)
        except Exception as e:
            print(f"[Dashboard] Update error: {e}")
        self.master.after(2000, self.process_updates)

    def apply_update(self, update):
        if not isinstance(update, dict):
            return

        self.current_mood.set(update.get("mood", "Unknown"))
        self.blink_ratio.set(round(update.get("blink_ratio", 0.0), 2))
        self.face_count.set(update.get("faces", 0))
        self.eye_status.set("Open" if update.get("eyes", False) else "Closed")

        for k, var in [
            ("water_time", self.last_water_time),
            ("meal_time", self.last_meal_time),
            ("walk_time", self.last_walk_time),
            ("eye_exercise_time", self.last_eye_time)
        ]:
            ts = update.get(k)
            if ts:
                if isinstance(ts, datetime):
                    var.set(ts.strftime("%I:%M:%S %p"))
                else:
                    var.set(datetime.fromtimestamp(ts).strftime("%I:%M:%S %p"))
            else:
                var.set("N/A")


        # Update buzzer flag in config (optional sync)
        self.config_data["buzzer_enabled"] = self.buzzer_enabled.get()
        self.save_config()

        notification_msg = update.get("notification")
        if notification_msg:
            self.notification_text.set(notification_msg)


    def is_buzzer_enabled(self):
        return self.buzzer_enabled.get()

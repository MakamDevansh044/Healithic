# === File: ui/dashboard.py ===
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import json
import os

CONFIG_PATH = "config/wellzen_config.json"

class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WellZen Dashboard")
        self.geometry("350x400")
        self.resizable(False, False)

        self.config = self.load_config()

        self.create_widgets()

    def load_config(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                return json.load(f)
        else:
            default_config = {
                "water_interval_minutes": 45,
                "eye_exercise_interval_minutes": 30,
                "walk_interval_minutes": 60,
                "meal_interval_hours": 4,
                "notifications_enabled": True,
                "webcam_enabled": True
            }
            os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
            with open(CONFIG_PATH, "w") as f:
                json.dump(default_config, f, indent=4)
            return default_config

    def save_config(self):
        with open(CONFIG_PATH, "w") as f:
            json.dump(self.config, f, indent=4)

    def create_widgets(self):
        ttk.Label(self, text="WellZen Preferences", font=("Arial", 14, "bold")).pack(pady=10)

        # Water interval
        ttk.Label(self, text="Water reminder interval (min):").pack(anchor="w", padx=20)
        self.water_var = tk.IntVar(value=self.config.get("water_interval_minutes", 45))
        ttk.Spinbox(self, from_=15, to=180, increment=5, textvariable=self.water_var).pack(padx=20, pady=5, fill="x")

        # Eye exercise interval
        ttk.Label(self, text="Eye exercise interval (min):").pack(anchor="w", padx=20)
        self.eye_var = tk.IntVar(value=self.config.get("eye_exercise_interval_minutes", 30))
        ttk.Spinbox(self, from_=10, to=120, increment=5, textvariable=self.eye_var).pack(padx=20, pady=5, fill="x")

        # Walk interval
        ttk.Label(self, text="Walk reminder interval (min):").pack(anchor="w", padx=20)
        self.walk_var = tk.IntVar(value=self.config.get("walk_interval_minutes", 60))
        ttk.Spinbox(self, from_=20, to=180, increment=10, textvariable=self.walk_var).pack(padx=20, pady=5, fill="x")

        # Meal interval
        ttk.Label(self, text="Meal reminder interval (hours):").pack(anchor="w", padx=20)
        self.meal_var = tk.IntVar(value=self.config.get("meal_interval_hours", 4))
        ttk.Spinbox(self, from_=1, to=8, increment=1, textvariable=self.meal_var).pack(padx=20, pady=5, fill="x")

        # Webcam enabled checkbox
        self.webcam_var = tk.BooleanVar(value=self.config.get("webcam_enabled", True))
        ttk.Checkbutton(self, text="Enable Webcam Monitoring", variable=self.webcam_var).pack(pady=5)

        # Notifications enabled checkbox
        self.notify_var = tk.BooleanVar(value=self.config.get("notifications_enabled", True))
        ttk.Checkbutton(self, text="Enable Notifications", variable=self.notify_var).pack(pady=5)

        # Save button
        ttk.Button(self, text="Save Preferences", command=self.on_save).pack(pady=15)

        # Status label
        self.status_label = ttk.Label(self, text="", foreground="green")
        self.status_label.pack()

    def on_save(self):
        self.config["water_interval_minutes"] = self.water_var.get()
        self.config["eye_exercise_interval_minutes"] = self.eye_var.get()
        self.config["walk_interval_minutes"] = self.walk_var.get()
        self.config["meal_interval_hours"] = self.meal_var.get()
        self.config["webcam_enabled"] = self.webcam_var.get()
        self.config["notifications_enabled"] = self.notify_var.get()

        self.save_config()
        self.status_label.config(text="Preferences saved!")

# ✅ Exportable function for main.py
def launch_dashboard():
    app = Dashboard()
    app.mainloop()



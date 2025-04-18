import psutil
import os
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox  # ✅ Import for alert

def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read()) / 1000.0
        return round(temp, 2)
    except:
        return "N/A"

def get_gpu_temperature():
    try:
        output = os.popen("vcgencmd measure_temp").readline()
        temp = output.replace("temp=", "").replace("'C\n", "")
        return float(temp)
    except:
        return "N/A"

def get_power_status():
    try:
        result = os.popen("vcgencmd get_throttled").read().strip()
        return result
    except:
        return "Unavailable"

def decode_throttled(hex_str):
    try:
        flags = int(hex_str.split('=')[-1], 16)
        reasons = []
        if flags & 0x1:
            reasons.append("Under-voltage")
        if flags & 0x2:
            reasons.append("Freq capped")
        if flags & 0x4:
            reasons.append("Throttled")
        if flags & 0x8:
            reasons.append("Temp limit")
        return ", ".join(reasons) if reasons else "Normal"
    except:
        return "N/A"

def get_cpu_freq():
    try:
        freq = psutil.cpu_freq()
        return f"{freq.current:.0f}/{freq.max:.0f} MHz"
    except:
        return "N/A"

def get_temp_status(temp):
    if temp == "N/A":
        return "❓ Unknown"
    if temp < 60:
        return "✅ Cool"
    elif 60 <= temp < 70:
        return "🟡 Warm"
    elif 70 <= temp < 80:
        return "🟠 Hot"
    else:
        return "🔴 Throttling"

class SystemMonitorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Raspberry Pi Monitor")
        self.root.geometry("260x240")
        self.root.resizable(False, False)

        self.style = tb.Style("superhero")

        self.frame = tb.Frame(root, padding=10)
        self.frame.pack(fill=BOTH, expand=YES)

        title = tb.Label(self.frame, text="Pi Monitor Dashboard", font=("Segoe UI", 12, "bold"), bootstyle="info")
        title.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        self.labels = {}

        fields = [
            ("CPU Usage", 1, 0), ("RAM Usage", 1, 1),
            ("CPU Temp", 2, 0), ("GPU Temp", 2, 1),
            ("Frequency", 3, 0), ("Power", 3, 1),
            ("Status", 4, 0)
        ]

        for label, row, col in fields:
            tb.Label(self.frame, text=label + ":", font=("Segoe UI", 9, "bold")).grid(row=row*2, column=col, sticky="w", padx=5, pady=1)
            self.labels[label] = tb.Label(self.frame, text="Loading...", font=("Segoe UI", 9), bootstyle="secondary")
            self.labels[label].grid(row=row*2 + 1, column=col, sticky="w", padx=5, pady=1)

        self.alert_shown = False  # ✅ Flag to prevent multiple popups
        self.update_data()

    def update_data(self):
        cpu_percent = psutil.cpu_percent()
        ram_percent = psutil.virtual_memory().percent
        cpu_temp = get_cpu_temperature()
        gpu_temp = get_gpu_temperature()
        cpu_freq = get_cpu_freq()
        power_raw = get_power_status()
        power_status = decode_throttled(power_raw)
        temp_status = get_temp_status(cpu_temp)

        self.labels["CPU Usage"].config(text=f"{cpu_percent}%", bootstyle=self.style_for_percent(cpu_percent))
        self.labels["RAM Usage"].config(text=f"{ram_percent}%", bootstyle=self.style_for_percent(ram_percent))
        self.labels["CPU Temp"].config(text=f"{cpu_temp} °C", bootstyle=self.style_for_temp(cpu_temp))
        self.labels["GPU Temp"].config(text=f"{gpu_temp} °C", bootstyle=self.style_for_temp(gpu_temp))
        self.labels["Frequency"].config(text=cpu_freq, bootstyle="warning")
        self.labels["Power"].config(text=power_status, bootstyle="warning" if "Throttled" in power_status else "success")
        self.labels["Status"].config(text=temp_status, bootstyle=self.style_for_status(temp_status))

        # ✅ Temperature alert logic
        if isinstance(cpu_temp, (int, float)) and cpu_temp > 60:
            if not self.alert_shown:
                self.alert_shown = True
                messagebox.showwarning("⚠️ High Temperature Warning", f"CPU temperature is {cpu_temp}°C!\nPlease check cooling.")
        else:
            self.alert_shown = False  # Reset alert if temp goes down

        self.root.after(1000, self.update_data)
    
    def style_for_status(self, status_text):
        if "Cool" in status_text:
            return "success"
        elif "Warm" in status_text:
            return "danger"
        elif "Hot" in status_text:
            return "warning"
        elif "Throttling" in status_text:
            return "danger"
        else:
            return "secondary"

    def style_for_percent(self, value):
        if value < 50:
            return "success"
        elif value < 75:
            return "warning"
        else:
            return "danger"

    def style_for_temp(self, temp):
        if temp == "N/A":
            return "secondary"
        elif temp < 60:
            return "success"
        elif temp < 70:
            return "warning"
        elif temp < 80:
            return "danger"
        else:
            return "danger"

def run_gui():
    root = tb.Window(themename="superhero")
    app = SystemMonitorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()

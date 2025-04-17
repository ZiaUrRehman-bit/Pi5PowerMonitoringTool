import psutil
import os
import tkinter as tk
import ttkbootstrap as tb
from ttkbootstrap.constants import *

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
        return "Unknown"
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
        self.root.title("Pi Monitor")
        self.root.geometry("260x220")
        self.root.resizable(False, False)

        self.style = tb.Style("superhero")  # modern dark theme

        self.frame = tb.Frame(root, padding=10)
        self.frame.pack(fill=BOTH, expand=YES)

        self.labels = {}

        # 2-column layout using grid
        fields = [
            ("CPU Usage", 0, 0), ("RAM Usage", 0, 1),
            ("CPU Temp", 1, 0), ("GPU Temp", 1, 1),
            ("Frequency", 2, 0), ("Power", 2, 1),
            ("Status", 3, 0)
        ]

        for label, row, col in fields:
            tb.Label(self.frame, text=label + ":", font=("Segoe UI", 9, "bold")).grid(row=row*2, column=col, sticky="w", padx=5, pady=2)
            self.labels[label] = tb.Label(self.frame, text="Loading...", font=("Segoe UI", 9))
            self.labels[label].grid(row=row*2 + 1, column=col, sticky="w", padx=5, pady=2)

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

        self.labels["CPU Usage"].config(text=f"{cpu_percent}%")
        self.labels["RAM Usage"].config(text=f"{ram_percent}%")
        self.labels["CPU Temp"].config(text=f"{cpu_temp} °C")
        self.labels["GPU Temp"].config(text=f"{gpu_temp} °C")
        self.labels["Frequency"].config(text=cpu_freq)
        self.labels["Power"].config(text=power_status)
        self.labels["Status"].config(text=temp_status)

        self.root.after(1000, self.update_data)

def run_gui():
    root = tb.Window(themename="superhero")
    app = SystemMonitorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    run_gui()

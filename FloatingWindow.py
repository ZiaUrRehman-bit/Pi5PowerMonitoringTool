import tkinter as tk
from tkinter import Label
import os
import psutil

def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read()) / 1000.0
        return round(temp, 1)
    except:
        return "N/A"

def get_gpu_temperature():
    try:
        output = os.popen("vcgencmd measure_temp").readline()
        temp = output.replace("temp=", "").replace("'C\n", "")
        return float(temp)
    except:
        return "N/A"

def get_temp_status(temp):
    if temp == "N/A":
        return "❓ Unknown"
    elif temp < 60:
        return "✅ Cool"
    elif temp < 70:
        return "🟡 Warm"
    elif temp < 80:
        return "🟠 Hot"
    else:
        return "🔴 Throttling"

def update_label():
    cpu_temp = get_cpu_temperature()
    gpu_temp = get_gpu_temperature()
    status = get_temp_status(cpu_temp)

    text = f"CPU: {cpu_temp}°C\nGPU: {gpu_temp}°C\nStatus: {status}"
    label.config(text=text)
    root.after(2000, update_label)  # Update every 2 seconds

root = tk.Tk()
root.overrideredirect(True)  # No border
root.attributes("-topmost", True)  # Stay on top
root.geometry("+1200+20")  # Position (adjust for your screen)

label = Label(root, font=("Segoe UI", 10), justify="left", bg="#1e1e1e", fg="white", padx=10, pady=5)
label.pack()

update_label()
root.mainloop()

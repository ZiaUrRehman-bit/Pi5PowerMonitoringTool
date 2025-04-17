import psutil
import os
import time

def get_cpu_temperature():
    try:
        # Reads from thermal zone for RPi
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read()) / 1000.0
        return round(temp, 2)
    except FileNotFoundError:
        return "N/A"

def get_power_status():
    try:
        # Might work depending on power config (USB PD status etc.)
        result = os.popen("vcgencmd get_throttled").read().strip()
        return result
    except:
        return "Unavailable"

def monitor_system():
    print(f"{'Time':<8} {'CPU %':<7} {'RAM %':<7} {'Temp (°C)':<10} {'Power':<20}")
    print("-"*60)
    while True:
        cpu_percent = psutil.cpu_percent(interval=1)
        ram_percent = psutil.virtual_memory().percent
        temp = get_cpu_temperature()
        power = get_power_status()

        current_time = time.strftime("%H:%M:%S")
        print(f"{current_time:<8} {cpu_percent:<7} {ram_percent:<7} {temp:<10} {power:<20}")
        time.sleep(1)

if __name__ == "__main__":
    monitor_system()

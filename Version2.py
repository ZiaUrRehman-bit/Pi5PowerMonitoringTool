import psutil
import os
import time

def get_cpu_temperature():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp = int(f.read()) / 1000.0
        return round(temp, 2)
    except FileNotFoundError:
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

def monitor_system():
    print(f"{'Time':<8} {'CPU %':<7} {'RAM %':<7} {'CPU °C':<8} {'GPU °C':<8} {'Freq':<12} {'Power Status'}")
    print("-"*80)
    while True:
        cpu_percent = psutil.cpu_percent(interval=1)
        ram_percent = psutil.virtual_memory().percent
        cpu_temp = get_cpu_temperature()
        gpu_temp = get_gpu_temperature()
        cpu_freq = get_cpu_freq()
        power_raw = get_power_status()
        power_status = decode_throttled(power_raw)
        current_time = time.strftime("%H:%M:%S")

        print(f"{current_time:<8} {cpu_percent:<7} {ram_percent:<7} {cpu_temp:<8} {gpu_temp:<8} {cpu_freq:<12} {power_status}")
        time.sleep(1)

if __name__ == "__main__":
    monitor_system()

# Importing Libraries
from serial import Serial
import time
import struct
import psutil
import subprocess
import json
import re


maxGpuMem = 0
arduinoPort = "/dev/cu.usbserial-110"
metricsSource = "macmon"
minGpuTemp = 10
lastGpuTemp = 0

arduino = Serial(port=arduinoPort, baudrate=9600, timeout=1)
while True:
    gpuMemPercentUsage = 0

    if metricsSource == "macmon":
        macmonInfo = subprocess.run(
            ["macmon", "pipe", "-s", "1"],
            capture_output=True,
            text=True,
            timeout=4,
            check=True,
        ).stdout.splitlines()[0]

        metrics = json.loads(macmonInfo)
        gpuUsage = int(float(metrics["gpu_usage"][1]) * 100)
        gpuFreq = int(float(metrics["gpu_usage"][0]))
        gpuPower = int(float(metrics["gpu_power"]) * 1000)

        cpuTemp = int(float(metrics["temp"]["cpu_temp_avg"]))
        gpuTemp = int(float(metrics["temp"]["gpu_temp_avg"]))
        
        # sometimes when gpu sleeps macmon stops and uses default value = 2 degrees
        if gpuTemp < minGpuTemp:
            gpuTemp = lastGpuTemp
        else:
            lastGpuTemp = gpuTemp
    elif metricsSource == "powermetrics":
        gpuInfo = subprocess.run(
            ["sudo", "-n", "powermetrics", "-n", "1", "-i", "1000", "--samplers", "gpu_power"],
            capture_output=True,
            text=True,
            timeout=3,
            check=True,
        ).stdout

        gpuUsage = int(float(re.search(r"GPU HW active residency:\s+([0-9.]+)%", gpuInfo).group(1)))
        gpuFreq = int(re.search(r"GPU HW active frequency:\s+([0-9]+)\s+MHz", gpuInfo).group(1))
        gpuPower = int(re.search(r"GPU Power:\s+([0-9]+)\s+mW", gpuInfo).group(1))

        tempInfo = subprocess.run(
            ["sudo", "-n", "powermetrics", "-n", "1", "-i", "1000", "--samplers", "smc"],
            capture_output=True,
            text=True,
            timeout=3,
            check=True,
        ).stdout

        cpuTemp = int(float(re.search(r"CPU die temperature:\s+([0-9.]+)\s*C", tempInfo).group(1)))
        gpuTemp = int(float(re.search(r"GPU die temperature:\s+([0-9.]+)\s*C", tempInfo).group(1)))
    else:
        raise ValueError('metricsSource must be "macmon" or "powermetrics"')

    ram = int(psutil.virtual_memory().percent)

    cpu = int(psutil.cpu_percent())

    swap = int(psutil.swap_memory().percent)

    obj_Disk = psutil.disk_usage('/')
    diskusage = int(obj_Disk.percent)

    print(f'cpu: {cpu}%, gpu: {gpuUsage}%, gpuFreq: {gpuFreq}MHz, gpuPower: {gpuPower}mW, gpuMemPercentUsage: {gpuMemPercentUsage}%, ram: {ram}%, cpuTemp: {cpuTemp}, gpuTemp: {gpuTemp}, swap: {swap}%, diskUsage: {diskusage}%')

    arduino.write(struct.pack('BBBBBBBB', cpu, gpuUsage, gpuMemPercentUsage, ram, swap, diskusage, cpuTemp, gpuTemp))
    time.sleep(1)

# Importing Libraries
from serial import Serial
import time
import struct
import psutil
import subprocess
import re
import os


maxGpuMem = 0
arduinoPort = "/dev/cu.usbserial-110"

arduino = Serial(port=arduinoPort, baudrate=9600, timeout=1)
while True:
    gpuUsage = 0
    gpuMemPercentUsage = 0
    gpuTemp = 0
    cpuTemp = 0
    gpuFreq = 0
    gpuPower = 0

    try:
        if os.geteuid() == 0:
            gpuInfo = subprocess.run(
                ["powermetrics", "-n", "1", "-i", "1000", "--samplers", "gpu_power"],
                capture_output=True,
                text=True,
                timeout=3,
            ).stdout
        else:
            gpuInfo = subprocess.run(
                ["sudo", "-n", "powermetrics", "-n", "1", "-i", "1000", "--samplers", "gpu_power"],
                capture_output=True,
                text=True,
                timeout=3,
            ).stdout

        gpuUsageMatch = re.search(r"GPU HW active residency:\s+([0-9.]+)%", gpuInfo)
        if gpuUsageMatch:
            gpuUsage = int(float(gpuUsageMatch.group(1)))

        gpuFreqMatch = re.search(r"GPU HW active frequency:\s+([0-9]+)\s+MHz", gpuInfo)
        if gpuFreqMatch:
            gpuFreq = int(gpuFreqMatch.group(1))

        gpuPowerMatch = re.search(r"GPU Power:\s+([0-9]+)\s+mW", gpuInfo)
        if gpuPowerMatch:
            gpuPower = int(gpuPowerMatch.group(1))
    except Exception:
        pass

    ram = int(psutil.virtual_memory().percent)

    cpu = int(psutil.cpu_percent())

    swap = int(psutil.swap_memory().percent)

    obj_Disk = psutil.disk_usage('/')
    diskusage = int(obj_Disk.percent)

    print(f'cpu: {cpu}%, gpu: {gpuUsage}%, gpuFreq: {gpuFreq}MHz, gpuPower: {gpuPower}mW, gpuMemPercentUsage: {gpuMemPercentUsage}%, ram: {ram}%, cpuTemp: {cpuTemp}, gpuTemp: {gpuTemp}, swap: {swap}%, diskUsage: {diskusage}%')

    arduino.write(struct.pack('BBBBBBBB', cpu, gpuUsage, gpuMemPercentUsage, ram, swap, diskusage, cpuTemp, gpuTemp))
    time.sleep(1)

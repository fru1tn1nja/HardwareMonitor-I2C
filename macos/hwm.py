# Importing Libraries
from serial import Serial
import time
import struct
import psutil
import subprocess
import json


maxGpuMem = 0
arduinoPort = "/dev/cu.usbserial-110"
minGpuTemp = 10
lastGpuTemp = 0

arduino = Serial(port=arduinoPort, baudrate=9600, timeout=1)
while True:
    gpuMemPercentUsage = 0

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

    ram = int(psutil.virtual_memory().percent)

    cpu = int(psutil.cpu_percent())

    swap = int(psutil.swap_memory().percent)

    obj_Disk = psutil.disk_usage('/')
    diskusage = int(obj_Disk.percent)

    print(f'cpu: {cpu}%, gpu: {gpuUsage}%, gpuFreq: {gpuFreq}MHz, gpuPower: {gpuPower}mW, gpuMemPercentUsage: {gpuMemPercentUsage}%, ram: {ram}%, cpuTemp: {cpuTemp}, gpuTemp: {gpuTemp}, swap: {swap}%, diskUsage: {diskusage}%')

    arduino.write(struct.pack('BBBBBBBB', cpu, gpuUsage, gpuMemPercentUsage, ram, swap, diskusage, cpuTemp, gpuTemp))
    time.sleep(1)

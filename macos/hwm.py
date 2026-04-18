# Importing Libraries
from serial import Serial
import time
import struct
import psutil


maxGpuMem = 0
arduinoPort = "/dev/cu.usbserial-110"

arduino = Serial(port=arduinoPort, baudrate=9600, timeout=1)
while True:
    gpuUsage = 0
    gpuMemPercentUsage = 0
    gpuTemp = 0
    cpuTemp = 0

    ram = int(psutil.virtual_memory().percent)

    cpu = int(psutil.cpu_percent())

    swap = int(psutil.swap_memory().percent)

    obj_Disk = psutil.disk_usage('/')
    diskusage = int(obj_Disk.percent)

    print(f'cpu: {cpu}%, gpu: {gpuUsage}%, gpuMemPercentUsage: {gpuMemPercentUsage}%, ram: {ram}%, cpuTemp: {cpuTemp}, gpuTemp: {gpuTemp}, swap: {swap}%, diskUsage: {diskusage}%')

    arduino.write(struct.pack('BBBBBBBB', cpu, gpuUsage, gpuMemPercentUsage, ram, swap, diskusage, cpuTemp, gpuTemp))
    time.sleep(1)

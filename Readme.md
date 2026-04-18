# HardwareMonitor Arduino + python
Analog of https://github.com/AlexGyver/PCdisplay for linux OS. Just displayed system perfomance info 

![How it looks like](https://github.com/aldiserg/HardwareMonitor-I2C/blob/main/view.png?raw=true)
![Connection](https://github.com/aldiserg/HardwareMonitor-I2C/blob/main/connections.png?raw=true)

# Requirements
Hardware:
  1. Arduino
  2. OLED display with i2c

Software:
  1. Python3
  2. pip3
  3. Arduino ide

Advanced:
  1. 3d printer ([Case model](https://www.thingiverse.com/thing:6146515))

# Python venv
Recommended:
```
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies from the `requirements.txt` file of the needed solution:
```
pip3 install -r amd/requirements.txt
pip3 install -r nvidia/requirements.txt
python3 -m pip install -r macos/requirements.txt
```

Deactivate when done:
```
deactivate
```

# Setup via script
Using install.sh

```
Usage:
./install.sh amd/nvidia gpuMemTotalMb /path/to/USB

Example:
./install.sh amd 12000 /dev/ttyUSB0
```
# Setup via shell
Upload sketch to arduino via arduino ide

Install libs + add access:

For NVIDIA gpu
```
pip3 install -r nvidia/requirements.txt
```

For AMD gpu
```
pip3 install -r amd/requirements.txt
```

Add permistion to /dev/ttyUSBx
```
sudo gpasswd -a username tty
sudo gpasswd -a username uucp

or

sudo chown username:usergroup /dev/ttyUSBx
```
Check tty device path
```
ls -l /dev/ttyUSB*
```
Run for check allright
```
python3 hwm.py
```

Create /etc/systemd/system/hwm.service file with following content
```
[Unit]
Description=Hardware Monitor
After=multi-user.target

[Service]
Type=simple
ExecStart=python /path/to/hwm.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Add deamon to startup and run
```
systemctl enable hwm --now
```

# macOS support
For macOS a separate minimal sender script is available in `macos/hwm.py`.
It keeps the same Arduino protocol and currently sends:

1. CPU usage
2. GPU usage
3. CPU temperature
4. GPU temperature
5. RAM usage
6. SWAP usage
7. Disk usage

`GPU memory usage` is currently left as `0` on Apple Silicon.
Reason: this project expects a VRAM-like metric, but Apple Silicon uses unified
memory, and there is no simple honest replacement for `GPUMEM` in the current
protocol.

The macOS sender now reads GPU usage, GPU frequency, GPU power,
CPU temperature and GPU temperature from `macmon`.

Install `macmon` with Homebrew:
```
brew install macmon
```

Important limitation:
if `macmon` is not installed or is not available in `PATH`,
`macos/hwm.py` will fail on startup.

Install dependencies:
```
python3 -m pip install -r macos/requirements.txt
```

Find the Arduino serial device:
```
ls /dev/cu.usb*
```

Open `macos/hwm.py`, find `arduinoPort`, and change it manually to your device path.
Example:
```
arduinoPort = "/dev/cu.usbserial-110"
```

Run the macOS sender:
```
.venv/bin/python3 macos/hwm.py
```

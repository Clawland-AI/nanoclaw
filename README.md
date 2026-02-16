# NanoClaw

**Mid-weight Python AI Agent with rich ecosystem support. Runs on $50 SBCs like Raspberry Pi.**

> Part of the [Clawland](https://github.com/Clawland-AI) ecosystem.

---

## Overview

NanoClaw bridges the gap between the ultra-lightweight PicClaw and the full-featured MoltClaw. Built in Python, it leverages the massive Python ecosystem for ML, computer vision, data processing, and automation — all on affordable single-board computers.

## Key Features

- **Python Ecosystem** — Full access to NumPy, OpenCV, TensorFlow Lite, scikit-learn, and more
- **Local ML Inference** — Run small models directly on edge hardware
- **Rich I/O** — GPIO, I2C, SPI, Serial, Camera, Microphone support
- **Agent Capabilities** — Tool use, memory, multi-step reasoning
- **Cloud Sync** — Report to MoltClaw, receive orchestration commands

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| RAM | 100MB | 512MB+ |
| Storage | 200MB | 1GB+ |
| Hardware | Raspberry Pi Zero 2W | Raspberry Pi 4/5 |
| Cost | ~$15 | ~$50 |

## Use Cases

- **Smart Camera** — Person/object detection with Pi Camera + TFLite
- **Voice Assistant** — Local wake-word + cloud LLM hybrid
- **Data Collector** — Aggregate sensor data from multiple MicroClaw nodes
- **Lab Monitor** — Temperature, humidity, air quality with ML anomaly detection

---

## Raspberry Pi Deployment Guide

### Prerequisites

**Hardware:**
- Raspberry Pi 4 Model B (2GB+ RAM recommended)
- MicroSD card (16GB+, Class 10 or better)
- USB-C power supply (5V/3A minimum)
- (Optional) Pi Camera Module for vision tasks
- (Optional) Sensors (DHT22, BME280, etc.)

**Software:**
- Raspberry Pi OS Lite (64-bit recommended)
- Python 3.9 or later
- Git

### Step 1: Prepare Raspberry Pi OS

#### Download and Flash OS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Flash **Raspberry Pi OS Lite (64-bit)** to your microSD card
3. Configure:
   - Set hostname: `nanoclaw-01`
   - Enable SSH
   - Set username and password
   - Configure WiFi (if using wireless)

#### First Boot

1. Insert microSD into Raspberry Pi and power on
2. SSH into the Pi:
   ```bash
   ssh pi@nanoclaw-01.local
   ```
3. Update system:
   ```bash
   sudo apt-get update && sudo apt-get upgrade -y
   ```

### Step 2: Install Dependencies

#### Python and System Packages

```bash
# Install Python 3 and pip
sudo apt-get install -y python3 python3-pip python3-venv git

# Install system libraries for ML and CV
sudo apt-get install -y \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libharfbuzz0b \
    libwebp7 \
    libjasper1 \
    libilmbase25 \
    libopenexr25 \
    libgstreamer1.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libqt5gui5 \
    libqt5test5 \
    libqt5widgets5

# For I2C/SPI/GPIO (if using sensors)
sudo apt-get install -y i2c-tools python3-smbus
```

#### Enable Hardware Interfaces

```bash
# Enable I2C, SPI, Camera
sudo raspi-config nonint do_i2c 0
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_camera 0

# Reboot to apply
sudo reboot
```

### Step 3: Install NanoClaw

#### Clone Repository

```bash
cd ~
git clone https://github.com/Clawland-AI/nanoclaw.git
cd nanoclaw
```

#### Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Install Python Dependencies

```bash
pip install --upgrade pip
pip install -e .
```

### Step 4: Configuration

#### Create Configuration File

```bash
mkdir -p ~/.nanoclaw
cat > ~/.nanoclaw/config.yaml << 'EOF'
# NanoClaw Configuration
agent:
  name: nanoclaw-01
  role: edge-gateway

cloud:
  moltclaw_url: https://your-moltclaw-instance.com
  api_key: YOUR_API_KEY_HERE

sensors:
  enabled: true
  poll_interval: 60  # seconds

camera:
  enabled: false
  resolution: [640, 480]
  fps: 10

logging:
  level: INFO
  file: /var/log/nanoclaw/agent.log
EOF
```

#### Edit Configuration

```bash
nano ~/.nanoclaw/config.yaml
```

Update `moltclaw_url` and `api_key` with your actual values.

### Step 5: Test Installation

```bash
# Activate virtual environment
source ~/nanoclaw/venv/bin/activate

# Run NanoClaw
python -m nanoclaw

# You should see startup logs
```

Press `Ctrl+C` to stop.

### Step 6: Create Systemd Service

#### Create Service File

```bash
sudo nano /etc/systemd/system/nanoclaw.service
```

Paste the following:

```ini
[Unit]
Description=NanoClaw AI Agent
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/nanoclaw
Environment="PATH=/home/pi/nanoclaw/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=/home/pi/nanoclaw/venv/bin/python -m nanoclaw
Restart=on-failure
RestartSec=10

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=nanoclaw

[Install]
WantedBy=multi-user.target
```

Save and exit (`Ctrl+X`, `Y`, `Enter`).

#### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable auto-start on boot
sudo systemctl enable nanoclaw

# Start service now
sudo systemctl start nanoclaw

# Check status
sudo systemctl status nanoclaw
```

#### View Logs

```bash
# Real-time logs
sudo journalctl -u nanoclaw -f

# Last 100 lines
sudo journalctl -u nanoclaw -n 100
```

### Step 7: Verify Operation

#### Check Service Status

```bash
sudo systemctl status nanoclaw
```

Should show `active (running)`.

#### Test Sensor Reading (if enabled)

```bash
# Install test script
cat > ~/test_sensor.py << 'EOF'
import time
from nanoclaw.sensors import read_sensors

while True:
    data = read_sensors()
    print(f"Temperature: {data['temperature']:.1f}°C")
    print(f"Humidity: {data['humidity']:.1f}%")
    time.sleep(5)
EOF

# Run test
python ~/test_sensor.py
```

### Troubleshooting

#### Service Won't Start

```bash
# Check detailed logs
sudo journalctl -u nanoclaw -xe

# Check Python errors
python -m nanoclaw
```

#### I2C/SPI Not Working

```bash
# Check if interfaces are enabled
ls /dev/i2c* /dev/spidev*

# Test I2C devices
sudo i2cdetect -y 1
```

#### High CPU Usage

```bash
# Check resource usage
htop

# Reduce ML inference frequency in config.yaml
nano ~/.nanoclaw/config.yaml
```

#### Network Issues

```bash
# Test MoltClaw connection
curl -I https://your-moltclaw-instance.com/health

# Check network connectivity
ping 8.8.8.8
```

### Updating NanoClaw

```bash
cd ~/nanoclaw
git pull origin main
source venv/bin/activate
pip install --upgrade -e .
sudo systemctl restart nanoclaw
```

### Uninstallation

```bash
# Stop and disable service
sudo systemctl stop nanoclaw
sudo systemctl disable nanoclaw
sudo rm /etc/systemd/system/nanoclaw.service
sudo systemctl daemon-reload

# Remove NanoClaw
rm -rf ~/nanoclaw
rm -rf ~/.nanoclaw
```

---

## Status

🚧 **Pre-Alpha** — Architecture design phase. Looking for contributors!

## Contributing

See the [Clawland Contributing Guide](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTING.md).

**Core contributors share 20% of product revenue.** Read the [Contributor Revenue Share](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTOR-REVENUE-SHARE.md) terms.

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.

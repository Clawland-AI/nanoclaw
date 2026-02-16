# 🍇 NanoClaw — L2 Regional Gateway Agent

**NanoClaw** is the L2 (regional gateway) agent in the Clawland edge AI network. It runs on Raspberry Pi or similar SBCs ($50-100), aggregating sensor data from multiple PicoClaw (L1) and MicroClaw (L0) edge nodes, and uploading batches to MoltClaw (L3) cloud coordination.

## Features

- ✅ **HTTP server** — receives sensor reports from edge nodes
- ✅ **In-memory buffer** — aggregates readings with configurable threshold
- ✅ **Batch upload** — efficient data transfer to MoltClaw (L3)
- ✅ **Offline queue** — resilient to L3 disconnection
- ✅ **Auto-retry** — syncs queued batches when connection restores
- ✅ **FastAPI** — OpenAPI docs at `/docs`

## Hardware Requirements

- **SBC:** Raspberry Pi 4/5 (2GB+ RAM) or equivalent
- **OS:** Raspberry Pi OS Lite (64-bit) or Ubuntu Server 22.04+
- **Storage:** 8GB+ microSD card
- **Network:** WiFi or Ethernet (must reach edge nodes and MoltClaw)

## Quick Start

### 1. Install on Raspberry Pi

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+ (if not already installed)
sudo apt install -y python3 python3-pip python3-venv

# Clone repository
git clone https://github.com/Clawland-AI/nanoclaw.git
cd nanoclaw

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install NanoClaw
pip install -e .
```

### 2. Start Gateway

```bash
# Start NanoClaw server
nanoclaw --host 0.0.0.0 --port 8000

# Or with auto-reload (dev mode)
nanoclaw --reload
```

### 3. Test API

```bash
# Health check
curl http://localhost:8000/healthz

# Send test sensor reading
curl -X POST http://localhost:8000/report \
  -H "Content-Type: application/json" \
  -d '{
    "node_id": "microclaw_node_001",
    "sensor_type": "temperature",
    "value": 23.5,
    "unit": "C"
  }'

# Check buffer status
curl http://localhost:8000/buffer
```

## API Endpoints

### POST /report
Receive sensor reading from edge node.

**Request body:**
```json
{
  "node_id": "microclaw_node_001",
  "sensor_type": "temperature",
  "value": 23.5,
  "unit": "C",
  "timestamp": "2026-02-16T08:00:00Z"  // optional
}
```

**Response:**
```json
{
  "status": "accepted",
  "node_id": "microclaw_node_001",
  "buffer_size": 42
}
```

### GET /buffer
Get current buffer status.

**Response:**
```json
{
  "buffer_size": 42,
  "batch_threshold": 100,
  "offline_queue_size": 0,
  "should_upload": false,
  "recent_readings": [...]
}
```

### POST /batch
Manually trigger batch upload to MoltClaw (L3).

**Response:**
```json
{
  "status": "uploaded",
  "batch_size": 42,
  "timestamp": "2026-02-16T08:00:00Z"
}
```

### GET /offline-queue
Get batches queued for offline retry.

**Response:**
```json
{
  "queue_size": 2,
  "batches": [
    {
      "gateway_id": "nanoclaw_gateway_001",
      "reading_count": 100,
      "timestamp": "2026-02-16T07:55:00Z"
    }
  ]
}
```

### POST /offline-queue/retry
Retry uploading queued batches.

**Response:**
```json
{
  "status": "completed",
  "uploaded": 2,
  "failed": 0
}
```

## Configuration

### Buffer Settings

Edit `src/nanoclaw/server.py`:

```python
sensor_buffer = SensorBuffer(
    max_size=1000,        # Max readings in buffer
    batch_threshold=100   # Upload when buffer reaches this size
)
```

### Batch Upload

By default, batches are created manually via `POST /batch`. For production, enable background task:

```python
# In server.py, uncomment auto_batch_upload() task
# This will upload every 60 seconds or when threshold is reached
```

## Systemd Service (Auto-Start)

Create `/etc/systemd/system/nanoclaw.service`:

```ini
[Unit]
Description=NanoClaw L2 Gateway Agent
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/nanoclaw
ExecStart=/home/pi/nanoclaw/.venv/bin/nanoclaw --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nanoclaw
sudo systemctl start nanoclaw
sudo systemctl status nanoclaw
```

## Architecture

```
┌─────────────────────────────────────────────┐
│  Clawland Edge AI Network                   │
├─────────────────────────────────────────────┤
│  L0 MicroClaw (ESP32)                       │
│    └─ POST /report → NanoClaw               │
│           ↓                                 │
│  L1 PicoClaw (RPi Pico W)                   │
│    └─ POST /report → NanoClaw               │
│           ↓                                 │
│  L2 NanoClaw (Raspberry Pi) ← YOU ARE HERE  │
│    ├─ Aggregate readings in buffer          │
│    ├─ Batch upload to MoltClaw              │
│    └─ Offline queue when L3 unreachable     │
│           ↓ HTTPS                           │
│  L3 MoltClaw (Cloud)                        │
│    └─ Global coordination                   │
└─────────────────────────────────────────────┘
```

## Offline Operation

NanoClaw is designed for edge scenarios where MoltClaw (L3) may be unreachable:

1. **Buffer fills** — readings from edge nodes accumulate in memory
2. **Upload fails** — batch is moved to offline queue
3. **Retry on interval** — background task retries every 5 minutes
4. **Connection restored** — all queued batches upload automatically

**Offline queue capacity:**
- Memory: ~1000 readings @ 100 bytes each = 100KB
- Persistent storage: TODO (future enhancement)

## Development

### Run Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Lint
ruff check .

# Format
ruff format .

# Type check
mypy src/
```

### API Docs

FastAPI auto-generates interactive docs:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### Edge Nodes Can't Connect

1. Check firewall: `sudo ufw allow 8000`
2. Verify NanoClaw is listening on 0.0.0.0: `netstat -tulnp | grep 8000`
3. Test from edge node: `curl http://<nanoclaw-ip>:8000/healthz`

### Buffer Overflows

Increase `max_size` in `server.py`:

```python
sensor_buffer = SensorBuffer(max_size=5000, batch_threshold=500)
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, and PR guidelines.

## License

Apache 2.0 — see [LICENSE](LICENSE) for details.

## Links

- **Clawland Docs:** https://docs.clawland.ai
- **Issues:** https://github.com/Clawland-AI/nanoclaw/issues
- **Discussions:** https://github.com/Clawland-AI/nanoclaw/discussions

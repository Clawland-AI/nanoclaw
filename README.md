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

## Raspberry Pi Gateway Quick Start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
nanoclaw --host 0.0.0.0 --port 8000
```

Docker/ARM64 deployments can use the included multi-arch Python base image:

```bash
docker build -t nanoclaw:local .
docker run --rm -p 8000:8000 nanoclaw:local
```

## Sensor Aggregation API

NanoClaw accepts reports from PicClaw or MicroClaw nodes and keeps a bounded
in-memory history for each node.

```bash
curl -X POST http://localhost:8000/api/v1/telemetry \
  -H 'Content-Type: application/json' \
  -d '{"node_id":"rack-a1","temperature_c":41.0,"humidity_pct":72.0}'
```

Core endpoints:

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/healthz` | Service health, node count, decision count |
| `POST` | `/api/v1/telemetry` | Ingest one sensor report |
| `GET` | `/api/v1/nodes` | List current node states |
| `GET` | `/api/v1/nodes/{node_id}` | Inspect one node and recent readings |
| `GET` | `/api/v1/decisions` | List local threshold decisions |

## Local Decision Engine

The first offline decision engine flags temperature and humidity threshold
crossings without needing MoltClaw/cloud access:

- `temperature_warning`
- `temperature_critical`
- `humidity_warning`

Each decision includes the node id, severity, threshold, observed value, and a
suggested local action such as publishing an alert or dispatching cooling.

## Status

🚧 **Pre-Alpha** — Sensor aggregation, local threshold decisions, FastAPI
endpoints, and ARM64-friendly Docker packaging are now scaffolded.

## Contributing

See the [Clawland Contributing Guide](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTING.md).

**Core contributors share 20% of product revenue.** Read the [Contributor Revenue Share](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTOR-REVENUE-SHARE.md) terms.

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.

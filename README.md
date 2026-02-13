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

## Status

🚧 **Pre-Alpha** — Architecture design phase. Looking for contributors!

## Contributing

See the [Clawland Contributing Guide](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTING.md).

**Core contributors share 20% of product revenue.** Read the [Contributor Revenue Share](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTOR-REVENUE-SHARE.md) terms.

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.

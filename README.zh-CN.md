# NanoClaw

**中量级 Python AI 智能体，支持丰富的生态工具。可运行在树莓派等约 50 美元的单板计算机上。**

> 属于 [Clawland](https://github.com/Clawland-AI) 生态。

---

## 项目简介

NanoClaw 位于轻量级 PicClaw 与功能完整的 MoltClaw 之间。它使用 Python 构建，可借助丰富的 Python 生态进行机器学习、计算机视觉、数据处理和自动化，并运行在价格亲民的单板计算机上。

## 主要功能

- **Python 生态**：可使用 NumPy、OpenCV、TensorFlow Lite、scikit-learn 等工具
- **本地机器学习推理**：可在边缘硬件上直接运行小型模型
- **丰富的输入输出接口**：支持 GPIO、I2C、SPI、串口、摄像头和麦克风
- **智能体能力**：支持工具调用、记忆和多步骤推理
- **云端同步**：向 MoltClaw 上报信息，并接收编排指令

## 硬件要求

| 组件 | 最低配置 | 推荐配置 |
|-----------|---------|-------------|
| 内存 | 100 MB | 512 MB 以上 |
| 存储空间 | 200 MB | 1 GB 以上 |
| 硬件 | Raspberry Pi Zero 2W | Raspberry Pi 4/5 |
| 成本 | 约 15 美元 | 约 50 美元 |

## 使用场景

- **智能摄像头**：搭配 Pi Camera 和 TFLite 进行人物或物体检测
- **语音助手**：结合本地唤醒词检测与云端大语言模型
- **数据采集器**：汇总多个 MicroClaw 节点的传感器数据
- **实验室监测**：使用机器学习检测温度、湿度和空气质量异常

## 项目状态

🚧 **预 Alpha 阶段**：目前处于架构设计阶段，欢迎贡献者参与。

## 参与贡献

请参阅 [Clawland 贡献指南](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTING.md)。

**核心贡献者可分享产品收入的 20%。** 详情请阅读[贡献者收入分成条款](https://github.com/Clawland-AI/.github/blob/main/CONTRIBUTOR-REVENUE-SHARE.md)。

## 许可证

Apache License 2.0。详情请参阅 [LICENSE](LICENSE)。


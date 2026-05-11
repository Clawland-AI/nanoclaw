"""Sensor aggregation and local decisions for NanoClaw."""

from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Any


@dataclass(slots=True)
class SensorReading:
    """A single report from a PicClaw or MicroClaw node."""

    node_id: str
    temperature_c: float | None = None
    humidity_pct: float | None = None
    metrics: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "temperature_c": self.temperature_c,
            "humidity_pct": self.humidity_pct,
            "metrics": self.metrics,
            "timestamp": self.timestamp,
        }


@dataclass(slots=True)
class NodeState:
    """Current state and bounded history for one edge node."""

    node_id: str
    readings: list[SensorReading] = field(default_factory=list)
    status: str = "unknown"
    updated_at: float = 0.0

    @property
    def latest(self) -> SensorReading | None:
        if not self.readings:
            return None
        return self.readings[-1]

    def to_dict(self) -> dict[str, Any]:
        latest = self.latest
        return {
            "node_id": self.node_id,
            "status": self.status,
            "updated_at": self.updated_at,
            "latest": latest.to_dict() if latest else None,
            "readings": [reading.to_dict() for reading in self.readings],
        }


@dataclass(slots=True)
class Decision:
    """A local offline decision generated from sensor data."""

    node_id: str
    type: str
    severity: str
    action: str
    value: float
    threshold: float
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "type": self.type,
            "severity": self.severity,
            "action": self.action,
            "value": self.value,
            "threshold": self.threshold,
            "timestamp": self.timestamp,
        }


class SensorAggregator:
    """In-memory L2 sensor aggregator for nearby L1 nodes."""

    def __init__(self, max_readings_per_node: int = 100, stale_after_seconds: int = 120) -> None:
        self.max_readings_per_node = max_readings_per_node
        self.stale_after_seconds = stale_after_seconds
        self._nodes: dict[str, NodeState] = {}

    def ingest(self, reading: SensorReading) -> NodeState:
        if not reading.node_id:
            raise ValueError("node_id is required")

        node = self._nodes.setdefault(reading.node_id, NodeState(node_id=reading.node_id))
        node.readings.append(reading)
        if len(node.readings) > self.max_readings_per_node:
            node.readings = node.readings[-self.max_readings_per_node :]
        node.status = "online"
        node.updated_at = reading.timestamp
        return node

    def get_node(self, node_id: str) -> NodeState:
        try:
            return self._nodes[node_id]
        except KeyError as exc:
            raise KeyError(f"node {node_id!r} not found") from exc

    def list_nodes(self) -> list[NodeState]:
        return sorted(self._nodes.values(), key=lambda node: node.node_id)

    def mark_stale_nodes(self, now: float | None = None) -> list[NodeState]:
        now = time.time() if now is None else now
        stale: list[NodeState] = []
        for node in self._nodes.values():
            if node.status == "online" and now - node.updated_at >= self.stale_after_seconds:
                node.status = "stale"
                stale.append(node)
        return stale


class DecisionEngine:
    """Threshold-based local decisions for offline operation."""

    def __init__(
        self,
        temp_warning_c: float = 35.0,
        temp_critical_c: float = 45.0,
        humidity_warning_pct: float = 75.0,
    ) -> None:
        self.temp_warning_c = temp_warning_c
        self.temp_critical_c = temp_critical_c
        self.humidity_warning_pct = humidity_warning_pct

    def evaluate(self, reading: SensorReading) -> list[Decision]:
        decisions: list[Decision] = []
        if reading.temperature_c is not None:
            if reading.temperature_c >= self.temp_critical_c:
                decisions.append(
                    Decision(
                        node_id=reading.node_id,
                        type="temperature_critical",
                        severity="critical",
                        action="publish alert and dispatch cooling command",
                        value=reading.temperature_c,
                        threshold=self.temp_critical_c,
                    )
                )
            elif reading.temperature_c >= self.temp_warning_c:
                decisions.append(
                    Decision(
                        node_id=reading.node_id,
                        type="temperature_warning",
                        severity="warning",
                        action="publish warning and increase sample rate",
                        value=reading.temperature_c,
                        threshold=self.temp_warning_c,
                    )
                )

        if reading.humidity_pct is not None and reading.humidity_pct >= self.humidity_warning_pct:
            decisions.append(
                Decision(
                    node_id=reading.node_id,
                    type="humidity_warning",
                    severity="warning",
                    action="publish humidity warning",
                    value=reading.humidity_pct,
                    threshold=self.humidity_warning_pct,
                )
            )
        return decisions

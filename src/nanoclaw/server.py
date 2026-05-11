"""NanoClaw FastAPI server - L2 regional gateway."""

from __future__ import annotations

from collections import deque
from typing import Any

from fastapi import FastAPI, HTTPException

from nanoclaw.aggregation import Decision, DecisionEngine, SensorAggregator, SensorReading

app = FastAPI(
    title="NanoClaw",
    description="L2 regional gateway that aggregates L1 PicoClaw/MicroClaw sensor reports",
    version="0.1.0",
)

aggregator = SensorAggregator()
decision_engine = DecisionEngine()
decision_log: deque[Decision] = deque(maxlen=1000)


@app.get("/healthz")
async def healthz() -> dict[str, Any]:
    aggregator.mark_stale_nodes()
    return {
        "status": "ok",
        "agent": "nanoclaw",
        "version": "0.1.0",
        "nodes": len(aggregator.list_nodes()),
        "decisions": len(decision_log),
    }


@app.post("/api/v1/telemetry", status_code=202)
async def ingest_telemetry(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        reading = SensorReading(
            node_id=str(payload["node_id"]),
            temperature_c=payload.get("temperature_c"),
            humidity_pct=payload.get("humidity_pct"),
            metrics=payload.get("metrics", {}),
            timestamp=payload.get("timestamp"),
        )
    except KeyError as exc:
        raise HTTPException(status_code=400, detail="node_id is required") from exc

    if reading.timestamp is None:
        reading = SensorReading(
            node_id=reading.node_id,
            temperature_c=reading.temperature_c,
            humidity_pct=reading.humidity_pct,
            metrics=reading.metrics,
        )

    try:
        node = aggregator.ingest(reading)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    decisions = decision_engine.evaluate(reading)
    decision_log.extend(decisions)

    return {
        "status": "accepted",
        "node": node.to_dict(),
        "decisions": [decision.to_dict() for decision in decisions],
    }


@app.get("/api/v1/nodes")
async def list_nodes() -> dict[str, Any]:
    aggregator.mark_stale_nodes()
    return {"nodes": [node.to_dict() for node in aggregator.list_nodes()]}


@app.get("/api/v1/nodes/{node_id}")
async def get_node(node_id: str) -> dict[str, Any]:
    aggregator.mark_stale_nodes()
    try:
        node = aggregator.get_node(node_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="node not found") from exc
    return node.to_dict()


@app.get("/api/v1/decisions")
async def list_decisions() -> dict[str, Any]:
    return {"decisions": [decision.to_dict() for decision in decision_log]}

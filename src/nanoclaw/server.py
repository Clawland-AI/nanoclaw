"""NanoClaw FastAPI server — L2 regional gateway."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from collections import deque

app = FastAPI(
    title="NanoClaw",
    description="L2 Regional Gateway Agent — aggregates data from L1 PicoClaw/MicroClaw nodes",
    version="0.2.0",
)

# ========== Data Models ==========

class SensorReading(BaseModel):
    """Single sensor reading from an edge node."""
    node_id: str = Field(..., description="Unique identifier for the reporting node")
    sensor_type: str = Field(..., description="Type of sensor (temperature, humidity, etc.)")
    value: float = Field(..., description="Sensor reading value")
    unit: str = Field(..., description="Unit of measurement (C, %, etc.)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Reading timestamp")

class BatchReport(BaseModel):
    """Batch of aggregated sensor readings for upload to MoltClaw (L3)."""
    gateway_id: str = Field(..., description="NanoClaw gateway identifier")
    readings: List[SensorReading] = Field(..., description="Aggregated sensor readings")
    batch_timestamp: datetime = Field(default_factory=datetime.utcnow)

# ========== In-Memory Buffer ==========

class SensorBuffer:
    """In-memory buffer for aggregating sensor readings."""
    def __init__(self, max_size: int = 1000, batch_threshold: int = 100):
        self.buffer: deque = deque(maxlen=max_size)
        self.batch_threshold = batch_threshold
        self.offline_queue: List[BatchReport] = []
        
    def add_reading(self, reading: SensorReading) -> None:
        """Add a sensor reading to the buffer."""
        self.buffer.append(reading)
        
    def get_readings(self, limit: Optional[int] = None) -> List[SensorReading]:
        """Get readings from buffer (FIFO)."""
        if limit:
            return list(self.buffer)[:limit]
        return list(self.buffer)
    
    def clear_readings(self, count: int) -> None:
        """Remove readings from buffer after successful upload."""
        for _ in range(min(count, len(self.buffer))):
            self.buffer.popleft()
    
    def should_batch_upload(self) -> bool:
        """Check if buffer has reached batch threshold."""
        return len(self.buffer) >= self.batch_threshold
    
    def queue_offline(self, batch: BatchReport) -> None:
        """Queue batch for later upload when L3 is unreachable."""
        self.offline_queue.append(batch)
        
    def get_offline_queue(self) -> List[BatchReport]:
        """Get all queued batches."""
        return self.offline_queue
    
    def clear_offline_queue(self) -> None:
        """Clear offline queue after successful sync."""
        self.offline_queue.clear()

# Global buffer instance
sensor_buffer = SensorBuffer(max_size=1000, batch_threshold=100)

# ========== API Endpoints ==========

@app.get("/healthz")
async def healthz():
    """Health check endpoint."""
    return {
        "status": "ok",
        "agent": "nanoclaw",
        "version": "0.2.0",
        "buffer_size": len(sensor_buffer.buffer),
        "offline_queue_size": len(sensor_buffer.offline_queue),
    }

@app.post("/report", status_code=201)
async def receive_report(reading: SensorReading):
    """
    Receive sensor reading from PicoClaw (L1) or MicroClaw (L0) edge node.
    
    **Example payload:**
    ```json
    {
      "node_id": "microclaw_node_001",
      "sensor_type": "temperature",
      "value": 23.5,
      "unit": "C",
      "timestamp": "2026-02-16T08:00:00Z"
    }
    ```
    """
    sensor_buffer.add_reading(reading)
    return {
        "status": "accepted",
        "node_id": reading.node_id,
        "buffer_size": len(sensor_buffer.buffer),
    }

@app.get("/buffer")
async def get_buffer_status():
    """
    Get current buffer status and recent readings.
    
    Returns:
    - Buffer size
    - Batch threshold
    - Offline queue size
    - Recent readings (last 10)
    """
    recent_readings = sensor_buffer.get_readings(limit=10)
    return {
        "buffer_size": len(sensor_buffer.buffer),
        "batch_threshold": sensor_buffer.batch_threshold,
        "offline_queue_size": len(sensor_buffer.offline_queue),
        "should_upload": sensor_buffer.should_batch_upload(),
        "recent_readings": [r.model_dump() for r in recent_readings],
    }

@app.post("/batch")
async def create_batch():
    """
    Manually trigger batch creation and upload to MoltClaw (L3).
    
    In production, this would be called automatically by a background task
    when buffer reaches threshold or on interval.
    """
    if len(sensor_buffer.buffer) == 0:
        raise HTTPException(status_code=400, detail="Buffer is empty")
    
    # Create batch report
    batch = BatchReport(
        gateway_id="nanoclaw_gateway_001",
        readings=sensor_buffer.get_readings(),
    )
    
    # Simulate upload to MoltClaw (L3)
    # In production, this would be an HTTP POST to MoltClaw API
    try:
        # TODO: Replace with actual HTTP call to MoltClaw
        # response = await httpx.post("https://moltclaw.clawland.ai/ingest", json=batch.model_dump())
        # response.raise_for_status()
        
        # For now, simulate success
        await asyncio.sleep(0.1)  # Simulate network delay
        
        # Clear buffer after successful upload
        sensor_buffer.clear_readings(len(batch.readings))
        
        return {
            "status": "uploaded",
            "batch_size": len(batch.readings),
            "timestamp": batch.batch_timestamp,
        }
    except Exception as e:
        # If upload fails, queue for offline retry
        sensor_buffer.queue_offline(batch)
        raise HTTPException(
            status_code=503,
            detail=f"L3 unreachable, queued for retry: {str(e)}"
        )

@app.get("/offline-queue")
async def get_offline_queue():
    """
    Get all batches queued for offline retry.
    
    These batches failed to upload to MoltClaw (L3) and are waiting for retry.
    """
    queue = sensor_buffer.get_offline_queue()
    return {
        "queue_size": len(queue),
        "batches": [
            {
                "gateway_id": batch.gateway_id,
                "reading_count": len(batch.readings),
                "timestamp": batch.batch_timestamp,
            }
            for batch in queue
        ],
    }

@app.post("/offline-queue/retry")
async def retry_offline_queue():
    """
    Retry uploading all queued batches to MoltClaw (L3).
    
    Returns number of successfully uploaded batches.
    """
    queue = sensor_buffer.get_offline_queue()
    if not queue:
        return {"status": "no_batches", "uploaded": 0}
    
    uploaded_count = 0
    failed_batches = []
    
    for batch in queue:
        try:
            # TODO: Replace with actual HTTP call to MoltClaw
            # response = await httpx.post("https://moltclaw.clawland.ai/ingest", json=batch.model_dump())
            # response.raise_for_status()
            
            # For now, simulate success
            await asyncio.sleep(0.1)
            uploaded_count += 1
        except Exception:
            # Keep failed batches in queue
            failed_batches.append(batch)
    
    # Update offline queue with only failed batches
    sensor_buffer.offline_queue = failed_batches
    
    return {
        "status": "completed",
        "uploaded": uploaded_count,
        "failed": len(failed_batches),
    }

# ========== Background Task (for production) ==========

@app.on_event("startup")
async def startup_event():
    """
    Initialize background tasks on startup.
    
    In production, this would start:
    - Periodic batch upload task (every 60 seconds or on threshold)
    - Offline queue retry task (every 5 minutes)
    """
    print("🍇 NanoClaw L2 Gateway starting...")
    print(f"   Buffer: max_size={sensor_buffer.buffer.maxlen}, threshold={sensor_buffer.batch_threshold}")
    print("   Ready to receive edge node reports")

# TODO: Add background task for automatic batch upload
# async def auto_batch_upload():
#     while True:
#         await asyncio.sleep(60)  # Check every 60 seconds
#         if sensor_buffer.should_batch_upload():
#             await create_batch()

"""NanoClaw FastAPI server 鈥?L2 regional gateway."""

from fastapi import FastAPI

app = FastAPI(
    title="NanoClaw",
    description="L2 Regional Gateway Agent 鈥?aggregates data from L1 PicoClaw/MicroClaw nodes",
    version="0.1.0",
)

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "agent": "nanoclaw", "version": "0.1.0"}
"""NanoClaw CLI entry point."""

import argparse
import uvicorn

def main() -> None:
    parser = argparse.ArgumentParser(description="NanoClaw — L2 Regional Gateway Agent")
    parser.add_argument("--port", type=int, default=8000, help="HTTP server port")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP server host")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (dev mode)")
    args = parser.parse_args()

    print(f"🍇 NanoClaw Agent v0.2.0")
    print(f"   Starting L2 Gateway on {args.host}:{args.port}...")
    print("   Aggregating data from L1 PicoClaw/MicroClaw nodes")
    print("   API docs: http://localhost:8000/docs")
    
    # Start FastAPI server
    uvicorn.run(
        "nanoclaw.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )

if __name__ == "__main__":
    main()

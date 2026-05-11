"""NanoClaw CLI entry point."""

from __future__ import annotations

import argparse

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="NanoClaw - L2 Regional Gateway Agent")
    parser.add_argument("--port", type=int, default=8000, help="HTTP server port")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP server host")
    parser.add_argument("--reload", action="store_true", help="Enable uvicorn reload for development")
    args = parser.parse_args()

    print(f"NanoClaw Agent starting on {args.host}:{args.port}...")
    print("L2 regional gateway ready for L1 edge agent reports.")
    uvicorn.run("nanoclaw.server:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()

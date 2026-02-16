"""NanoClaw CLI entry point."""

import argparse

def main() -> None:
    parser = argparse.ArgumentParser(description="NanoClaw 鈥?L2 Regional Gateway Agent")
    parser.add_argument("--port", type=int, default=8000, help="HTTP server port")
    parser.add_argument("--host", default="0.0.0.0", help="HTTP server host")
    args = parser.parse_args()

    print(f"馃 NanoClaw Agent starting on {args.host}:{args.port}...")
    print("   L2 Regional Gateway ready.")
    print("   Waiting for L1 edge agent reports...")

if __name__ == "__main__":
    main()
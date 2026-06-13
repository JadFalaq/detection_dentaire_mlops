#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import uvicorn

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from detection_dentaire.serving import create_app


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Serve the dental detection API.")
    parser.add_argument("--host", default="127.0.0.1", help="Host bind address.")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on.")
    parser.add_argument(
        "--config",
        default="configs/infer.yaml",
        help="Inference config path relative to the project root.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    app = create_app(config_path=args.config)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

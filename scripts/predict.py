#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from detection_dentaire.utils import load_yaml, project_root, resolve_project_path, ensure_dir


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run inference on one image or a folder of images using a trained YOLO model."
    )
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        help="Path to one image or a folder of images.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="configs/infer.yaml",
        help="Path to inference config file.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Optional custom output directory. If omitted, uses configs/infer.yaml.",
    )
    return parser.parse_args()


def validate_source(source: Path) -> Path:
    if not source.exists():
        raise FileNotFoundError(f"Source not found: {source}")
    return source


def collect_images_from_dir(folder: Path) -> list[Path]:
    return sorted([p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS])


def main() -> None:
    args = parse_args()
    root = project_root()

    infer_cfg = load_yaml(root / args.config)
    inference = infer_cfg["inference"]
    outputs = infer_cfg["outputs"]

    checkpoint = resolve_project_path(inference["checkpoint"], base=root)
    if not checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint}")

    source = validate_source(Path(args.source).resolve())

    save_dir = Path(args.output_dir).resolve() if args.output_dir else (root / outputs["save_dir"]).resolve()
    ensure_dir(save_dir)

    model = YOLO(str(checkpoint))

    # Ultralytics accepte directement un fichier ou un dossier
    results = model.predict(
        source=str(source),
        imgsz=inference["image_size"],
        conf=inference["conf_threshold"],
        iou=inference["iou_threshold"],
        max_det=inference["max_det"],
        device=inference["device"],
        save=True,
        save_txt=inference["save_txt"],
        save_conf=inference["save_conf"],
        project=str(save_dir.parent),
        name=save_dir.name,
        exist_ok=True,
        verbose=True,
    )

    n_images = 1
    if source.is_dir():
        n_images = len(collect_images_from_dir(source))

    print("[OK] Inference finished.")
    print(f"[OK] Checkpoint : {checkpoint}")
    print(f"[OK] Source     : {source}")
    print(f"[OK] Images     : {n_images}")
    print(f"[OK] Saved to   : {save_dir}")


if __name__ == "__main__":
    main()

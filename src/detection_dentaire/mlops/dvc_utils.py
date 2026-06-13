from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def read_dvc_file(dvc_path: str | Path) -> dict[str, Any]:
    dvc_path = Path(dvc_path)
    if not dvc_path.exists():
        raise FileNotFoundError(f"DVC file not found: {dvc_path}")

    with dvc_path.open("r", encoding="utf-8") as f:
        payload = yaml.safe_load(f) or {}

    if not isinstance(payload, dict):
        raise ValueError(f"Invalid DVC file format: {dvc_path}")
    return payload


def listed_dvc_outputs(dvc_path: str | Path) -> list[Path]:
    payload = read_dvc_file(dvc_path)
    outputs = []
    for item in payload.get("outs", []):
        if isinstance(item, dict) and "path" in item:
            outputs.append(Path(item["path"]))
    return outputs


def dvc_outputs_exist(dvc_path: str | Path, base_dir: str | Path | None = None) -> bool:
    dvc_path = Path(dvc_path)
    base_dir = Path(base_dir) if base_dir is not None else dvc_path.parent
    return all((base_dir / output).exists() for output in listed_dvc_outputs(dvc_path))

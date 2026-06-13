#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import mlflow
import yaml
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from detection_dentaire.mlops import (
    start_run_with_configs,
    log_config_artifacts,
    log_metrics_dict,
)
from detection_dentaire.mlops.mlflow_utils import log_dict_as_params
from detection_dentaire.utils import (
    load_yaml,
    load_params,
    project_root,
    resolve_project_path,
    ensure_dir,
    save_json,
    set_global_seed,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate a YOLO checkpoint on eval, test and external splits."
    )
    parser.add_argument(
        "--eval-config",
        type=str,
        default="configs/eval.yaml",
        help="Path to the evaluation config file relative to the project root.",
    )
    parser.add_argument(
        "--mlflow-config",
        type=str,
        default="configs/mlflow.yaml",
        help="Path to the MLflow config file relative to the project root.",
    )
    return parser.parse_args()


def build_eval_data_yaml(
    dataset_root: Path,
    split_images_rel: str,
    class_names_dict: dict[int, str],
    output_path: Path,
) -> Path:
    """
    Construit un YAML temporaire Ultralytics pour évaluer un split spécifique.
    On met le split ciblé dans la clé 'val' pour utiliser model.val().
    """
    ensure_dir(output_path.parent)
    names = [class_names_dict[i] for i in sorted(class_names_dict.keys())]

    payload = {
        "path": str(dataset_root.resolve()),
        "train": "train/images",
        "val": split_images_rel,
        "names": names,
        "nc": len(names),
    }

    with output_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)

    return output_path


def sanitize_metrics(raw_metrics: dict[str, Any]) -> dict[str, float]:
    """
    Nettoie les métriques YOLO pour les rendre loggables proprement.
    """
    cleaned = {}
    for key, value in raw_metrics.items():
        try:
            metric_value = float(value)
        except Exception:
            continue

        clean_key = (
            str(key)
            .replace("/", "_")
            .replace("(", "")
            .replace(")", "")
            .replace(" ", "_")
            .replace("%", "pct")
        )
        cleaned[clean_key] = metric_value

    return cleaned


def extract_yolo_metrics(results) -> dict[str, float]:
    """
    Extrait les métriques principales depuis l'objet retourné par Ultralytics.
    Fonction robuste avec fallback.
    """
    metrics: dict[str, float] = {}

    raw = getattr(results, "results_dict", None)
    if isinstance(raw, dict):
        metrics.update(sanitize_metrics(raw))

    box = getattr(results, "box", None)
    if box is not None:
        for attr_name, metric_name in [
            ("map", "box_map"),
            ("map50", "box_map50"),
            ("map75", "box_map75"),
            ("mp", "box_precision"),
            ("mr", "box_recall"),
        ]:
            value = getattr(box, attr_name, None)
            if value is not None:
                try:
                    metrics[metric_name] = float(value)
                except Exception:
                    pass

    return metrics


def main() -> None:
    args = parse_args()
    root = project_root()

    params = load_params(root / "params.yaml")
    data_cfg = load_yaml(root / "configs" / "data.yaml")
    eval_cfg_path = resolve_project_path(args.eval_config, base=root)
    mlflow_cfg_path = resolve_project_path(args.mlflow_config, base=root)
    eval_cfg = load_yaml(eval_cfg_path)
    mlflow_cfg = load_yaml(mlflow_cfg_path)

    set_global_seed(params["project"]["seed"])

    dataset_root = resolve_project_path(data_cfg["dataset"]["root"], base=root)
    checkpoint = resolve_project_path(eval_cfg["evaluation"]["checkpoint"], base=root)

    if not checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint}")

    class_names_dict = data_cfg["classes"]["names"]

    split_rel_paths = {
        "eval": "eval/images",
        "test": "test/images",
        "external": "test_alte_cabinete/Ext-validation/images",
    }

    enabled_splits = {
        "eval": bool(eval_cfg["splits"]["eval"]),
        "test": bool(eval_cfg["splits"]["test"]),
        "external": bool(eval_cfg["splits"]["external"]),
    }

    generated_dir = ensure_dir(root / "configs" / "generated" / "eval")
    output_metrics_path = root / eval_cfg["outputs"]["metrics_json"]
    ensure_dir(output_metrics_path.parent)

    model_name = checkpoint.parent.parent.name
    run_name = f"evaluate_{model_name}"

    all_metrics: dict[str, Any] = {
        "checkpoint": str(checkpoint),
        "dataset_root": str(dataset_root),
        "splits": {},
    }

    with start_run_with_configs(
        run_name=run_name,
        data_cfg=data_cfg,
        train_cfg=eval_cfg,
        mlflow_cfg=mlflow_cfg,
    ):
        mlflow.set_tag("project", params["project"]["name"])
        mlflow.set_tag("stage", "evaluation")
        mlflow.set_tag("checkpoint", str(checkpoint))

        log_dict_as_params("params", params)
        log_dict_as_params("data", data_cfg)
        log_dict_as_params("eval", eval_cfg)
        log_dict_as_params("mlflow", mlflow_cfg)

        log_config_artifacts(
            [
                root / "params.yaml",
                root / "configs" / "data.yaml",
                eval_cfg_path,
                mlflow_cfg_path,
                checkpoint,
            ]
        )

        model = YOLO(str(checkpoint))

        for split_name, enabled in enabled_splits.items():
            if not enabled:
                continue

            split_yaml = build_eval_data_yaml(
                dataset_root=dataset_root,
                split_images_rel=split_rel_paths[split_name],
                class_names_dict=class_names_dict,
                output_path=generated_dir / f"{split_name}_eval_data.yaml",
            )

            results = model.val(
                data=str(split_yaml),
                imgsz=eval_cfg["evaluation"]["image_size"],
                conf=eval_cfg["evaluation"]["conf_threshold"],
                iou=eval_cfg["evaluation"]["iou_threshold"],
                max_det=eval_cfg["evaluation"]["max_det"],
                device=eval_cfg["evaluation"]["device"],
                split="val",
            )

            metrics = extract_yolo_metrics(results)
            all_metrics["splits"][split_name] = metrics

            print(f"\n[OK] {split_name.upper()} metrics")
            for k, v in metrics.items():
                print(f"  - {k}: {v:.6f}")

            log_metrics_dict(metrics, prefix=f"{split_name}")

        save_json(all_metrics, output_metrics_path)
        mlflow.log_artifact(str(output_metrics_path))

        print(f"\n[OK] Metrics JSON saved to: {output_metrics_path}")
        print("[OK] Evaluation finished.")


if __name__ == "__main__":
    main()

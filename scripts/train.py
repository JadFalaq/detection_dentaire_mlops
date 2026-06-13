#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import mlflow

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from detection_dentaire.models import YOLOTrainer, build_ultralytics_data_yaml
from detection_dentaire.mlops import (
    start_run_with_configs,
    log_config_artifacts,
    log_training_summary,
)
from detection_dentaire.mlops.mlflow_utils import log_dict_as_params
from detection_dentaire.utils import (
    load_yaml,
    load_params,
    project_root,
    resolve_project_path,
    ensure_dir,
    set_global_seed,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train a YOLO dental detector from a selected config file."
    )
    parser.add_argument(
        "--train-config",
        type=str,
        default="configs/train.yaml",
        help="Path to the training config file relative to the project root.",
    )
    parser.add_argument(
        "--mlflow-config",
        type=str,
        default="configs/mlflow.yaml",
        help="Path to the MLflow config file relative to the project root.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = project_root()

    params = load_params(root / "params.yaml")
    data_cfg = load_yaml(root / "configs" / "data.yaml")
    train_cfg_path = resolve_project_path(args.train_config, base=root)
    mlflow_cfg_path = resolve_project_path(args.mlflow_config, base=root)
    train_cfg = load_yaml(train_cfg_path)
    mlflow_cfg = load_yaml(mlflow_cfg_path)

    set_global_seed(params["project"]["seed"])

    generated_dir = ensure_dir(root / "configs" / "generated")
    generated_name = f"yolo_data_{train_cfg['outputs']['run_name']}.yaml"
    yolo_data_yaml = build_ultralytics_data_yaml(
        data_cfg=data_cfg,
        output_path=generated_dir / generated_name,
    )

    run_name = train_cfg["experiment"]["name"]
    model_weights = resolve_project_path(train_cfg["model"]["variant"], base=root)

    # IMPORTANT: forcer les sorties dans le projet
    train_cfg["outputs"]["project_dir"] = str((root / train_cfg["outputs"]["project_dir"]).resolve())

    with start_run_with_configs(
        run_name=run_name,
        data_cfg=data_cfg,
        train_cfg=train_cfg,
        mlflow_cfg=mlflow_cfg,
    ):
        mlflow.set_tag("project", params["project"]["name"])
        mlflow.set_tag("stage", "training")
        mlflow.set_tag("model_type", train_cfg["model"]["type"])

        log_dict_as_params("params", params)
        log_dict_as_params("data", data_cfg)
        log_dict_as_params("train", train_cfg)
        log_dict_as_params("mlflow", mlflow_cfg)

        log_config_artifacts(
            [
                root / "params.yaml",
                root / "configs" / "data.yaml",
                train_cfg_path,
                mlflow_cfg_path,
                yolo_data_yaml,
            ]
        )

        trainer = YOLOTrainer(weights=model_weights)
        results = trainer.train(
            data_yaml=yolo_data_yaml,
            train_cfg=train_cfg,
        )

        run_dir = Path(train_cfg["outputs"]["project_dir"]) / train_cfg["outputs"]["run_name"]
        log_training_summary(results, run_dir)

        # Optionnel mais très utile: copie stable du meilleur modèle
        best_src = run_dir / "weights" / "best.pt"
        last_src = run_dir / "weights" / "last.pt"

        stable_dir = ensure_dir(root / "models" / "checkpoints" / train_cfg["outputs"]["run_name"] / "weights")

        if best_src.exists():
            shutil.copy2(best_src, stable_dir / "best.pt")
        if last_src.exists():
            shutil.copy2(last_src, stable_dir / "last.pt")

        print("[OK] Training finished.")
        print(f"[OK] Run directory: {run_dir}")
        print(f"[OK] Stable checkpoint dir: {stable_dir}")


if __name__ == "__main__":
    main()

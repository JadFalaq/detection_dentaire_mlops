from __future__ import annotations

from pathlib import Path
from typing import Any

import mlflow


def setup_mlflow(mlflow_cfg: dict[str, Any]) -> None:
    cfg = mlflow_cfg["mlflow"]
    mlflow.set_tracking_uri(cfg["tracking_uri"])
    mlflow.set_experiment(cfg["experiment_name"])


def start_run_with_configs(
    run_name: str,
    data_cfg: dict[str, Any],
    train_cfg: dict[str, Any],
    mlflow_cfg: dict[str, Any],
):
    setup_mlflow(mlflow_cfg)
    return mlflow.start_run(run_name=run_name)


def log_config_artifacts(config_paths: list[str | Path]) -> None:
    for path in config_paths:
        path = Path(path)
        if path.exists():
            mlflow.log_artifact(str(path))


def _flatten(prefix: str, obj: dict[str, Any], out: dict[str, Any]) -> None:
    for k, v in obj.items():
        key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            _flatten(key, v, out)
        else:
            out[key] = v


def log_dict_as_params(prefix: str, data: dict[str, Any]) -> None:
    flat: dict[str, Any] = {}
    _flatten(prefix, data, flat)

    # MLflow params doivent être simples
    for k, v in flat.items():
        if isinstance(v, (list, tuple)):
            mlflow.log_param(k, str(v))
        else:
            mlflow.log_param(k, v)


def log_training_summary(results, run_dir: str | Path) -> None:
    """
    Log minimal des artefacts et métriques après entraînement YOLO.
    """
    run_dir = Path(run_dir)

    # Artefacts classiques produits par Ultralytics
    candidates = [
        run_dir / "results.csv",
        run_dir / "args.yaml",
        run_dir / "weights" / "best.pt",
        run_dir / "weights" / "last.pt",
        run_dir / "confusion_matrix.png",
        run_dir / "F1_curve.png",
        run_dir / "P_curve.png",
        run_dir / "R_curve.png",
        run_dir / "PR_curve.png",
        run_dir / "results.png",
    ]

    for path in candidates:
        if path.exists():
            mlflow.log_artifact(str(path))

    # Si results.csv existe, il suffit souvent côté rapport.
    # Les métriques finales détaillées pourront être loggées plus tard via evaluate.py.




def log_metrics_dict(metrics: dict[str, float], prefix: str | None = None) -> None:
    """
    Log un dictionnaire de métriques dans MLflow.
    """
    for key, value in metrics.items():
        metric_name = f"{prefix}.{key}" if prefix else key
        try:
            mlflow.log_metric(metric_name, float(value))
        except Exception:
            continue
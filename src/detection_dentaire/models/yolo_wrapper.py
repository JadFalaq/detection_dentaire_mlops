from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from ultralytics import YOLO

from detection_dentaire.utils import ensure_dir, project_root, resolve_project_path


def build_ultralytics_data_yaml(
    data_cfg: dict[str, Any],
    output_path: str | Path,
) -> Path:
    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    root = project_root()
    dataset_root = resolve_project_path(data_cfg["dataset"]["root"], base=root)
    class_names_dict = data_cfg["classes"]["names"]
    names = [class_names_dict[i] for i in sorted(class_names_dict.keys())]
    try:
        dataset_path_value = dataset_root.relative_to(root).as_posix()
    except ValueError:
        dataset_path_value = str(dataset_root)

    yolo_cfg = {
        "path": dataset_path_value,
        "train": "train/images",
        "val": "eval/images",
        "test": "test/images",
        "names": names,
        "nc": len(names),
    }

    with output_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(yolo_cfg, f, sort_keys=False, allow_unicode=True)

    return output_path


class YOLOTrainer:
    def __init__(self, weights: str | Path) -> None:
        self.weights = str(weights)
        self.model = YOLO(self.weights)

    def train(
        self,
        data_yaml: str | Path,
        train_cfg: dict[str, Any],
    ):
        training = train_cfg["training"]
        outputs = train_cfg["outputs"]
        augmentation = train_cfg.get("augmentation", {})

        project_dir = Path(outputs["project_dir"]).resolve()
        ensure_dir(project_dir)

        train_kwargs = {
            "data": str(data_yaml),
            "imgsz": training["image_size"],
            "epochs": training["epochs"],
            "batch": training["batch_size"],
            "device": training["device"],
            "workers": training["workers"],
            "optimizer": training["optimizer"],
            "lr0": training["lr0"],
            "patience": training["patience"],
            "pretrained": training["pretrained"],
            "cache": training["cache"],
            "verbose": training["verbose"],
            "project": str(project_dir),
            "name": outputs["run_name"],
            "exist_ok": True,
        }

        consumed_training_keys = {
            "image_size",
            "epochs",
            "batch_size",
            "device",
            "workers",
            "optimizer",
            "lr0",
            "patience",
            "pretrained",
            "cache",
            "verbose",
        }
        for key, value in training.items():
            if key not in consumed_training_keys:
                train_kwargs[key] = value

        for key, value in augmentation.items():
            train_kwargs[key] = value

        results = self.model.train(**train_kwargs)
        return results

    def val(
        self,
        data_yaml: str | Path,
        eval_cfg: dict[str, Any],
    ):
        evaluation = eval_cfg["evaluation"]

        results = self.model.val(
            data=str(data_yaml),
            imgsz=evaluation["image_size"],
            conf=evaluation["conf_threshold"],
            iou=evaluation["iou_threshold"],
            max_det=evaluation["max_det"],
            device=evaluation["device"],
        )
        return results

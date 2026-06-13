from __future__ import annotations

from pathlib import Path
from typing import Any

from detection_dentaire.utils import ensure_dir, load_yaml, project_root, resolve_project_path


class YOLOPredictor:
    """
    Petit wrapper reutilisable autour de l'inference Ultralytics.
    """

    def __init__(self, checkpoint: str | Path) -> None:
        self.checkpoint = Path(checkpoint)
        self.model: Any | None = None

    def _get_model(self):
        if self.model is None:
            from ultralytics import YOLO

            self.model = YOLO(str(self.checkpoint))
        return self.model

    def predict(
        self,
        source: str | Path,
        *,
        image_size: int = 640,
        conf_threshold: float = 0.25,
        iou_threshold: float = 0.50,
        max_det: int = 300,
        device: int | str = 0,
        save_dir: str | Path | None = None,
        save_txt: bool = False,
        save_conf: bool = True,
        verbose: bool = True,
    ):
        save_dir_path = Path(save_dir).resolve() if save_dir else None
        if save_dir_path is not None:
            ensure_dir(save_dir_path)

        project = str(save_dir_path.parent) if save_dir_path is not None else None
        name = save_dir_path.name if save_dir_path is not None else None

        model = self._get_model()
        return model.predict(
            source=str(Path(source).resolve()),
            imgsz=image_size,
            conf=conf_threshold,
            iou=iou_threshold,
            max_det=max_det,
            device=device,
            save=save_dir_path is not None,
            save_txt=save_txt,
            save_conf=save_conf,
            project=project,
            name=name,
            exist_ok=True,
            verbose=verbose,
        )


def predictor_from_config(config_path: str | Path = "configs/infer.yaml") -> tuple[YOLOPredictor, dict]:
    root = project_root()
    cfg = load_yaml(resolve_project_path(config_path, base=root))
    inference = cfg["inference"]
    checkpoint = resolve_project_path(inference["checkpoint"], base=root)
    predictor = YOLOPredictor(checkpoint=checkpoint)
    return predictor, cfg

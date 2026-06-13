from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from detection_dentaire.inference.predictor import YOLOPredictor, predictor_from_config
from detection_dentaire.utils import load_yaml, project_root, resolve_project_path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


class PredictorService:
    def __init__(self, config_path: str | Path = "configs/infer.yaml") -> None:
        self.root = project_root()
        self.config_path = resolve_project_path(config_path, base=self.root)
        self._cfg: dict[str, Any] | None = None
        self._predictor: YOLOPredictor | None = None

    @property
    def cfg(self) -> dict[str, Any]:
        if self._cfg is None:
            self._cfg = load_yaml(self.config_path)
        return self._cfg

    @property
    def checkpoint_path(self) -> Path:
        return resolve_project_path(self.cfg["inference"]["checkpoint"], base=self.root)

    def model_name(self) -> str:
        checkpoint = self.checkpoint_path
        if checkpoint.parent.name == "weights":
            return checkpoint.parent.parent.name
        return checkpoint.stem

    def get_predictor(self) -> YOLOPredictor:
        if self._predictor is None:
            predictor, cfg = predictor_from_config(self.config_path)
            self._predictor = predictor
            self._cfg = cfg
        return self._predictor

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "service": "dental-detection-api",
            "config_path": str(self.config_path),
            "model_name": self.model_name(),
            "checkpoint_path": str(self.checkpoint_path),
            "checkpoint_exists": self.checkpoint_path.exists(),
            "model_loaded": self._predictor is not None,
        }

    def predict_uploaded_file(
        self,
        upload: UploadFile,
        *,
        image_size: int | None = None,
        conf_threshold: float | None = None,
        iou_threshold: float | None = None,
        max_det: int | None = None,
    ) -> dict[str, Any]:
        suffix = Path(upload.filename or "upload.jpg").suffix.lower()
        if suffix not in IMAGE_EXTS:
            raise HTTPException(status_code=400, detail="Unsupported image format.")

        predictor = self.get_predictor()
        inference_cfg = self.cfg["inference"]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(upload.file.read())
            temp_path = Path(tmp.name)

        try:
            results = predictor.predict(
                source=temp_path,
                image_size=image_size or inference_cfg["image_size"],
                conf_threshold=conf_threshold or inference_cfg["conf_threshold"],
                iou_threshold=iou_threshold or inference_cfg["iou_threshold"],
                max_det=max_det or inference_cfg["max_det"],
                device=inference_cfg["device"],
                save_dir=None,
                save_txt=False,
                save_conf=False,
                verbose=False,
            )
            if not results:
                return {
                    "model_name": self.model_name(),
                    "checkpoint_path": str(self.checkpoint_path),
                    "image_name": upload.filename,
                    "num_detections": 0,
                    "detections": [],
                }

            result = results[0]
            names = result.names
            detections: list[dict[str, Any]] = []
            orig_shape = getattr(result, "orig_shape", None)
            boxes = getattr(result, "boxes", None)
            if boxes is not None:
                xyxy = boxes.xyxy.cpu().tolist() if boxes.xyxy is not None else []
                confs = boxes.conf.cpu().tolist() if boxes.conf is not None else []
                clss = boxes.cls.cpu().tolist() if boxes.cls is not None else []
                for idx, bbox in enumerate(xyxy):
                    class_id = int(clss[idx])
                    detections.append(
                        {
                            "class_id": class_id,
                            "class_name": str(names[class_id]),
                            "confidence": float(confs[idx]),
                            "bbox_xyxy": [float(value) for value in bbox],
                        }
                    )

            return {
                "model_name": self.model_name(),
                "checkpoint_path": str(self.checkpoint_path),
                "image_name": upload.filename,
                "num_detections": len(detections),
                "image_width": int(orig_shape[1]) if orig_shape else None,
                "image_height": int(orig_shape[0]) if orig_shape else None,
                "settings": {
                    "image_size": image_size or inference_cfg["image_size"],
                    "conf_threshold": conf_threshold or inference_cfg["conf_threshold"],
                    "iou_threshold": iou_threshold or inference_cfg["iou_threshold"],
                    "max_det": max_det or inference_cfg["max_det"],
                },
                "detections": detections,
            }
        finally:
            temp_path.unlink(missing_ok=True)


def create_app(config_path: str | Path = "configs/infer.yaml") -> FastAPI:
    service = PredictorService(config_path=config_path)
    app = FastAPI(
        title="Dental Detection API",
        version="0.1.0",
        description="Inference API for panoramic dental anomaly detection.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/")
    def root() -> dict[str, Any]:
        return {
            "message": "Dental Detection API is running.",
            "docs": "/docs",
            "health": "/health",
            "predict": "/predict",
        }

    @app.get("/health")
    def health() -> dict[str, Any]:
        return service.health()

    @app.get("/model-info")
    def model_info() -> dict[str, Any]:
        return {
            "model_name": service.model_name(),
            "checkpoint_path": str(service.checkpoint_path),
            "checkpoint_exists": service.checkpoint_path.exists(),
            "config_path": str(service.config_path),
        }

    @app.post("/predict")
    def predict(
        file: UploadFile = File(...),
        image_size: int | None = Form(default=None),
        conf_threshold: float | None = Form(default=None),
        iou_threshold: float | None = Form(default=None),
        max_det: int | None = Form(default=None),
    ) -> JSONResponse:
        payload = service.predict_uploaded_file(
            file,
            image_size=image_size,
            conf_threshold=conf_threshold,
            iou_threshold=iou_threshold,
            max_det=max_det,
        )
        return JSONResponse(content=payload)

    return app

from __future__ import annotations

import io
import os
import tempfile
import threading
import time
from collections import deque
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

from detection_dentaire.inference.predictor import YOLOPredictor, predictor_from_config
from detection_dentaire.utils import load_yaml, project_root, resolve_project_path

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

MAX_UPLOAD_BYTES = 15 * 1024 * 1024
# Multipart framing around the file; requests above this Content-Length are rejected early.
MAX_REQUEST_BYTES = MAX_UPLOAD_BYTES + 64 * 1024
# A small file can decode to a huge bitmap; 40 MP is far above any panoramic radiograph.
MAX_IMAGE_PIXELS = 40_000_000

DEFAULT_ALLOWED_ORIGINS = (
    "https://snani.vercel.app",
    "https://detection-dentaire-mlops.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
)
# (max requests, window in seconds) per client IP on POST /predict.
DEFAULT_PREDICT_RATE_LIMITS = ((10, 60), (100, 3600))


class SlidingWindowRateLimiter:
    """In-memory limiter. Valid because the service runs on a single replica."""

    def __init__(self, limits: tuple[tuple[int, int], ...], max_tracked_clients: int = 5000) -> None:
        self.limits = limits
        self.longest_window = max(window for _, window in limits)
        self.max_tracked_clients = max_tracked_clients
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str, now: float | None = None) -> int:
        """Records the hit and returns 0 when allowed, otherwise the seconds to wait."""
        now = time.monotonic() if now is None else now
        with self._lock:
            hits = self._hits.setdefault(key, deque())
            while hits and now - hits[0] >= self.longest_window:
                hits.popleft()
            for max_requests, window in self.limits:
                recent = [hit for hit in hits if now - hit < window]
                if len(recent) >= max_requests:
                    return max(1, int(window - (now - recent[0])) + 1)
            hits.append(now)
            if len(self._hits) > self.max_tracked_clients:
                self._prune(now)
            return 0

    def _prune(self, now: float) -> None:
        stale = [key for key, hits in self._hits.items() if not hits or now - hits[-1] >= self.longest_window]
        for key in stale:
            del self._hits[key]


def client_ip(request: Request) -> str:
    # Azure Container Apps' ingress appends the real peer address as the last
    # X-Forwarded-For entry; earlier entries are client-controlled.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


def env_flag(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def allowed_origins_from_env() -> list[str]:
    value = os.getenv("ALLOWED_ORIGINS")
    if not value:
        return list(DEFAULT_ALLOWED_ORIGINS)
    return [origin.strip() for origin in value.split(",") if origin.strip()]


def read_limited(upload: UploadFile, limit: int) -> bytes:
    data = upload.file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(status_code=413, detail="File too large (max 15 MB).")
    return data


def validate_image(data: bytes) -> None:
    try:
        with Image.open(io.BytesIO(data)) as image:
            width, height = image.size
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError) as error:
        raise HTTPException(status_code=400, detail="Unsupported or corrupted image.") from error
    if width * height > MAX_IMAGE_PIXELS:
        raise HTTPException(status_code=413, detail="Image dimensions too large.")


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
            "model_name": self.model_name(),
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

        data = read_limited(upload, MAX_UPLOAD_BYTES)
        validate_image(data)

        predictor = self.get_predictor()
        inference_cfg = self.cfg["inference"]

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(data)
            temp_path = Path(tmp.name)

        settings = {
            "image_size": image_size or inference_cfg["image_size"],
            "conf_threshold": conf_threshold or inference_cfg["conf_threshold"],
            "iou_threshold": iou_threshold or inference_cfg["iou_threshold"],
            "max_det": max_det or inference_cfg["max_det"],
        }
        try:
            results = predictor.predict(
                source=temp_path,
                **settings,
                device=inference_cfg["device"],
                save_dir=None,
                save_txt=False,
                save_conf=False,
                verbose=False,
            )
            if not results:
                return {
                    "model_name": self.model_name(),
                    "image_name": upload.filename,
                    "num_detections": 0,
                    "settings": settings,
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
                "image_name": upload.filename,
                "num_detections": len(detections),
                "image_width": int(orig_shape[1]) if orig_shape else None,
                "image_height": int(orig_shape[0]) if orig_shape else None,
                "settings": settings,
                "detections": detections,
            }
        finally:
            temp_path.unlink(missing_ok=True)


def create_app(
    config_path: str | Path = "configs/infer.yaml",
    *,
    enable_docs: bool | None = None,
    allowed_origins: list[str] | None = None,
    predict_rate_limits: tuple[tuple[int, int], ...] = DEFAULT_PREDICT_RATE_LIMITS,
) -> FastAPI:
    service = PredictorService(config_path=config_path)
    docs_enabled = env_flag("API_DOCS_ENABLED", True) if enable_docs is None else enable_docs
    rate_limiter = SlidingWindowRateLimiter(predict_rate_limits)

    app = FastAPI(
        title="Dental Detection API",
        version="0.2.0",
        description="Inference API for panoramic dental anomaly detection.",
        docs_url="/docs" if docs_enabled else None,
        redoc_url="/redoc" if docs_enabled else None,
        openapi_url="/openapi.json" if docs_enabled else None,
    )

    @app.middleware("http")
    async def guard_predict(request: Request, call_next):
        # Runs before the multipart body is parsed, so rejected requests cost almost nothing.
        if request.method == "POST" and request.url.path == "/predict":
            length = request.headers.get("content-length")
            if length is None or not length.isdigit():
                return JSONResponse({"detail": "Content-Length required."}, status_code=411)
            if int(length) > MAX_REQUEST_BYTES:
                return JSONResponse({"detail": "File too large (max 15 MB)."}, status_code=413)
            retry_after = rate_limiter.check(client_ip(request))
            if retry_after:
                return JSONResponse(
                    {"detail": "Too many requests, please retry later."},
                    status_code=429,
                    headers={"Retry-After": str(retry_after)},
                )
        return await call_next(request)

    # Added last so it wraps the guard: 413/429 responses still carry CORS headers.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins if allowed_origins is not None else allowed_origins_from_env(),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
        expose_headers=["Retry-After"],
        max_age=600,
    )

    @app.get("/")
    def root() -> dict[str, Any]:
        return {"message": "Dental Detection API is running.", "health": "/health", "predict": "/predict"}

    @app.get("/health")
    def health() -> dict[str, Any]:
        return service.health()

    @app.get("/model-info")
    def model_info() -> dict[str, Any]:
        return {"model_name": service.model_name(), "checkpoint_exists": service.checkpoint_path.exists()}

    @app.post("/predict")
    def predict(
        file: UploadFile = File(...),
        image_size: int | None = Form(default=None, ge=320, le=1280),
        conf_threshold: float | None = Form(default=None, ge=0.05, le=0.95),
        iou_threshold: float | None = Form(default=None, ge=0.1, le=0.9),
        max_det: int | None = Form(default=None, ge=1, le=300),
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

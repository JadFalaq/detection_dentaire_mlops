from __future__ import annotations

from fastapi.testclient import TestClient

from detection_dentaire.serving.api import PredictorService, create_app


def test_health_endpoint(monkeypatch):
    def fake_health(self):
        return {
            "status": "ok",
            "service": "dental-detection-api",
            "checkpoint_exists": True,
            "model_loaded": False,
        }

    monkeypatch.setattr(PredictorService, "health", fake_health)

    client = TestClient(create_app())
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["checkpoint_exists"] is True


def test_predict_endpoint(monkeypatch):
    def fake_predict_uploaded_file(
        self,
        upload,
        *,
        image_size=None,
        conf_threshold=None,
        iou_threshold=None,
        max_det=None,
    ):
        return {
            "model_name": "champion",
            "checkpoint_path": "models/checkpoints/champion/weights/best.pt",
            "image_name": upload.filename,
            "num_detections": 1,
            "detections": [
                {
                    "class_id": 0,
                    "class_name": "CARIES",
                    "confidence": 0.91,
                    "bbox_xyxy": [1.0, 2.0, 3.0, 4.0],
                }
            ],
        }

    monkeypatch.setattr(PredictorService, "predict_uploaded_file", fake_predict_uploaded_file)

    client = TestClient(create_app())
    response = client.post(
        "/predict",
        files={"file": ("demo.jpg", b"fake-image-content", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["num_detections"] == 1
    assert payload["detections"][0]["class_name"] == "CARIES"


def _png_bytes(width: int = 8, height: int = 8) -> bytes:
    import io

    from PIL import Image

    buffer = io.BytesIO()
    Image.new("L", (width, height)).save(buffer, format="PNG")
    return buffer.getvalue()


def test_cors_allows_only_known_origins():
    client = TestClient(create_app(allowed_origins=["https://snani.example"]))
    preflight_headers = {"Access-Control-Request-Method": "POST"}

    allowed = client.options("/predict", headers={"Origin": "https://snani.example", **preflight_headers})
    denied = client.options("/predict", headers={"Origin": "https://evil.example", **preflight_headers})

    assert allowed.headers.get("access-control-allow-origin") == "https://snani.example"
    assert "access-control-allow-origin" not in denied.headers


def test_docs_can_be_disabled():
    client = TestClient(create_app(enable_docs=False))

    assert client.get("/docs").status_code == 404
    assert client.get("/openapi.json").status_code == 404


def test_predict_rejects_out_of_range_parameters():
    client = TestClient(create_app())

    response = client.post(
        "/predict",
        files={"file": ("radio.png", _png_bytes(), "image/png")},
        data={"image_size": "10000"},
    )

    assert response.status_code == 422


def test_predict_rejects_oversized_request():
    client = TestClient(create_app())
    too_big = b"0" * (15 * 1024 * 1024 + 128 * 1024)

    response = client.post("/predict", files={"file": ("radio.jpg", too_big, "image/jpeg")})

    assert response.status_code == 413


def test_predict_rejects_non_image_content():
    client = TestClient(create_app())

    response = client.post("/predict", files={"file": ("radio.jpg", b"not-an-image", "image/jpeg")})

    assert response.status_code == 400


def test_predict_rejects_huge_image_dimensions():
    client = TestClient(create_app())

    response = client.post(
        "/predict",
        files={"file": ("radio.png", _png_bytes(8000, 6000), "image/png")},
    )

    assert response.status_code == 413


def test_predict_is_rate_limited_per_client(monkeypatch):
    monkeypatch.setattr(PredictorService, "predict_uploaded_file", lambda self, upload, **kwargs: {"detections": []})
    client = TestClient(create_app(predict_rate_limits=((2, 60),)))

    def call(ip: str):
        return client.post(
            "/predict",
            files={"file": ("radio.png", _png_bytes(), "image/png")},
            headers={"X-Forwarded-For": f"1.2.3.4, {ip}"},
        )

    assert call("10.0.0.1").status_code == 200
    assert call("10.0.0.1").status_code == 200
    limited = call("10.0.0.1")
    assert limited.status_code == 429
    assert int(limited.headers["retry-after"]) > 0
    assert call("10.0.0.2").status_code == 200

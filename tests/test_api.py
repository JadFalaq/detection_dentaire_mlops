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

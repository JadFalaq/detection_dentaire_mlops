from __future__ import annotations

from detection_dentaire.data import load_yolo_label_file, validate_label_file


def test_load_yolo_label_file_parses_multiple_records(tmp_path):
    label_path = tmp_path / "sample.txt"
    label_path.write_text(
        "4 0.500000 0.500000 0.250000 0.250000\n"
        "7 0.250000 0.750000 0.100000 0.200000\n",
        encoding="utf-8",
    )

    records = load_yolo_label_file(label_path)

    assert records == [
        (4, 0.5, 0.5, 0.25, 0.25),
        (7, 0.25, 0.75, 0.1, 0.2),
    ]


def test_validate_label_file_reports_invalid_bbox(tmp_path):
    label_path = tmp_path / "invalid.txt"
    label_path.write_text("4 0.500000 0.500000 0.000000 0.250000\n", encoding="utf-8")

    report = validate_label_file(label_path, allowed_classes={4})

    assert report["valid"] is False
    assert report["num_objects"] == 1
    assert any("width/height must be > 0" in error for error in report["errors"])

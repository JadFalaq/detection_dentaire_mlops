from __future__ import annotations

from pathlib import Path
from typing import Iterable


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}


def collect_images(folder: str | Path) -> list[Path]:
    """
    Retourne toutes les images trouvées récursivement dans un dossier.
    """
    folder = Path(folder)
    if not folder.exists():
        return []
    return sorted(
        [p for p in folder.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS]
    )


def collect_labels(folder: str | Path) -> list[Path]:
    """
    Retourne tous les fichiers labels .txt trouvés récursivement dans un dossier.
    """
    folder = Path(folder)
    if not folder.exists():
        return []
    return sorted([p for p in folder.rglob("*.txt") if p.is_file()])


def find_split_dirs(root: str | Path) -> dict[str, dict[str, Path]]:
    """
    Détecte les splits du dataset selon ta structure actuelle.

    Structure attendue :
    root/
      train/images, train/labels
      valid/images, valid/labels
      test/images, test/labels
      test_alte_cabinete/Ext-validation/images, labels
    """
    root = Path(root)

    split_map = {
        "train": root / "train",
        "valid": root / "valid",
        "test": root / "test",
        "external": root / "test_alte_cabinete" / "Ext-validation",
    }

    out: dict[str, dict[str, Path]] = {}
    for split_name, split_root in split_map.items():
        image_dir = split_root / "images"
        label_dir = split_root / "labels"
        out[split_name] = {
            "root": split_root,
            "images": image_dir,
            "labels": label_dir,
        }
    return out


def infer_label_path_from_image(image_path: str | Path) -> Path:
    """
    Infère le chemin du label YOLO à partir du chemin d'une image
    en remplaçant 'images' par 'labels' et l'extension par .txt.
    """
    image_path = Path(image_path)
    parts = list(image_path.parts)

    if "images" not in parts:
        raise ValueError(f"Cannot infer label path because 'images' is not in {image_path}")

    idx = parts.index("images")
    parts[idx] = "labels"
    return Path(*parts).with_suffix(".txt")


def load_yolo_label_file(label_path: str | Path) -> list[tuple[int, float, float, float, float]]:
    """
    Charge un fichier label YOLO.

    Retour :
    [
      (class_id, x_center, y_center, width, height),
      ...
    ]
    """
    label_path = Path(label_path)
    if not label_path.exists():
        raise FileNotFoundError(f"Label file not found: {label_path}")

    text = label_path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    records: list[tuple[int, float, float, float, float]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        parts = line.strip().split()
        if len(parts) != 5:
            raise ValueError(f"{label_path} | line {line_no}: expected 5 values, got {len(parts)}")

        cls_id = int(float(parts[0]))
        xc = float(parts[1])
        yc = float(parts[2])
        bw = float(parts[3])
        bh = float(parts[4])

        records.append((cls_id, xc, yc, bw, bh))

    return records
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import cv2
import numpy as np


DEFAULT_CLASS_COLORS = {
    0: (0, 0, 255),      # red
    1: (255, 0, 0),      # blue
    2: (0, 255, 255),    # yellow
    3: (0, 255, 0),      # green
    4: (255, 0, 255),    # magenta
    5: (255, 165, 0),    # orange
    6: (128, 0, 128),    # purple
}


def yolo_to_xyxy(
    xc: float,
    yc: float,
    bw: float,
    bh: float,
    img_w: int,
    img_h: int,
) -> tuple[int, int, int, int]:
    """
    Convertit une bbox YOLO normalisée en coordonnées pixels (x1, y1, x2, y2).
    """
    x_center = xc * img_w
    y_center = yc * img_h
    box_w = bw * img_w
    box_h = bh * img_h

    x1 = int(round(x_center - box_w / 2))
    y1 = int(round(y_center - box_h / 2))
    x2 = int(round(x_center + box_w / 2))
    y2 = int(round(y_center + box_h / 2))

    x1 = max(0, min(x1, img_w - 1))
    y1 = max(0, min(y1, img_h - 1))
    x2 = max(0, min(x2, img_w - 1))
    y2 = max(0, min(y2, img_h - 1))

    return x1, y1, x2, y2


def draw_box_with_label(
    image: np.ndarray,
    box: tuple[int, int, int, int],
    label: str,
    color: tuple[int, int, int],
    thickness: int = 2,
    font_scale: float = 0.6,
) -> np.ndarray:
    """
    Dessine une bbox et son label sur une image.
    """
    x1, y1, x2, y2 = box
    cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness)

    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), baseline = cv2.getTextSize(label, font, font_scale, 1)

    text_y1 = max(0, y1 - th - baseline - 4)
    text_y2 = y1
    text_x1 = x1
    text_x2 = x1 + tw + 6

    cv2.rectangle(image, (text_x1, text_y1), (text_x2, text_y2), color, -1)
    cv2.putText(
        image,
        label,
        (x1 + 3, y1 - 4),
        font,
        font_scale,
        (255, 255, 255),
        1,
        cv2.LINE_AA,
    )
    return image


def annotate_yolo_image(
    image: np.ndarray,
    records: list[tuple[int, float, float, float, float]],
    class_names: dict[int, str],
    class_colors: dict[int, tuple[int, int, int]] | None = None,
    thickness: int = 2,
    font_scale: float = 0.6,
) -> np.ndarray:
    """
    Annote une image à partir d'une liste de records YOLO :
    [(class_id, xc, yc, bw, bh), ...]
    """
    if class_colors is None:
        class_colors = DEFAULT_CLASS_COLORS

    annotated = image.copy()
    img_h, img_w = annotated.shape[:2]

    for cls_id, xc, yc, bw, bh in records:
        box = yolo_to_xyxy(xc, yc, bw, bh, img_w, img_h)
        class_name = class_names.get(cls_id, f"class_{cls_id}")
        color = class_colors.get(cls_id, (255, 255, 255))

        draw_box_with_label(
            image=annotated,
            box=box,
            label=class_name,
            color=color,
            thickness=thickness,
            font_scale=font_scale,
        )

    return annotated


def save_image(image: np.ndarray, path: str | Path) -> Path:
    """
    Sauvegarde une image annotée.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    ok = cv2.imwrite(str(path), image)
    if not ok:
        raise RuntimeError(f"Failed to save image: {path}")

    return path
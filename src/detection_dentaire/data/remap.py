from __future__ import annotations


OLD_CLASS_NAMES = {
    0: "Implant",
    1: "Prosthetic restoration",
    2: "Obturation",
    3: "Endodontic treatment",
    4: "Carious lesion",
    5: "Bone resorbtion",
    6: "Impacted tooth",
    7: "Apical periodontitis",
    8: "Root fragment",
    9: "Furcation lesion",
    10: "Apical surgery",
    11: "Root resorption",
    12: "Orthodontic device",
    13: "Surgical device",
}

NEW_CLASS_NAMES = [
    "CARIES",
    "PERIAPICAL_PATHOLOGY",
    "PERIODONTAL_BONE",
    "IMPACTED_TOOTH",
    "ROOT_PATHOLOGY",
    "TREATED_TOOTH",
    "DEVICE_IMPLANT",
]

CLASS_REMAP = {
    0: 6,   # Implant -> DEVICE_IMPLANT
    1: 5,   # Prosthetic restoration -> TREATED_TOOTH
    2: 5,   # Obturation -> TREATED_TOOTH
    3: 5,   # Endodontic treatment -> TREATED_TOOTH
    4: 0,   # Carious lesion -> CARIES
    5: 2,   # Bone resorbtion -> PERIODONTAL_BONE
    6: 3,   # Impacted tooth -> IMPACTED_TOOTH
    7: 1,   # Apical periodontitis -> PERIAPICAL_PATHOLOGY
    8: 4,   # Root fragment -> ROOT_PATHOLOGY
    9: 2,   # Furcation lesion -> PERIODONTAL_BONE
    10: 5,  # Apical surgery -> TREATED_TOOTH
    11: 4,  # Root resorption -> ROOT_PATHOLOGY
    12: 6,  # Orthodontic device -> DEVICE_IMPLANT
    13: 6,  # Surgical device -> DEVICE_IMPLANT
}


def remap_records(
    records: list[tuple[int, float, float, float, float]]
) -> list[tuple[int, float, float, float, float]]:
    """
    Remappe une liste de records YOLO de 14 classes vers 7 classes.
    """
    remapped = []
    for cls_id, xc, yc, bw, bh in records:
        if cls_id not in CLASS_REMAP:
            raise ValueError(f"Unknown original class id: {cls_id}")
        new_cls = CLASS_REMAP[cls_id]
        remapped.append((new_cls, xc, yc, bw, bh))
    return remapped
from .io import (
    IMAGE_EXTS,
    collect_images,
    collect_labels,
    find_split_dirs,
    infer_label_path_from_image,
    load_yolo_label_file,
)
from .checks import (
    check_image_label_consistency,
    validate_yolo_record,
    validate_label_file,
)
from .remap import (
    OLD_CLASS_NAMES,
    NEW_CLASS_NAMES,
    CLASS_REMAP,
    remap_records,
)
from .stats import (
    compute_split_stats,
    aggregate_stats,
)

try:
    from .visualization import (
        DEFAULT_CLASS_COLORS,
        yolo_to_xyxy,
        draw_box_with_label,
        annotate_yolo_image,
        save_image,
    )
    _HAS_VISUALIZATION = True
except ModuleNotFoundError:
    _HAS_VISUALIZATION = False

__all__ = [
    "IMAGE_EXTS",
    "collect_images",
    "collect_labels",
    "find_split_dirs",
    "infer_label_path_from_image",
    "load_yolo_label_file",
    "check_image_label_consistency",
    "validate_yolo_record",
    "validate_label_file",
    "OLD_CLASS_NAMES",
    "NEW_CLASS_NAMES",
    "CLASS_REMAP",
    "remap_records",
    "compute_split_stats",
    "aggregate_stats",
]

if _HAS_VISUALIZATION:
    __all__.extend(
        [
            "DEFAULT_CLASS_COLORS",
            "yolo_to_xyxy",
            "draw_box_with_label",
            "annotate_yolo_image",
            "save_image",
        ]
    )

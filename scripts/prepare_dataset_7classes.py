#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import os
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from detection_dentaire.data import (
    CLASS_REMAP,
    NEW_CLASS_NAMES,
    OLD_CLASS_NAMES,
    collect_images,
    collect_labels,
    find_split_dirs,
    infer_label_path_from_image,
    validate_yolo_record,
)
from detection_dentaire.utils import ensure_dir, save_json


RAW_ALLOWED_CLASSES = set(CLASS_REMAP.keys())
NEW_CLASS_NAME_MAP = {idx: name for idx, name in enumerate(NEW_CLASS_NAMES)}
SPLIT_REMAP = {
    "train": Path("train"),
    "valid": Path("eval"),
    "test": Path("test"),
    "external": Path("test_alte_cabinete") / "Ext-validation",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare the dental YOLO dataset by remapping 14 classes to 7 classes."
    )
    parser.add_argument(
        "--src-root",
        type=str,
        required=True,
        help="Source raw dataset root, e.g. data/raw/dataset_original",
    )
    parser.add_argument(
        "--dst-root",
        type=str,
        required=True,
        help="Destination processed dataset root, e.g. data/processed/dataset_7classes",
    )
    parser.add_argument(
        "--copy-images",
        action="store_true",
        help="Copy images instead of creating hard links when possible.",
    )
    return parser.parse_args()


def reset_dir(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_or_link_file(src: Path, dst: Path, copy_images: bool) -> None:
    ensure_dir(dst.parent)
    if dst.exists():
        dst.unlink()

    if copy_images:
        shutil.copy2(src, dst)
        return

    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def format_record(record: tuple[int, float, float, float, float]) -> str:
    cls_id, xc, yc, bw, bh = record
    return f"{cls_id} {xc:.6f} {yc:.6f} {bw:.6f} {bh:.6f}"


def write_label_file(records: list[tuple[int, float, float, float, float]], dst_path: Path) -> None:
    ensure_dir(dst_path.parent)
    content = "\n".join(format_record(record) for record in records)
    dst_path.write_text(content, encoding="utf-8")


def sort_counter(counter: Counter[int]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter.keys())}


def rel_posix(path: Path, start: Path) -> str:
    return path.relative_to(start).as_posix()


def parse_and_remap_label_file(
    label_path: Path,
) -> tuple[list[tuple[int, float, float, float, float]], int, list[str], Counter[int], Counter[int]]:
    text = label_path.read_text(encoding="utf-8").strip()
    if not text:
        return [], 0, [], Counter(), Counter()

    remapped_records: list[tuple[int, float, float, float, float]] = []
    errors: list[str] = []
    old_counts: Counter[int] = Counter()
    new_counts: Counter[int] = Counter()
    invalid_lines = 0

    for line_no, line in enumerate(text.splitlines(), start=1):
        parts = line.strip().split()
        if len(parts) != 5:
            invalid_lines += 1
            errors.append(f"{label_path} | line {line_no}: expected 5 values, got {len(parts)}")
            continue

        try:
            cls_id = int(float(parts[0]))
            xc = float(parts[1])
            yc = float(parts[2])
            bw = float(parts[3])
            bh = float(parts[4])
        except ValueError:
            invalid_lines += 1
            errors.append(f"{label_path} | line {line_no}: non numeric values")
            continue

        record_errors = validate_yolo_record(
            cls_id=cls_id,
            xc=xc,
            yc=yc,
            bw=bw,
            bh=bh,
            allowed_classes=RAW_ALLOWED_CLASSES,
        )
        if record_errors:
            invalid_lines += 1
            for error in record_errors:
                errors.append(f"{label_path} | line {line_no}: {error}")
            continue

        new_cls_id = CLASS_REMAP[cls_id]
        remapped_records.append((new_cls_id, xc, yc, bw, bh))
        old_counts[cls_id] += 1
        new_counts[new_cls_id] += 1

    return remapped_records, invalid_lines, errors, old_counts, new_counts


def process_split(
    split_name: str,
    split_dirs: dict[str, Path],
    src_root: Path,
    dst_root: Path,
    copy_images: bool,
) -> tuple[str, dict[str, Any]]:
    image_dir = split_dirs["images"]
    label_dir = split_dirs["labels"]

    src_split_rel = rel_posix(split_dirs["root"], src_root)
    dst_split_rel = SPLIT_REMAP[split_name].as_posix()

    dst_image_dir = dst_root / SPLIT_REMAP[split_name] / "images"
    dst_label_dir = dst_root / SPLIT_REMAP[split_name] / "labels"
    ensure_dir(dst_image_dir)
    ensure_dir(dst_label_dir)

    images = collect_images(image_dir)
    labels = collect_labels(label_dir)
    image_stems = {image.stem for image in images}
    label_stems = {label.stem for label in labels}

    missing_labels_for_images: list[str] = []
    orphan_labels_without_images = sorted(label_stems - image_stems)
    split_errors: list[str] = []
    old_counts: Counter[int] = Counter()
    new_counts: Counter[int] = Counter()
    objects_total = 0
    invalid_lines = 0
    output_label_count = 0
    empty_label_files = 0

    for image_path in images:
        relative_image = image_path.relative_to(image_dir)
        dst_image_path = dst_image_dir / relative_image
        copy_or_link_file(image_path, dst_image_path, copy_images=copy_images)

        src_label_path = infer_label_path_from_image(image_path)
        dst_label_path = (dst_label_dir / relative_image).with_suffix(".txt")

        if not src_label_path.exists():
            missing_labels_for_images.append(image_path.stem)
            write_label_file([], dst_label_path)
            output_label_count += 1
            empty_label_files += 1
            continue

        records, file_invalid_lines, file_errors, file_old_counts, file_new_counts = parse_and_remap_label_file(
            src_label_path
        )
        write_label_file(records, dst_label_path)

        output_label_count += 1
        if not records:
            empty_label_files += 1

        invalid_lines += file_invalid_lines
        split_errors.extend(file_errors)
        old_counts.update(file_old_counts)
        new_counts.update(file_new_counts)
        objects_total += len(records)

    summary = {
        "src_split": src_split_rel,
        "dst_split": dst_split_rel,
        "num_images": len(images),
        "num_labels": output_label_count,
        "objects_total": objects_total,
        "empty_label_files": empty_label_files,
        "invalid_lines": invalid_lines,
        "missing_labels_for_images": sorted(missing_labels_for_images),
        "orphan_labels_without_images": orphan_labels_without_images,
        "old_class_counts": sort_counter(old_counts),
        "new_class_counts": sort_counter(new_counts),
        "errors": split_errors,
    }
    return src_split_rel, summary


def write_dataset_yaml(dst_root: Path) -> Path:
    yaml_path = dst_root / "data_7classes.yaml"
    payload = {
        "path": ".",
        "train": "train/images",
        "val": "eval/images",
        "test": "test/images",
        "external_val": "test_alte_cabinete/Ext-validation/images",
        "nc": len(NEW_CLASS_NAMES),
        "names": NEW_CLASS_NAME_MAP,
    }
    with yaml_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    return yaml_path


def write_labels_file(dst_root: Path) -> Path:
    labels_path = dst_root / "labels_7classes.txt"
    labels_path.write_text("\n".join(NEW_CLASS_NAMES) + "\n", encoding="utf-8")
    return labels_path


def write_mapping_file(dst_root: Path) -> Path:
    mapping_path = dst_root / "class_mapping_14_to_7.json"
    payload = {
        "old_class_names": {str(k): v for k, v in sorted(OLD_CLASS_NAMES.items())},
        "new_class_names": {str(i): name for i, name in enumerate(NEW_CLASS_NAMES)},
        "old_to_new": {str(k): int(v) for k, v in sorted(CLASS_REMAP.items())},
    }
    save_json(payload, mapping_path)
    return mapping_path


def main() -> None:
    args = parse_args()
    src_root = Path(args.src_root).resolve()
    dst_root = Path(args.dst_root).resolve()

    if not src_root.exists():
        raise FileNotFoundError(f"Source dataset root not found: {src_root}")

    reset_dir(dst_root)
    split_dirs = find_split_dirs(src_root)

    prepare_summary: dict[str, Any] = {}
    for split_name, dirs in split_dirs.items():
        key, summary = process_split(
            split_name=split_name,
            split_dirs=dirs,
            src_root=src_root,
            dst_root=dst_root,
            copy_images=args.copy_images,
        )
        prepare_summary[key] = summary

    dataset_yaml = write_dataset_yaml(dst_root)
    labels_file = write_labels_file(dst_root)
    mapping_file = write_mapping_file(dst_root)
    summary_path = dst_root / "prepare_summary.json"
    save_json(prepare_summary, summary_path)

    print("[OK] Dataset preparation finished.")
    print(f"[OK] Source root        : {src_root}")
    print(f"[OK] Destination root   : {dst_root}")
    print(f"[OK] Dataset YAML       : {dataset_yaml}")
    print(f"[OK] Labels file        : {labels_file}")
    print(f"[OK] Mapping file       : {mapping_file}")
    print(f"[OK] Summary JSON       : {summary_path}")


if __name__ == "__main__":
    main()

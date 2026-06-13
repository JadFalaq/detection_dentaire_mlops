from __future__ import annotations

from pathlib import Path
from typing import Any

from detection_dentaire.utils import ensure_dir


def flatten_split_metrics(metrics_payload: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Transforme le JSON d'evaluation en lignes simples exploitables.
    """
    rows: list[dict[str, Any]] = []
    for split_name, metrics in metrics_payload.get("splits", {}).items():
        for metric_name, value in metrics.items():
            rows.append(
                {
                    "split": split_name,
                    "metric": metric_name,
                    "value": value,
                }
            )
    return rows


def build_markdown_report(metrics_payload: dict[str, Any]) -> str:
    lines = [
        "# Evaluation Report",
        "",
        f"- Checkpoint: `{metrics_payload.get('checkpoint', 'N/A')}`",
        f"- Dataset root: `{metrics_payload.get('dataset_root', 'N/A')}`",
        "",
    ]

    for split_name, metrics in metrics_payload.get("splits", {}).items():
        lines.append(f"## {split_name}")
        lines.append("")
        if not metrics:
            lines.append("- No metrics available")
            lines.append("")
            continue

        for metric_name, value in sorted(metrics.items()):
            lines.append(f"- `{metric_name}`: {value}")
        lines.append("")

    return "\n".join(lines).strip() + "\n"


def save_markdown_report(metrics_payload: dict[str, Any], output_path: str | Path) -> Path:
    output_path = Path(output_path)
    ensure_dir(output_path.parent)
    output_path.write_text(build_markdown_report(metrics_payload), encoding="utf-8")
    return output_path

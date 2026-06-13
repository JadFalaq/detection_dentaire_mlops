#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from detection_dentaire.mlops import (
    infer_model_name_from_checkpoint,
    set_run_selection_tags,
    update_model_registry,
)
from detection_dentaire.utils import load_yaml, project_root, resolve_project_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Promote a checkpoint as Champion, Candidate or Archived."
    )
    parser.add_argument(
        "--checkpoint",
        required=True,
        help="Path to the checkpoint to register, relative to the project root.",
    )
    parser.add_argument(
        "--role",
        choices=["champion", "candidate", "archived"],
        default="champion",
        help="Registry role to assign to the checkpoint.",
    )
    parser.add_argument(
        "--model-name",
        default=None,
        help="Optional explicit model name. Defaults to the checkpoint parent run name.",
    )
    parser.add_argument(
        "--reason",
        required=True,
        help="Human-readable reason explaining the selection.",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional MLflow run id to tag with the selection role.",
    )
    parser.add_argument(
        "--registry-config",
        default="configs/model_registry.yaml",
        help="Path to the project registry config file.",
    )
    parser.add_argument(
        "--mlflow-config",
        default="configs/mlflow.yaml",
        help="Path to the MLflow config file.",
    )
    parser.add_argument(
        "--champion-alias",
        default="models/checkpoints/champion/weights/best.pt",
        help="Stable alias path used when promoting a Champion checkpoint.",
    )
    parser.add_argument(
        "--skip-mlflow-tags",
        action="store_true",
        help="Do not attempt to tag the MLflow run.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    root = project_root()

    checkpoint = resolve_project_path(args.checkpoint, base=root)
    registry_config = resolve_project_path(args.registry_config, base=root)
    mlflow_config = resolve_project_path(args.mlflow_config, base=root)
    champion_alias = resolve_project_path(args.champion_alias, base=root)

    model_name = args.model_name or infer_model_name_from_checkpoint(checkpoint)
    payload = update_model_registry(
        registry_config_path=registry_config,
        project_root=root,
        checkpoint_path=checkpoint,
        role=args.role,
        model_name=model_name,
        rationale=args.reason,
        source_run_id=args.run_id,
        champion_alias_path=champion_alias,
    )

    print(f"[OK] Modele enregistre comme {args.role.title()}: {model_name}")
    print(f"[OK] Checkpoint source: {checkpoint}")
    if args.role == "champion":
        print(f"[OK] Alias Champion: {champion_alias}")
    print(f"[OK] Registry config: {registry_config}")

    if args.run_id and not args.skip_mlflow_tags and mlflow_config.exists():
        mlflow_cfg = load_yaml(mlflow_config)
        tracking_uri = mlflow_cfg["mlflow"]["tracking_uri"]
        tag_status = set_run_selection_tags(
            tracking_uri=tracking_uri,
            run_id=args.run_id,
            role=args.role.title(),
            rationale=args.reason,
            model_name=model_name,
        )
        print(f"[INFO] MLflow tag status: {tag_status}")

    champion = payload.get("champion") or {}
    candidate = payload.get("candidate") or {}
    print(f"[INFO] Champion courant: {champion.get('name', '-')}")
    print(f"[INFO] Candidate courant: {candidate.get('name', '-')}")


if __name__ == "__main__":
    main()

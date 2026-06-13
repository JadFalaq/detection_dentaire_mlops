from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

import yaml

from detection_dentaire.utils import ensure_dir


def _relative_to_root(path: str | Path, root: str | Path) -> str:
    path = Path(path).resolve()
    root = Path(root).resolve()
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _load_registry_config(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    if not path.exists():
        return {
            "registry": {
                "project_model_name": "dental_anomaly_detector",
                "selection_policy": "best_global_compromise",
            },
            "champion": {},
            "candidate": {},
            "archived": [],
        }

    with path.open("r", encoding="utf-8") as f:
        payload = yaml.safe_load(f) or {}

    if not isinstance(payload, dict):
        raise ValueError(f"Invalid registry config: {path}")

    payload.setdefault("registry", {})
    payload.setdefault("champion", {})
    payload.setdefault("candidate", {})
    payload.setdefault("archived", [])
    return payload


def _save_registry_config(path: str | Path, payload: dict[str, Any]) -> Path:
    path = Path(path)
    ensure_dir(path.parent)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)
    return path


def infer_model_name_from_checkpoint(checkpoint_path: str | Path) -> str:
    checkpoint_path = Path(checkpoint_path)
    if checkpoint_path.suffix == ".pt" and checkpoint_path.parent.name == "weights":
        return checkpoint_path.parent.parent.name
    return checkpoint_path.stem


def promote_checkpoint_alias(
    source_checkpoint: str | Path,
    alias_checkpoint: str | Path,
) -> Path:
    source_checkpoint = Path(source_checkpoint)
    alias_checkpoint = Path(alias_checkpoint)

    if not source_checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint not found: {source_checkpoint}")

    ensure_dir(alias_checkpoint.parent)
    shutil.copy2(source_checkpoint, alias_checkpoint)
    return alias_checkpoint


def _build_registry_entry(
    *,
    role: str,
    model_name: str,
    checkpoint_path: str | Path,
    root: str | Path,
    rationale: str,
    source_run_id: str | None = None,
    alias_checkpoint: str | Path | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "name": model_name,
        "role": role,
        "checkpoint": _relative_to_root(checkpoint_path, root),
        "rationale": rationale,
    }

    if alias_checkpoint is not None:
        entry["checkpoint"] = _relative_to_root(alias_checkpoint, root)
        entry["source_checkpoint"] = _relative_to_root(checkpoint_path, root)

    if source_run_id:
        entry["source_run_id"] = source_run_id

    return entry


def _append_archived_entry(payload: dict[str, Any], entry: dict[str, Any]) -> None:
    archived = payload.setdefault("archived", [])
    archived = [item for item in archived if item.get("name") != entry.get("name")]
    archived.append(entry)
    payload["archived"] = archived


def update_model_registry(
    *,
    registry_config_path: str | Path,
    project_root: str | Path,
    checkpoint_path: str | Path,
    role: str,
    model_name: str | None = None,
    rationale: str,
    source_run_id: str | None = None,
    champion_alias_path: str | Path | None = None,
) -> dict[str, Any]:
    project_root = Path(project_root).resolve()
    checkpoint_path = Path(checkpoint_path).resolve()
    registry_config_path = Path(registry_config_path).resolve()
    role = role.title()

    if not checkpoint_path.exists():
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    if model_name is None:
        model_name = infer_model_name_from_checkpoint(checkpoint_path)

    payload = _load_registry_config(registry_config_path)
    alias_checkpoint: Path | None = None

    if role == "Champion":
        previous = payload.get("champion") or {}
        if previous.get("name") and previous.get("name") != model_name:
            archived_entry = {
                "name": previous.get("name"),
                "role": "Archived",
                "checkpoint": previous.get("source_checkpoint", previous.get("checkpoint")),
                "rationale": "ancien champion conserve pour historique",
            }
            if previous.get("source_run_id"):
                archived_entry["source_run_id"] = previous["source_run_id"]
            _append_archived_entry(payload, archived_entry)

        if champion_alias_path is None:
            champion_alias_path = project_root / "models" / "checkpoints" / "champion" / "weights" / "best.pt"
        alias_checkpoint = promote_checkpoint_alias(checkpoint_path, champion_alias_path)
        payload["champion"] = _build_registry_entry(
            role=role,
            model_name=model_name,
            checkpoint_path=checkpoint_path,
            root=project_root,
            rationale=rationale,
            source_run_id=source_run_id,
            alias_checkpoint=alias_checkpoint,
        )

        candidate = payload.get("candidate") or {}
        if candidate.get("name") == model_name:
            payload["candidate"] = {}

    elif role == "Candidate":
        payload["candidate"] = _build_registry_entry(
            role=role,
            model_name=model_name,
            checkpoint_path=checkpoint_path,
            root=project_root,
            rationale=rationale,
            source_run_id=source_run_id,
        )

    elif role == "Archived":
        _append_archived_entry(
            payload,
            _build_registry_entry(
                role=role,
                model_name=model_name,
                checkpoint_path=checkpoint_path,
                root=project_root,
                rationale=rationale,
                source_run_id=source_run_id,
            ),
        )
    else:
        raise ValueError(f"Unsupported role: {role}")

    _save_registry_config(registry_config_path, payload)
    return payload


def set_run_selection_tags(
    *,
    tracking_uri: str,
    run_id: str,
    role: str,
    rationale: str,
    model_name: str,
) -> str:
    try:
        from mlflow.tracking import MlflowClient
    except Exception as exc:  # pragma: no cover - depends on runtime environment
        return f"MLflow indisponible: {exc}"

    try:
        client = MlflowClient(tracking_uri=tracking_uri)
        client.set_tag(run_id, "selection_role", role)
        client.set_tag(run_id, "selection_reason", rationale)
        client.set_tag(run_id, "selected_model_name", model_name)
        return "ok"
    except Exception as exc:  # pragma: no cover - depends on active/deleted run state
        return str(exc)

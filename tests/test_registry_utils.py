from __future__ import annotations

from detection_dentaire.mlops.registry_utils import update_model_registry
from detection_dentaire.utils import load_yaml


def test_update_model_registry_sets_champion_and_alias(tmp_path):
    project_root = tmp_path / "project"
    checkpoint = project_root / "models" / "checkpoints" / "baseline" / "weights" / "best.pt"
    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    checkpoint.write_bytes(b"baseline")

    registry_path = project_root / "configs" / "model_registry.yaml"
    alias_path = project_root / "models" / "checkpoints" / "champion" / "weights" / "best.pt"

    payload = update_model_registry(
        registry_config_path=registry_path,
        project_root=project_root,
        checkpoint_path=checkpoint,
        role="Champion",
        model_name="baseline",
        rationale="meilleur compromis global",
        champion_alias_path=alias_path,
    )

    saved = load_yaml(registry_path)

    assert alias_path.exists()
    assert alias_path.read_bytes() == b"baseline"
    assert payload["champion"]["name"] == "baseline"

    # Normalise les séparateurs pour compatibilité Windows/Linux
    saved_checkpoint = saved["champion"]["checkpoint"].replace("\\", "/")
    saved_source = saved["champion"]["source_checkpoint"].replace("\\", "/")

    assert saved_checkpoint == "models/checkpoints/champion/weights/best.pt"
    assert saved_source == "models/checkpoints/baseline/weights/best.pt"


def test_update_model_registry_archives_previous_champion(tmp_path):
    project_root = tmp_path / "project"
    old_checkpoint = project_root / "models" / "checkpoints" / "baseline" / "weights" / "best.pt"
    new_checkpoint = project_root / "models" / "checkpoints" / "candidate" / "weights" / "best.pt"
    old_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    new_checkpoint.parent.mkdir(parents=True, exist_ok=True)
    old_checkpoint.write_bytes(b"old")
    new_checkpoint.write_bytes(b"new")

    registry_path = project_root / "configs" / "model_registry.yaml"
    alias_path = project_root / "models" / "checkpoints" / "champion" / "weights" / "best.pt"

    update_model_registry(
        registry_config_path=registry_path,
        project_root=project_root,
        checkpoint_path=old_checkpoint,
        role="Champion",
        model_name="baseline",
        rationale="ancien champion",
        champion_alias_path=alias_path,
    )

    update_model_registry(
        registry_config_path=registry_path,
        project_root=project_root,
        checkpoint_path=new_checkpoint,
        role="Champion",
        model_name="candidate",
        rationale="nouveau meilleur modele",
        champion_alias_path=alias_path,
    )

    saved = load_yaml(registry_path)
    archived_names = [item["name"] for item in saved["archived"]]

    assert saved["champion"]["name"] == "candidate"
    assert "baseline" in archived_names

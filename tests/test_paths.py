from __future__ import annotations

from detection_dentaire.utils import project_root, resolve_project_path


def test_project_root_and_resolve_project_path():
    root = project_root()

    assert root.name == "detection_dentaire_mlops"
    assert (root / "pyproject.toml").exists()
    assert resolve_project_path("configs/train.yaml") == (root / "configs" / "train.yaml").resolve()

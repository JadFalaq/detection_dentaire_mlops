from __future__ import annotations

import pytest

from detection_dentaire.utils import load_yaml


def test_load_yaml_returns_mapping(tmp_path):
    yaml_path = tmp_path / "config.yaml"
    yaml_path.write_text("project:\n  name: demo\nseed: 42\n", encoding="utf-8")

    data = load_yaml(yaml_path)

    assert data["project"]["name"] == "demo"
    assert data["seed"] == 42


def test_load_yaml_rejects_non_mapping_content(tmp_path):
    yaml_path = tmp_path / "invalid.yaml"
    yaml_path.write_text("- a\n- b\n", encoding="utf-8")

    with pytest.raises(ValueError, match="dictionary"):
        load_yaml(yaml_path)

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> dict[str, Any]:
    """
    Charge un fichier YAML et retourne son contenu sous forme de dictionnaire.

    Parameters
    ----------
    path : str | Path
        Chemin vers le fichier YAML.

    Returns
    -------
    dict[str, Any]
        Contenu du YAML.

    Raises
    ------
    FileNotFoundError
        Si le fichier n'existe pas.
    ValueError
        Si le contenu YAML n'est pas un dictionnaire.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        return {}

    if not isinstance(data, dict):
        raise ValueError(f"YAML content must be a dictionary: {path}")

    return data


def load_params(path: str | Path = "params.yaml") -> dict[str, Any]:
    """
    Charge le fichier params.yaml du projet.

    Parameters
    ----------
    path : str | Path, default="params.yaml"
        Chemin vers le fichier params.yaml.

    Returns
    -------
    dict[str, Any]
        Paramètres du projet.
    """
    return load_yaml(path)
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def save_json(data: Any, path: str | Path, indent: int = 2) -> Path:
    """
    Sauvegarde un objet Python en JSON.

    Parameters
    ----------
    data : Any
        Objet sérialisable JSON.
    path : str | Path
        Chemin de sortie.
    indent : int, default=2
        Indentation JSON.

    Returns
    -------
    Path
        Chemin du fichier sauvegardé.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=indent, ensure_ascii=False), encoding="utf-8")
    return path


def load_json(path: str | Path) -> Any:
    """
    Charge un fichier JSON.

    Parameters
    ----------
    path : str | Path
        Chemin du JSON.

    Returns
    -------
    Any
        Contenu du JSON.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {path}")

    return json.loads(path.read_text(encoding="utf-8"))
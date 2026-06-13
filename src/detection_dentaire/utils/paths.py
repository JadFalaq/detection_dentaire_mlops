from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """
    Retourne la racine du projet en remontant depuis ce fichier.

    Structure attendue :
    src/detection_dentaire/utils/paths.py
    -> racine = 3 niveaux au-dessus de src/

    Returns
    -------
    Path
        Racine du projet.
    """
    return Path(__file__).resolve().parents[3]


def resolve_project_path(path: str | Path, base: str | Path | None = None) -> Path:
    """
    Résout un chemin relatif par rapport à la racine du projet.

    Si le chemin fourni est déjà absolu, il est retourné tel quel.
    """
    path = Path(path)
    if path.is_absolute():
        return path

    if base is None:
        base = project_root()

    return (Path(base) / path).resolve()


def ensure_dir(path: str | Path) -> Path:
    """
    Crée un dossier s'il n'existe pas et retourne son Path.

    Parameters
    ----------
    path : str | Path
        Chemin du dossier à créer.

    Returns
    -------
    Path
        Chemin du dossier.
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

# Architecture

## Vue generale

Le projet suit une organisation simple de type MLOps :

- `scripts/` contient les points d'entree executables
- `src/detection_dentaire/` contient la logique reutilisable
- `configs/` centralise les parametres
- `data/` contient les donnees brutes et preparees
- `mlartifacts/` stocke les artefacts locaux MLflow

## Flux principal

1. `scripts/prepare_dataset_7classes.py`
   - lit le dataset YOLO brut
   - remappe 14 classes vers 7 classes
   - ecrit le dataset prepare dans `data/processed/dataset_7classes`

2. `scripts/inspect_dataset.py` et `scripts/verify_yolo_labels.py`
   - verifient la coherence images/labels
   - detectent les labels invalides ou les fichiers corrompus

3. `scripts/train.py`
   - charge les configurations
   - genere un YAML Ultralytics
   - lance l'entrainement YOLOv8
   - logue les artefacts dans MLflow

4. `scripts/evaluate.py`
   - evalue le modele sur plusieurs splits
   - consolide les metriques en JSON
   - logue les resultats dans MLflow

5. `scripts/predict.py`
   - applique le modele sur une image ou un dossier
   - sauvegarde les predictions dans `reports/predictions/`

## Modules source

- `data/` : IO, verification, remapping, stats, visualisation
- `models/` : wrapper YOLOv8 et generation du YAML Ultralytics
- `mlops/` : integration MLflow et aides MLOps
- `utils/` : chemins, YAML, JSON, seed

## Remarque

Plusieurs modules etaient initialement vides pour preparer une architecture plus large. Le noyau fonctionnel du projet est actuellement concentre dans les scripts et dans les modules `data/`, `models/`, `mlops/` et `utils/`.

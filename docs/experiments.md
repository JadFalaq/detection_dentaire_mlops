# Experiments

## Outil de suivi

Le suivi des experiences est gere avec MLflow.

Les parametres principaux sont dans `configs/mlflow.yaml` :

- `tracking_uri`
- `experiment_name`
- `registered_model_name`

## Entrainement

Commande principale :

```bash
python scripts/train.py
```

Ce script :

- charge `params.yaml` et les fichiers de configuration
- cree un run MLflow
- logue les configurations en artefacts
- lance YOLOv8 via Ultralytics
- logue les sorties principales du run

## Evaluation

Commande :

```bash
python scripts/evaluate.py
```

Les metriques d'evaluation sont :

- sauvegardees en local dans `reports/summaries/eval_metrics.json`
- loguees dans MLflow avec un prefixe par split

## Artefacts attendus

Selon le run, on retrouve en general :

- `weights/best.pt`
- `weights/last.pt`
- `results.csv`
- `results.png`
- `confusion_matrix.png`

## Bonnes pratiques pour la suite

Pour la suite du PFA, il est pertinent d'ajouter :

- comparaison automatique de plusieurs runs
- table de suivi des hyperparametres
- selection automatique du meilleur modele
- rapport markdown ou PDF a partir des metriques MLflow

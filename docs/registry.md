# Registry

## Etat actuel

Le projet contient deja une configuration de registry dans `configs/mlflow.yaml` avec le nom :

- `dental_anomaly_detector`

Le code actuel logue correctement les runs et les artefacts MLflow, mais la partie model registry reste encore minimale.

## Objectif vise

Le schema cible pour le PFA peut etre :

1. entrainer plusieurs variantes YOLOv8
2. comparer les metriques sur `eval`, `test` et `external`
3. selectionner le meilleur checkpoint
4. enregistrer ce checkpoint dans le registry MLflow
5. utiliser ce modele en inference et en demo

## Convention recommandee

- `Champion` : meilleur modele valide pour la demo
- `Candidate` : nouveau modele en cours de comparaison
- `Archived` : ancien modele conserve pour trace experimentale

## Prochaine etape possible

Une amelioration naturelle consiste a implementer un utilitaire `register_best_model.py` qui :

- lit un run MLflow
- recupere `best.pt`
- l'enregistre dans le registry
- ajoute les tags utiles du projet

## Etat actuel du projet

- `Champion` actuel : `yolov8s_7classes_baseline`
- `Candidate` actuel : `yolov8s_7classes_ext_generalization_v1`
- source de verite projet : `configs/model_registry.yaml`
- comparaison des performances : `reports/summaries/model_selection.md`

Le `Champion` est aussi expose via un alias de checkpoint stable :

- `models/checkpoints/champion/weights/best.pt`

Cette convention permet de changer de modele principal sans casser `train`, `evaluate` ou `predict`, car les configurations peuvent simplement pointer vers l'alias `Champion`.

## Commande de promotion

Le script projet pour promouvoir un checkpoint est :

```bash
python scripts/register_best_model.py --checkpoint models/checkpoints/yolov8s_7classes_ext_generalization_v1/weights/best.pt --role candidate --reason "meilleur sur external"
```

Pour remplacer le modele principal :

```bash
python scripts/register_best_model.py --checkpoint models/checkpoints/yolov8s_7classes_baseline/weights/best.pt --role champion --reason "meilleur compromis global"
```

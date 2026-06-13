# Detection Dentaire MLOps

Projet MLOps pour la detection d'anomalies et de maladies dentaires sur radiographies panoramiques.

## Objectif

Le projet vise a construire un pipeline reproductible de detection d'objets dentaires avec :

- preparation et controle qualite des donnees YOLO
- remapping de 14 classes vers 7 classes cliniques
- entrainement d'un detecteur YOLOv8
- suivi des experiences avec MLflow
- versionnage des donnees avec DVC
- evaluation sur `eval`, `test` et un split externe
- inference sur une image ou un dossier d'images

## Classes ciblees

Les 7 classes finales sont :

1. `CARIES`
2. `PERIAPICAL_PATHOLOGY`
3. `PERIODONTAL_BONE`
4. `IMPACTED_TOOTH`
5. `ROOT_PATHOLOGY`
6. `TREATED_TOOTH`
7. `DEVICE_IMPLANT`

## Structure du projet

```text
detection_dentaire_mlops/
├── configs/        # configurations train, eval, infer, MLflow
├── data/           # donnees DVC et donnees preparees
├── docs/           # documentation courte du projet
├── mlartifacts/    # artefacts locaux MLflow
├── scripts/        # points d'entree CLI
├── src/            # code Python reutilisable
├── tests/          # tests unitaires
├── dvc.yaml        # pipeline DVC
├── params.yaml     # parametres globaux
└── README.md
```

## Installation

Python 3.11 est recommande.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Pipeline de donnees

Le dataset brut est versionne avec DVC dans `data/raw/dataset_original.dvc`.

Le script de preparation principal est :

```bash
python scripts/prepare_dataset_7classes.py --src-root data/raw/dataset_original --dst-root data/processed/dataset_7classes --copy-images
```

Ce script :

- detecte les splits `train`, `valid`, `test` et `external`
- remappe les labels YOLO de 14 classes vers 7 classes
- genere `data_7classes.yaml`
- genere `class_mapping_14_to_7.json`
- genere `prepare_summary.json`

Pour executer le pipeline DVC :

```bash
dvc repro
```

## Entrainement

```bash
python scripts/train.py
```

Configurations utilisees :

- `params.yaml`
- `configs/data.yaml`
- `configs/train.yaml`
- `configs/mlflow.yaml`

Le script genere un `configs/generated/yolo_data.yaml` adapte a Ultralytics puis lance l'entrainement YOLOv8.

## Evaluation

```bash
python scripts/evaluate.py
```

Le script evalue le checkpoint configure sur :

- `eval`
- `test`
- `test_alte_cabinete/Ext-validation`

Les resultats consolides sont sauvegardes dans `reports/summaries/eval_metrics.json`.

## Inference

```bash
python scripts/predict.py --source path/to/image_or_folder
```

Le checkpoint utilise est defini dans `configs/infer.yaml` et reste maintenant relatif au projet.

## Registry du modele

Le modele principal du projet est expose via l'alias stable :

- `models/checkpoints/champion/weights/best.pt`

Pour promouvoir un checkpoint en `Champion`, `Candidate` ou `Archived` :

```bash
python scripts/register_best_model.py --checkpoint models/checkpoints/yolov8s_7classes_baseline/weights/best.pt --role champion --reason "meilleur compromis global"
```

La selection courante est tracee dans :

- `configs/model_registry.yaml`
- `reports/summaries/model_selection.md`

## Service API

Le modele `Champion` peut maintenant etre expose comme service HTTP :

```bash
pip install -r requirements-service.txt
python scripts/serve_api.py --host 127.0.0.1 --port 8000
```

Endpoints disponibles :

- `GET /health`
- `GET /model-info`
- `POST /predict`

Documentation interactive :

- [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Frontend Agent

Une interface React est disponible dans `frontend/` pour transformer le modele en demo interactive type agent :

- theme dentaire responsive
- upload par clic ou glisser-deposer
- preprocessing client-side avant envoi au modele
- reglages `image_size`, `conf_threshold`, `iou_threshold`, `max_det`
- reglages de luminosite et contraste
- affichage de l'image preprocessée avec bbox et predictions

Lancement local :

```bash
cd frontend
npm install
npm run dev
```

Par defaut, Vite utilise un proxy local vers `http://127.0.0.1:8000` via `/api`.
Si besoin, tu peux surcharger l'URL avec la variable d'environnement `VITE_API_BASE_URL`.

## CI/CD

Le projet contient maintenant :

- `.github/workflows/ci.yml` pour les tests et verifications CLI
- `.github/workflows/cd-service.yml` pour construire l'image Docker CPU du service
- `Dockerfile` pour packager l'API
- `requirements-service.txt` pour les dependances minimales du service CPU

Documentation detaillee :

- `docs/deployment.md`

## Tests

```bash
pytest -q
```

Les tests couvrent les utilitaires critiques :

- chargement YAML
- resolution de chemins projet
- parsing de labels YOLO
- validation des labels
- remapping des classes

## Documentation courte

- `docs/architecture.md`
- `docs/dataset.md`
- `docs/experiments.md`
- `docs/registry.md`

## Etat du projet

Le projet est maintenant organise pour etre plus facilement reproductible localement. Les axes suivants restent naturels pour la suite du PFA :

- ajout d'un vrai model registry operationnel
- ajout d'une API ou interface de demo
- enrichissement des rapports d'evaluation
- automatisation CI pour tests et verifications

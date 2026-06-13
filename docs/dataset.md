# Dataset

## Source

Le dataset brut est stocke dans `data/raw/dataset_original` et reference par DVC via `data/raw/dataset_original.dvc`.

La structure brute attendue est :

```text
dataset_original/
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── test_alte_cabinete/
    └── Ext-validation/
        ├── images/
        └── labels/
```

## Dataset prepare

Le dataset prepare est ecrit dans `data/processed/dataset_7classes/` avec la structure suivante :

```text
dataset_7classes/
├── train/
│   ├── images/
│   └── labels/
├── eval/
│   ├── images/
│   └── labels/
├── test/
│   ├── images/
│   └── labels/
└── test_alte_cabinete/
    └── Ext-validation/
        ├── images/
        └── labels/
```

Le split `valid` du dataset brut devient `eval` dans le dataset prepare.

## Remapping des classes

Les 14 classes d'origine sont regroupees en 7 classes :

- `CARIES`
- `PERIAPICAL_PATHOLOGY`
- `PERIODONTAL_BONE`
- `IMPACTED_TOOTH`
- `ROOT_PATHOLOGY`
- `TREATED_TOOTH`
- `DEVICE_IMPLANT`

Le mapping detaille est enregistre dans :

- `data/processed/dataset_7classes/class_mapping_14_to_7.json`
- `data/processed/dataset_7classes/labels_7classes.txt`

## Fichiers generes

Le script de preparation genere egalement :

- `prepare_summary.json` : resume par split
- `data_7classes.yaml` : YAML descriptif du dataset prepare

## Controle qualite

Les scripts utiles pour auditer le dataset sont :

```bash
python scripts/inspect_dataset.py --root data/processed/dataset_7classes --check-images --save-json reports/summaries/inspect_report.json
python scripts/verify_yolo_labels.py --root data/processed/dataset_7classes --save-json reports/summaries/labels_report.json
python scripts/class_stats.py --root data/processed/dataset_7classes --save-csv reports/tables/class_stats.csv --save-json reports/summaries/class_stats.json
```

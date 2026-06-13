# Deployment

## API locale

Le service d'inference expose le modele `Champion` via :

- `GET /`
- `GET /health`
- `GET /model-info`
- `POST /predict`

Lancement local :

```bash
pip install -r requirements-service.txt
python scripts/serve_api.py --host 127.0.0.1 --port 8000
```

Documentation interactive :

- `http://127.0.0.1:8000/docs`

## Exemple d'appel

Avec `curl` :

```bash
curl -X POST "http://127.0.0.1:8000/predict" -F "file=@path/to/image.jpg"
```

Le endpoint `POST /predict` accepte aussi les reglages suivants en formulaire multipart :

- `image_size`
- `conf_threshold`
- `iou_threshold`
- `max_det`

## Frontend local

Le frontend React/Vite du dossier `frontend/` fournit une interface de demo pour :

- uploader une radio dentaire
- reshaper et preprocesser l'image dans le navigateur
- envoyer l'image transformee au modele `Champion`
- afficher les bbox et predictions sur l'image

Lancement :

```bash
cd frontend
npm install
npm run dev
```

Configuration locale :

- Vite ecoute sur `http://127.0.0.1:5173`
- le proxy `/api` redirige vers `http://127.0.0.1:8000`
- `VITE_API_BASE_URL` permet d'utiliser une autre URL d'API si necessaire

## Docker

L'image Docker du projet est maintenant dediee au **service CPU** afin d'eviter le telechargement des grosses dependances CUDA dans le build.

Construction de l'image :

```bash
docker build -t dental-detection-api:latest .
```

Execution du conteneur :

```bash
docker run --rm -p 8000:8000 dental-detection-api:latest
```

Cette image s'appuie sur :

- `Dockerfile`
- `requirements-service.txt`

Elle est volontairement plus legere que l'environnement complet du projet et ne contient que les dependances necessaires au service d'inference.

## CI

Le workflow `.github/workflows/ci.yml` :

- installe le projet
- lance `pytest`
- verifie les points d'entree CLI principaux

## CD

Le workflow `.github/workflows/cd-service.yml` :

- reconstruit automatiquement l'image du service
- valide que le conteneur peut etre construit proprement

## Note importante

Pour une inference reelle, le checkpoint `Champion` doit etre present dans :

- `models/checkpoints/champion/weights/best.pt`

Si tu deployes sur une autre machine ou dans un conteneur de production, il faut :

- copier ce checkpoint
- ou le monter comme volume
- ou l'injecter via un stockage d'artefacts

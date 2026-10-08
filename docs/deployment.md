# Deployment

## Architecture de production

| Élément | Hébergement | Coût au repos |
|---|---|---|
| Frontend React (Snani) | Vercel — https://detection-dentaire-mlops.vercel.app | 0 |
| Image Docker de l'API | GitHub Container Registry — `ghcr.io/jadfalaq/dental-detection-api` | 0 (package public) |
| API d'inférence | Azure Container Apps, plan Consumption, **0 à 1 replica** | 0 |

L'API ne consomme des crédits Azure **que lorsqu'un visiteur fait un test réel** :

- le conteneur est à 0 replica au repos et démarre à la première requête HTTP ;
- il s'éteint ~5 minutes après la dernière requête ;
- le frontend n'appelle jamais l'API à l'ouverture de la page : il la réveille seulement quand le visiteur charge une radio (la sienne ou l'exemple) ;
- le CD ne fait plus de health-check de production à chaque push ;
- `max-replicas = 1` plafonne le coût même en cas de trafic anormal ;
- l'environnement est créé sans Log Analytics (pas de frais de logs).

Ordre de grandeur (France Central, 0,5 vCPU / 1 Gio) : 0,054 $ par heure active, soit
~0,005 $ par session de test de ~6 minutes. Le quota gratuit mensuel d'Azure Container Apps
(180 000 vCPU·s et 360 000 Gio·s) couvre ~100 heures actives, donc ~1 000 sessions par mois.

Le premier appel après une période d'inactivité prend 30 à 60 s (démarrage à froid) ; le
frontend affiche « Réveil de l'IA… » pendant ce temps.

## Déployer l'API sur Azure (première fois)

1. Installer Azure CLI et se connecter :

   ```powershell
   winget install -e --id Microsoft.AzureCLI
   az login
   ```

2. Publier l'image : pousser sur `master` déclenche le workflow CD, qui teste l'image puis la
   publie sur `ghcr.io/jadfalaq/dental-detection-api` (tags `latest` et SHA court).

3. Rendre le package public (une seule fois, sinon Azure ne peut pas le télécharger) :
   GitHub → profil → **Packages** → `dental-detection-api` → **Package settings** →
   **Change visibility** → **Public**.

4. Créer l'application Azure :

   ```powershell
   .\deploy\azure\deploy.ps1
   ```

   Le script est idempotent : le relancer met à jour l'application existante. Il affiche
   l'URL de l'API à la fin.

5. Brancher le frontend sur cette URL :
   - `frontend/.env.production` → `VITE_API_BASE_URL=https://<url-affichée>` ;
   - même variable dans Vercel → **Settings** → **Environment Variables**, puis redéployer ;
   - même valeur dans `.github/workflows/ci.yml` (étape « Build frontend »).

6. Recommandé : créer un budget avec alerte e-mail (portail Azure → **Cost Management** →
   **Budgets**, par exemple 5 $ par mois).

## Déploiement automatique à chaque push (optionnel)

Le job `deploy-azure` du CD met à jour l'image de l'application dès que ces réglages
existent dans le repo GitHub (**Settings** → **Secrets and variables** → **Actions**) :

- variable `AZURE_CONTAINERAPP` = `snani-api`
- variable `AZURE_RESOURCE_GROUP` = `rg-snani`
- secret `AZURE_CREDENTIALS` = sortie JSON de :

  ```powershell
  az ad sp create-for-rbac --name snani-github --role contributor `
    --scopes /subscriptions/<id-abonnement>/resourceGroups/rg-snani --json-auth
  ```

Certains abonnements « Azure for Students » interdisent la création de service principals
dans le tenant de l'université. Dans ce cas, il suffit de relancer `deploy.ps1` après chaque
nouvelle image.

## API locale

Le service d'inférence expose le modèle `Champion` via :

- `GET /`
- `GET /health`
- `GET /model-info`
- `POST /predict`

Lancement local (Python 3.10+) :

```bash
pip install -r requirements-service.txt
python scripts/serve_api.py --host 127.0.0.1 --port 8000
```

Documentation interactive : `http://127.0.0.1:8000/docs`

```bash
curl -X POST "http://127.0.0.1:8000/predict" -F "file=@path/to/image.jpg"
```

`POST /predict` accepte aussi `image_size`, `conf_threshold`, `iou_threshold` et `max_det`.

## Frontend local

```bash
cd frontend
npm install
npm run dev        # utilise l'API locale via le proxy /api -> http://127.0.0.1:8000
npm run dev:mock   # sans backend : réponses simulées (résultats fictifs)
```

## Docker

```bash
docker build -t dental-detection-api:latest .
docker run --rm -p 8000:8000 dental-detection-api:latest
```

L'image est dédiée au service CPU (`requirements-service.txt`) et embarque le checkpoint
`models/checkpoints/champion/weights/best.pt`.

<#
.SYNOPSIS
  Déploie l'API de détection dentaire sur Azure Container Apps en mode "scale-to-zero".

.DESCRIPTION
  - 0 replica au repos : aucune consommation tant que personne n'appelle l'API.
  - 1 replica maximum : le coût est plafonné même en cas de trafic anormal.
  - Aucun espace Log Analytics : pas de frais d'ingestion de logs.
  - Image publique sur ghcr.io : pas de registre Azure payant.

  Prérequis : Azure CLI installé et `az login` effectué.

.EXAMPLE
  .\deploy\azure\deploy.ps1
  .\deploy\azure\deploy.ps1 -Location westeurope
#>
param(
    [string]$ResourceGroup = 'rg-snani',
    [string]$Location = 'francecentral',
    [string]$EnvironmentName = 'snani-env',
    [string]$AppName = 'snani-api',
    [string]$Image = 'ghcr.io/jadfalaq/dental-detection-api:latest',
    [string]$Cpu = '0.5',
    [string]$Memory = '1.0Gi'
)

$ErrorActionPreference = 'Stop'

function Invoke-Az {
    & az @args
    if ($LASTEXITCODE -ne 0) {
        throw "La commande 'az $($args -join ' ')' a échoué (code $LASTEXITCODE)."
    }
}

# Windows PowerShell turns native stderr into terminating errors under 'Stop'.
function Test-AzResource {
    $previous = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    try {
        & az @args -o none 2>&1 | Out-Null
        return $LASTEXITCODE -eq 0
    }
    finally {
        $ErrorActionPreference = $previous
    }
}

Write-Host "==> Abonnement Azure utilisé" -ForegroundColor Cyan
Invoke-Az account show --query "{abonnement:name, id:id}" -o table

Write-Host "==> Préparation de la CLI et des fournisseurs" -ForegroundColor Cyan
Invoke-Az extension add --name containerapp --upgrade --only-show-errors
Invoke-Az provider register --namespace Microsoft.App --wait

Write-Host "==> Groupe de ressources $ResourceGroup ($Location)" -ForegroundColor Cyan
Invoke-Az group create --name $ResourceGroup --location $Location -o none

Write-Host "==> Environnement Container Apps $EnvironmentName (sans Log Analytics)" -ForegroundColor Cyan
if (-not (Test-AzResource containerapp env show --name $EnvironmentName --resource-group $ResourceGroup)) {
    Invoke-Az containerapp env create `
        --name $EnvironmentName `
        --resource-group $ResourceGroup `
        --location $Location `
        --logs-destination none `
        -o none
}

$scaleArgs = @(
    '--min-replicas', '0',
    '--max-replicas', '1',
    '--scale-rule-name', 'http-wake',
    '--scale-rule-type', 'http',
    '--scale-rule-http-concurrency', '10'
)

Write-Host "==> Application $AppName" -ForegroundColor Cyan
if (-not (Test-AzResource containerapp show --name $AppName --resource-group $ResourceGroup)) {
    Invoke-Az containerapp create `
        --name $AppName `
        --resource-group $ResourceGroup `
        --environment $EnvironmentName `
        --image $Image `
        --target-port 8000 `
        --ingress external `
        --cpu $Cpu `
        --memory $Memory `
        @scaleArgs `
        -o none
}
else {
    Invoke-Az containerapp update `
        --name $AppName `
        --resource-group $ResourceGroup `
        --image $Image `
        --cpu $Cpu `
        --memory $Memory `
        @scaleArgs `
        -o none
}

$fqdn = (& az containerapp show --name $AppName --resource-group $ResourceGroup `
        --query properties.configuration.ingress.fqdn -o tsv).Trim()

Write-Host ""
Write-Host "Déploiement terminé." -ForegroundColor Green
Write-Host "URL de l'API : https://$fqdn"
Write-Host ""
Write-Host "Étapes suivantes :"
Write-Host "  1. Mettre cette URL dans frontend/.env.production (VITE_API_BASE_URL)"
Write-Host "     et dans les variables d'environnement du projet Vercel."
Write-Host "  2. Ne PAS ouvrir cette URL pour tester sans raison : chaque appel réveille"
Write-Host "     le conteneur pendant ~5 minutes (c'est le seul moment où il consomme)."

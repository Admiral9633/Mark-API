# Quick Deploy Script für UGreen NAS mit DSM
# Führe dieses Script auf deinem Windows PC aus

param(
    [Parameter(Mandatory=$true)]
    [string]$NasIP,

    [Parameter(Mandatory=$false)]
    [string]$NasUser = "admin",

    [Parameter(Mandatory=$false)]
    [string]$DeployPath = "/volume1/docker/pdf-ocr"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PDF OCR - Quick Deploy auf UGreen NAS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ProjectPath = $PSScriptRoot

Write-Host "📋 Deployment-Info:" -ForegroundColor Yellow
Write-Host "  NAS IP: $NasIP"
Write-Host "  NAS User: $NasUser"
Write-Host "  Deploy Path: $DeployPath"
Write-Host "  Lokales Projekt: $ProjectPath"
Write-Host ""

# Teste SSH Verbindung
Write-Host "🔌 Teste SSH Verbindung..." -ForegroundColor Cyan
try {
    $testResult = ssh -o ConnectTimeout=5 "$NasUser@$NasIP" "echo 'OK'"
    if ($testResult -eq "OK") {
        Write-Host "  ✅ SSH Verbindung erfolgreich" -ForegroundColor Green
    }
} catch {
    Write-Host "  ❌ SSH Verbindung fehlgeschlagen!" -ForegroundColor Red
    Write-Host "  Bitte aktiviere SSH auf deinem NAS:" -ForegroundColor Yellow
    Write-Host "  DSM → Systemsteuerung → Terminal & SNMP → SSH aktivieren" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "📁 Erstelle Verzeichnis auf NAS..." -ForegroundColor Cyan
ssh "$NasUser@$NasIP" "mkdir -p $DeployPath"
Write-Host "  ✅ Verzeichnis erstellt" -ForegroundColor Green

Write-Host ""
Write-Host "📤 Kopiere Projekt-Dateien (dauert 2-5 Min)..." -ForegroundColor Cyan
Write-Host "  Bitte warten..." -ForegroundColor Yellow

# Wichtige Dateien kopieren
$filesToCopy = @(
    "docker-compose.yml",
    "docker-compose-marker-only.yml",
    "backend",
    "frontend",
    ".env.example",
    "dev.sh",
    "DEPLOYMENT_DSM.md",
    "QUICK_REFERENCE.md"
)

foreach ($file in $filesToCopy) {
    if (Test-Path $file) {
        Write-Host "  📄 Kopiere $file..." -ForegroundColor Gray
        scp -r "$ProjectPath\$file" "$NasUser@${NasIP}:$DeployPath/"
    }
}

Write-Host "  ✅ Dateien kopiert" -ForegroundColor Green

Write-Host ""
Write-Host "🐳 Starte Docker Container..." -ForegroundColor Cyan
ssh "$NasUser@$NasIP" "cd $DeployPath; sudo docker-compose down; sudo docker-compose up -d"

Write-Host ""
Write-Host "⏳ Warte 10 Sekunden..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "📊 Container Status:" -ForegroundColor Cyan
ssh "$NasUser@$NasIP" "cd $DeployPath; sudo docker-compose ps"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ Deployment abgeschlossen!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Deine Anwendung ist erreichbar unter:" -ForegroundColor Cyan
Write-Host "  Frontend:   http://${NasIP}:3000" -ForegroundColor White
Write-Host "  Backend:    http://${NasIP}:8000" -ForegroundColor White
Write-Host "  Marker-API: http://${NasIP}:8001" -ForegroundColor White
Write-Host ""
Write-Host "📋 Nächste Schritte:" -ForegroundColor Yellow
Write-Host "  1. Logs ansehen: ssh $NasUser@$NasIP 'cd $DeployPath && sudo docker-compose logs -f'"
Write-Host "  2. Browser öffnen: http://${NasIP}:3000"
Write-Host "  3. Beim ersten Start: Warte 5-10 Min (Modelle werden geladen)"
Write-Host ""
Write-Host "🐛 Bei Problemen:" -ForegroundColor Yellow
Write-Host "  ssh $NasUser@$NasIP"
Write-Host "  cd $DeployPath"
Write-Host "  sudo docker-compose logs -f"
Write-Host ""

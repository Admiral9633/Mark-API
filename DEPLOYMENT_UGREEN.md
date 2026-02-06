# PDF OCR System - Deployment auf UGreen NAS

## Voraussetzungen
- Docker und Docker Compose installiert
- Mindestens 8GB RAM verfügbar
- Ca. 10GB freier Speicher für Modelle

## Deployment Schritte

### 1. Projekt auf UGreen NAS kopieren
```bash
# Via SSH oder SMB das gesamte Projekt-Verzeichnis kopieren
scp -r /path/to/mark-api user@ugreen-nas:/volume1/docker/pdf-ocr/
```

### 2. Auf UGreen NAS einloggen
```bash
ssh user@ugreen-nas
cd /volume1/docker/pdf-ocr/
```

### 3. Docker Container starten
```bash
# Alle Container im Hintergrund starten
docker-compose up -d

# Logs ansehen
docker-compose logs -f

# Status prüfen
docker-compose ps
```

### 4. Beim ersten Start
Der erste Start dauert länger (5-10 Minuten), weil:
- PostgreSQL Datenbank initialisiert wird
- Django Migrationen laufen
- Marker-API die AI-Modelle herunterlädt (~5GB)

### 5. Zugriff
- Frontend: http://ugreen-nas-ip:3000
- Backend API: http://ugreen-nas-ip:8000
- Marker-API: http://ugreen-nas-ip:8001

### 6. Auf lokalem PC Frontend konfigurieren
Bearbeite `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://UGREEN-NAS-IP:8000
```

## GPU Unterstützung (optional)
Falls das UGreen NAS eine NVIDIA GPU hat:

1. Installiere NVIDIA Container Toolkit
2. In `docker-compose.yml` ändere:
   ```yaml
   marker-api:
     environment:
       - TORCH_DEVICE=cuda
       - MARKER_USE_GPU=1
     deploy:
       resources:
         reservations:
           devices:
             - driver: nvidia
               count: 1
               capabilities: [gpu]
   ```

## Wartung

### Container neustarten
```bash
docker-compose restart
```

### Logs ansehen
```bash
# Alle Services
docker-compose logs -f

# Nur ein Service
docker-compose logs -f marker-api
```

### Container stoppen
```bash
docker-compose down
```

### Volumes löschen (ACHTUNG: Löscht alle Daten!)
```bash
docker-compose down -v
```

### Updates
```bash
# Code aktualisieren
git pull  # oder Dateien manuell kopieren

# Container neu bauen und starten
docker-compose up -d --build
```

## Troubleshooting

### Marker-API startet nicht
- Prüfe Logs: `docker-compose logs marker-api`
- RAM prüfen: `docker stats`
- Image neu pullen: `docker-compose pull marker-api`

### Backend verbindet nicht zur Datenbank
- Warte 30 Sekunden nach Start (DB braucht Zeit)
- Prüfe DB Health: `docker-compose ps db`
- Logs: `docker-compose logs db`

### Frontend kann Backend nicht erreichen
- Prüfe CORS Einstellungen in `backend/pdf_ocr/settings.py`
- Frontend `.env.local` IP-Adresse korrekt?
- Firewall auf UGreen NAS prüfen

## Performance Optimierung

### Für schnellere OCR-Verarbeitung:
1. Mehr RAM für marker-api: In `docker-compose.yml` erhöhe `memory: 16G`
2. GPU nutzen (siehe oben)
3. Mehrere Worker: Marker-API unterstützt parallele Verarbeitung

### Für stabilen Betrieb:
```yaml
# In docker-compose.yml für alle Services:
restart: unless-stopped
deploy:
  resources:
    reservations:
      memory: 2G
    limits:
      memory: 4G
```

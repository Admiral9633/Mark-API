# Manuelle Deployment-Schritte für NAS 192.168.178.84

## Schritt 1: SSH testen
```powershell
ssh bjoern@192.168.178.84
# Passwort eingeben
# Wenn erfolgreich: exit
```

## Schritt 2: Ordner erstellen
```powershell
ssh bjoern@192.168.178.84 "mkdir -p /volume1/docker/pdf-ocr"
```

## Schritt 3: Dateien kopieren
```powershell
cd C:\Users\Administrator.BETRIEBSMEDIZIN\Documents\django\mark-api

# Docker Compose
scp docker-compose.yml bjoern@192.168.178.84:/volume1/docker/pdf-ocr/
scp docker-compose-marker-only.yml bjoern@192.168.178.84:/volume1/docker/pdf-ocr/

# Backend
scp -r backend bjoern@192.168.178.84:/volume1/docker/pdf-ocr/

# Frontend  
scp -r frontend bjoern@192.168.178.84:/volume1/docker/pdf-ocr/
```

## Schritt 4: Auf NAS einloggen und starten
```powershell
ssh bjoern@192.168.178.84
```

Dann auf dem NAS:
```bash
cd /volume1/docker/pdf-ocr
sudo docker-compose up -d
sudo docker-compose logs -f
```

## Alternative: Nur Marker-API
Einfacher und schneller:

```powershell
ssh bjoern@192.168.178.84
```

Auf dem NAS:
```bash
docker run -d --name marker-api \
  -p 8001:8000 \
  -v marker_cache:/root/.cache \
  --memory=12g \
  ghcr.io/adithya-s-k/marker-api:latest
```

Dann lokal auf PC:
```powershell
cd backend
echo "MARKER_API_URL=http://192.168.178.84:8001" > .env
python manage.py runserver
```

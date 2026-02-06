# 🚀 NAS Deployment - Ollama + Lexoffice Integration

## Quick Start (Automatisch)

```bash
# 1. Lokal: Committen & Pushen (neues PowerShell Fenster)
cd "C:\Users\Administrator.BETRIEBSMEDIZIN\Documents\django\mark-api"
git add .
git commit -m "Add: Ollama AI + Lexoffice integration"
git push

# 2. NAS: Deploy Script ausführen (SSH)
ssh bjoern@192.168.178.84
cd /volume1/docker/pdf-ocr
curl -sSL https://raw.githubusercontent.com/Admiral9633/Mark-API/main/deploy-ollama-nas.sh | sudo bash
```

## Manuell (Schritt für Schritt)

### 1️⃣ Git Push (Lokal - PowerShell)

```powershell
cd "C:\Users\Administrator.BETRIEBSMEDIZIN\Documents\django\mark-api"
git add .
git commit -m "Add: Ollama AI + Lexoffice integration"
git push
```

### 2️⃣ SSH zum NAS

```bash
ssh bjoern@192.168.178.84
# Passwort: Akk0n5481!
```

### 3️⃣ Ollama Container starten

```bash
# Ollama als Docker Container
sudo docker run -d \
  --name ollama \
  --restart unless-stopped \
  -p 11434:11434 \
  -v /volume1/docker/ollama:/root/.ollama \
  ollama/ollama

# Warten bis gestartet
sleep 5

# Llama3.2 Model herunterladen (~2GB, dauert 5-10 Min)
sudo docker exec ollama ollama pull llama3.2

# Test
curl http://localhost:11434/api/tags
# Sollte JSON mit Models zurückgeben
```

### 4️⃣ Ollama ins Netzwerk verbinden

```bash
sudo docker network connect pdf_ocr_network ollama
```

### 5️⃣ Code von GitHub holen

```bash
cd /volume1/docker/pdf-ocr

sudo wget https://github.com/Admiral9633/Mark-API/archive/refs/heads/main.zip -O main.zip
sudo unzip -o main.zip
sudo cp -r Mark-API-main/* .
sudo rm -rf Mark-API-main main.zip
```

### 6️⃣ .env Datei bearbeiten

```bash
sudo nano .env
```

**Füge hinzu:**
```env
# Ollama AI
OLLAMA_API_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2

# Lexoffice API
LEXOFFICE_API_KEY=whz6Oofxi0Hud2Y8947oU2-GNe3KlFJiTJ_BI_CzaSnW.oc.
LEXOFFICE_API_URL=https://api.lexware.io
```

**Speichern:** `Ctrl+X` → `Y` → `Enter`

### 7️⃣ Container neu starten

```bash
cd /volume1/docker/pdf-ocr

sudo docker-compose down
sudo docker-compose up -d

# Warten bis DB bereit ist
sleep 10

# Migrations ausführen
sudo docker-compose exec backend python manage.py migrate
```

### 8️⃣ Health Checks

```bash
# Backend Logs ansehen
sudo docker-compose logs backend | tail -50

# Alle Services prüfen
sudo docker-compose ps

# Sollte zeigen:
# - pdf_ocr_db        (healthy)
# - pdf_ocr_backend   (Up)
# - pdf_ocr_frontend  (Up)
# - pdf_ocr_marker    (Up)

# Ollama separat prüfen
sudo docker ps | grep ollama
curl http://localhost:11434/api/tags
```

### 9️⃣ Backend Test

```bash
# Test 1: Backend kann Ollama erreichen?
sudo docker-compose exec backend python3 -c "
import requests
try:
    r = requests.get('http://ollama:11434/api/tags', timeout=5)
    print('✅ Ollama erreichbar:', r.status_code == 200)
    print('Models:', r.json())
except Exception as e:
    print('❌ Ollama NICHT erreichbar:', e)
"

# Test 2: Environment Variablen gesetzt?
sudo docker-compose exec backend env | grep -E 'OLLAMA|LEXOFFICE'
```

### 🔟 PDF Upload testen

1. Öffne im Browser: **http://192.168.178.84:3000**
2. Lade eine Test-Rechnung hoch (z.B. Hornbach)
3. Beobachte Logs:

```bash
sudo docker-compose logs -f backend | grep -E "\[OCR\]|\[AI\]|\[LEXOFFICE\]"
```

**Erwartete Ausgabe:**
```
[OCR] Sende PDF an Marker-API: /app/media/pdfs/rechnung.pdf
[OCR] Marker-API erfolgreich, Markdown Length: 1234
[OCR] Dokument 1 erfolgreich verarbeitet
[AI] Starte Klassifizierung für Dokument 1
[AI] Klassifizierung abgeschlossen: is_invoice=True, type=incoming
[LEXOFFICE] Rechnung erkannt, starte Upload
[LEXOFFICE] Upload erfolgreich: file_id=abc-123-def
```

## 🐛 Troubleshooting

### Problem: Ollama nicht erreichbar

```bash
# Prüfen ob Container läuft
sudo docker ps | grep ollama

# Neu starten
sudo docker restart ollama

# Logs ansehen
sudo docker logs ollama

# Netzwerk prüfen
sudo docker network inspect pdf_ocr_network | grep ollama
```

### Problem: Model nicht gefunden

```bash
# Models auflisten
sudo docker exec ollama ollama list

# Model neu downloaden
sudo docker exec ollama ollama pull llama3.2
```

### Problem: Lexoffice Upload fehlschlägt

```bash
# API Key prüfen
sudo docker-compose exec backend env | grep LEXOFFICE_API_KEY

# Test mit curl
curl -H "Authorization: Bearer whz6Oofxi0Hud2Y8947oU2-GNe3KlFJiTJ_BI_CzaSnW.oc." \
     https://api.lexware.io/v1/profile
```

### Problem: Migration schlägt fehl

```bash
# Migrations nochmal ausführen
sudo docker-compose exec backend python manage.py migrate

# Oder Container neu bauen
sudo docker-compose down
sudo docker-compose up -d --build backend
sudo docker-compose exec backend python manage.py migrate
```

## 📊 Monitoring

### Container Status

```bash
sudo docker-compose ps
sudo docker stats --no-stream
```

### Logs Live ansehen

```bash
# Alle Logs
sudo docker-compose logs -f

# Nur Backend
sudo docker-compose logs -f backend

# Nur AI + Lexoffice
sudo docker-compose logs -f backend | grep -E "\[AI\]|\[LEXOFFICE\]"

# Ollama separat
sudo docker logs -f ollama
```

### Ressourcen Nutzung

```bash
# Speicher
df -h /volume1/docker/ollama
du -sh /volume1/docker/ollama/*

# Docker Volumes
sudo docker system df
```

## 🔄 Updates

Wenn du später Änderungen machst:

```bash
# 1. Lokal pushen
git push

# 2. Auf NAS updaten
cd /volume1/docker/pdf-ocr
sudo wget https://github.com/Admiral9633/Mark-API/archive/refs/heads/main.zip -O main.zip
sudo unzip -o main.zip
sudo cp -r Mark-API-main/* .
sudo rm -rf Mark-API-main main.zip

# 3. Neu starten
sudo docker-compose restart backend

# 4. Migrations (falls nötig)
sudo docker-compose exec backend python manage.py migrate
```

## 📱 URLs

- **Frontend**: http://192.168.178.84:3000
- **Backend API**: http://192.168.178.84:8000/api/
- **Marker-API**: http://192.168.178.84:8001
- **Ollama API**: http://192.168.178.84:11434
- **Lexoffice**: https://app.lexware.de/vouchers

## ✅ Fertig!

Das System läuft jetzt mit:
- ✅ OCR (Marker-API)
- ✅ AI Classification (Ollama + Llama3.2)
- ✅ Automatischer Lexoffice Upload
- ✅ Alle Daten auf NAS gespeichert

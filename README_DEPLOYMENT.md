# PDF OCR System - Deployment Optionen

## 🎯 Empfohlene Konfiguration: Hybrid Setup

**Problem gelöst:** Lokaler PC hat zu wenig RAM für AI-Modelle (5GB), UGreen NAS hat mehr RAM.

### Setup:
1. **Auf UGreen NAS:** Nur Marker-API (AI/OCR Service)
2. **Auf lokalem PC:** Django Backend + Next.js Frontend

### Vorteile:
- ✅ AI-Modelle laufen auf Server mit viel RAM
- ✅ Entwicklung bleibt lokal und schnell
- ✅ Keine RAM-Probleme mehr auf lokalem PC
- ✅ Frontend kann schnell geändert werden

---

## 🚀 Quick Start: Hybrid Setup

### 1. Auf UGreen NAS
```bash
# Via SSH auf UGreen
ssh user@UGREEN_IP

# Erstelle Verzeichnis
mkdir -p /volume1/docker/marker-api
cd /volume1/docker/marker-api

# Kopiere docker-compose-marker-only.yml auf UGreen
# Dann starte:
docker-compose -f docker-compose-marker-only.yml up -d

# Logs prüfen (dauert 5-10 Min beim ersten Start)
docker-compose logs -f marker-api
```

### 2. Auf lokalem PC

**Backend anpassen:**
```bash
cd backend
```

Erstelle `.env` Datei:
```env
DEBUG=True
SECRET_KEY=dev-key
DATABASE_URL=sqlite:///db.sqlite3
MARKER_API_URL=http://UGREEN_IP:8001
ALLOWED_HOSTS=*
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

Backend starten:
```bash
python manage.py migrate
python manage.py runserver
```

**Frontend starten:**
```bash
cd frontend
npm run dev
```

### 3. Testen
- Öffne: http://localhost:3000
- Lade eine PDF hoch
- OCR läuft jetzt auf UGreen NAS!

---

## 📦 Alternative: Komplett auf UGreen NAS

Alles (DB, Backend, Frontend, Marker-API) auf UGreen:

```bash
# Auf UGreen
cd /volume1/docker/pdf-ocr
docker-compose up -d

# Zugriff
http://UGREEN_IP:3000
```

Siehe [DEPLOYMENT_UGREEN.md](./DEPLOYMENT_UGREEN.md) für Details.

---

## 🔧 Troubleshooting

### Marker-API nicht erreichbar
```bash
# Auf UGreen
docker-compose logs marker-api
docker stats  # RAM Usage prüfen
```

### Backend kann Marker-API nicht erreichen
```bash
# Teste von lokalem PC
curl http://UGREEN_IP:8001/health

# Firewall auf UGreen prüfen
# Port 8001 muss erreichbar sein
```

### Erste OCR dauert sehr lange
- Normal! Beim ersten Upload lädt Marker-API die Modelle (~5GB)
- Danach sind sie gecacht und es geht schnell

---

## 📊 System Requirements

### UGreen NAS (für Marker-API):
- **RAM:** Mindestens 8GB, besser 12-16GB
- **Storage:** 10GB für Docker Images + Modelle
- **CPU:** Multi-Core empfohlen

### Lokaler PC:
- **RAM:** 4GB reichen (ohne AI-Modelle)
- Python 3.12, Node.js 20+

---

## 🎨 Entwicklung

### Code ändern und testen:
```bash
# Backend
cd backend
# Änderungen in api/views.py, api/models.py etc.
# Django reloaded automatisch

# Frontend
cd frontend
# Änderungen in components/, app/ etc.
# Next.js Hot Reload aktiv
```

### Nur Marker-API läuft auf UGreen, alles andere lokal = beste Entwicklererfahrung!

---

## 📝 Weitere Dokumentation

- [DEPLOYMENT_UGREEN.md](./DEPLOYMENT_UGREEN.md) - Vollständiges Deployment
- [QUICK_START.md](./QUICK_START.md) - Schnelleinstieg
- [test-deployment.sh](./test-deployment.sh) - Test-Script

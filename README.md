# 📄 PDF OCR System - Lokales Setup

Ein vollständig lokales System zum Hochladen und Verarbeiten von gescannten PDFs mit OCR und Struktur-Extraktion.

## 🧱 Architektur

- **Frontend**: Next.js 14 mit TypeScript & shadcn/ui
- **Backend**: Django + Django REST Framework
- **Datenbank**: MySQL 8.0
- **OCR**: Marker-API (Docker)

## 🚀 Schnellstart

### Voraussetzungen

- Docker & Docker Compose installiert
- Git installiert

### Installation

1. **Repository klonen**

```bash
cd c:\Users\Administrator.BETRIEBSMEDIZIN\Documents\django\mark-api
```

2. **Umgebungsvariablen anpassen (optional)**

Die `.env` Datei ist bereits erstellt. Für Production sollten Sie die Werte anpassen:

```bash
# .env bearbeiten
notepad .env
```

3. **Docker Container starten**

```bash
docker compose up -d
```

Dies startet:

- MySQL Datenbank (Port 3306)
- Marker-API OCR Service (Port 8001)
- Django Backend (Port 8000)
- Next.js Frontend (Port 3000)

4. **Datenbank initialisieren**

```bash
# Migrations ausführen
docker exec -it pdf_ocr_backend python manage.py migrate

# Admin-User erstellen (optional)
docker exec -it pdf_ocr_backend python manage.py createsuperuser
```

5. **Anwendung öffnen**

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Django Admin**: http://localhost:8000/admin/
- **Marker-API**: http://localhost:8001/docs

## 📁 Projektstruktur

```
mark-api/
├── docker-compose.yml          # Docker Orchestrierung
├── .env                        # Umgebungsvariablen
├── .env.example               # Beispiel-Konfiguration
├── backend/                    # Django Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── manage.py
│   ├── pdf_ocr/               # Django Projekt
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── api/                   # API App
│       ├── models.py          # Document Model
│       ├── views.py           # API Views
│       ├── serializers.py     # DRF Serializers
│       └── admin.py           # Admin Interface
└── frontend/                   # Next.js Frontend
    ├── Dockerfile
    ├── package.json
    ├── app/                   # App Router
    │   ├── page.tsx          # Hauptseite
    │   ├── layout.tsx        # Root Layout
    │   └── globals.css       # Global Styles
    └── components/            # React Komponenten
        ├── upload-zone.tsx   # Drag & Drop Upload
        ├── document-list.tsx # Dokumentliste
        └── ui/               # shadcn/ui Komponenten
```

## 🔄 Workflow

1. **PDF hochladen** - Drag & Drop oder Dateiauswahl
2. **OCR-Verarbeitung** - Automatische Weiterleitung an Marker-API
3. **Ergebnisse anzeigen** - Markdown & JSON Daten werden gespeichert
4. **Download** - Markdown-Export der OCR-Ergebnisse

## 🌐 API Endpoints

### Documents

- `GET /api/documents/` - Liste aller Dokumente
- `GET /api/documents/{id}/` - Einzelnes Dokument
- `POST /api/documents/convert/` - PDF hochladen & verarbeiten
  - Body: `multipart/form-data`
  - Field: `pdf_file` (max. 50MB)

### Beispiel cURL

```bash
curl -X POST http://localhost:8000/api/documents/convert/ \
  -F "pdf_file=@/pfad/zur/datei.pdf"
```

## 🗃️ Datenbank-Schema

### Document Model

```python
{
  "id": 1,
  "created_at": "2026-02-06T10:00:00Z",
  "updated_at": "2026-02-06T10:05:00Z",
  "original_filename": "rechnung.pdf",
  "pdf_file": "/media/pdfs/rechnung.pdf",
  "marker_markdown": "# Rechnung\n\n...",
  "marker_json": {...},
  "status": "completed",  # uploaded, processing, completed, error
  "error_message": null
}
```

## 🛠️ Entwicklung

### Backend Development

```bash
# Container betreten
docker exec -it pdf_ocr_backend bash

# Neue Migration erstellen
python manage.py makemigrations

# Migration ausführen
python manage.py migrate

# Shell öffnen
python manage.py shell
```

### Frontend Development

```bash
# Container betreten
docker exec -it pdf_ocr_frontend sh

# Dependencies installieren
npm install

# Build erstellen
npm run build
```

### Logs anzeigen

```bash
# Alle Container
docker compose logs -f

# Nur Backend
docker compose logs -f backend

# Nur Frontend
docker compose logs -f frontend

# Nur Marker
docker compose logs -f marker
```

## 🔧 Troubleshooting

### Container stoppen und neu starten

```bash
docker compose down
docker compose up -d
```

### Volumes löschen (Vorsicht: Datenverlust!)

```bash
docker compose down -v
```

### Datenbank-Verbindungsfehler

1. Sicherstellen, dass MySQL Container läuft:

```bash
docker compose ps
```

2. Logs prüfen:

```bash
docker compose logs db
```

3. Im Backend-Container testen:

```bash
docker exec -it pdf_ocr_backend python manage.py dbshell
```

### Marker-API antwortet nicht

1. Marker Container Logs prüfen:

```bash
docker compose logs marker
```

2. Health-Check:

```bash
curl http://localhost:8001/health
```

## 📊 Ressourcen & Performance

### Empfohlene Systemanforderungen

- **CPU**: 4+ Cores
- **RAM**: 8+ GB
- **Disk**: 20+ GB freier Speicher
- **Docker**: Version 24+

### Marker-API Performance

- Erste OCR-Verarbeitung kann länger dauern (Model-Download)
- Typische Verarbeitungszeit: 10-60 Sekunden pro Seite
- CPU-Modus ist langsamer als GPU-Modus

## 🔮 Roadmap

- [ ] Ollama Integration für KI-Analyse
- [ ] CSV/Excel Export
- [ ] Batch OCR Verarbeitung
- [ ] Benutzer-Authentifizierung
- [ ] Volltextsuche
- [ ] PDF Viewer Integration
- [ ] REST API Dokumentation (Swagger)
- [ ] Docker Compose für Synology optimieren

## 🛡️ Sicherheit

- ✅ 100% lokal - keine Cloud-Services
- ✅ Datenschutz-konform (DSGVO)
- ⚠️ Für Production: `DEBUG=False` setzen
- ⚠️ Für Production: `SECRET_KEY` ändern
- ⚠️ Für Production: `ALLOWED_HOSTS` konfigurieren

## 📝 Lizenz

Dieses Projekt ist für den privaten Gebrauch bestimmt.

## 🤝 Support

Bei Problemen:

1. Logs prüfen: `docker compose logs`
2. Container neu starten: `docker compose restart`
3. Volumes prüfen: `docker volume ls`

---

**Status**: ✅ Produktionsbereit für lokale Nutzung
**Version**: 1.0.0
**Datum**: Februar 2026

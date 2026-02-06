# 🚀 Quick Reference - Docker Development

## Wichtigste Commands

```bash
# Starten
docker-compose up -d

# Logs live
docker-compose logs -f

# Stoppen
docker-compose stop

# Neu starten
docker-compose restart
```

## Helper Script (Empfohlen!)

**Windows:**
```powershell
.\dev.ps1 start     # Alles starten
.\dev.ps1 logs      # Logs anzeigen
.\dev.ps1 status    # Status prüfen
.\dev.ps1 test      # Alle Services testen
```

**Linux/Mac:**
```bash
./dev.sh start
./dev.sh logs
./dev.sh status
./dev.sh test
```

## Code ändern - Was passiert?

| Datei geändert | Was passiert | Wartezeit |
|----------------|--------------|-----------|
| `backend/**/*.py` | Django Auto-Reload | 2-3 Sek |
| `frontend/**/*.tsx` | Next.js HMR | Sofort |
| `requirements.txt` | Rebuild nötig | `docker-compose build backend` |
| `package.json` | Rebuild nötig | `docker-compose build frontend` |
| `models.py` | Migration nötig | `docker-compose exec backend python manage.py migrate` |

## Häufige Aufgaben

### Django Migrations
```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

### Shell im Container
```bash
# Backend (Python)
docker-compose exec backend sh

# Frontend (Node)
docker-compose exec frontend sh

# Datenbank (PostgreSQL)
docker-compose exec db psql -U postgres -d pdf_ocr
```

### Django Management Commands
```bash
# Admin User erstellen
docker-compose exec backend python manage.py createsuperuser

# Django Shell
docker-compose exec backend python manage.py shell

# Tests ausführen
docker-compose exec backend python manage.py test
```

### NPM Pakete installieren
```bash
# Im Container
docker-compose exec frontend npm install package-name

# Oder lokal + restart
cd frontend
npm install package-name
docker-compose restart frontend
```

## URLs während Entwicklung

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api/
- **Django Admin:** http://localhost:8000/admin/
- **Marker-API:** http://localhost:8001
- **PostgreSQL:** localhost:5432

## Probleme lösen

```bash
# Container neu bauen
docker-compose build

# Alles neu starten
docker-compose down
docker-compose up -d

# Kompletter Reset (LÖSCHT DATEN!)
docker-compose down -v
docker-compose build
docker-compose up -d
```

## Ordnerstruktur

```
mark-api/
├── backend/          → Django, wird live in Container gemountet
│   ├── api/          → Deine Änderungen hier → Auto-Reload
│   ├── manage.py
│   └── requirements.txt
├── frontend/         → Next.js, wird live in Container gemountet
│   ├── app/          → Deine Änderungen hier → HMR
│   ├── components/
│   └── package.json
├── docker-compose.yml
└── dev.ps1 / dev.sh  → Helper Scripts
```

## Live-Entwicklung Workflow

1. **Starte Container:** `docker-compose up -d`
2. **Öffne Logs:** `docker-compose logs -f` (in separatem Terminal)
3. **Code ändern:** Editiere Dateien in `backend/` oder `frontend/`
4. **Speichern:** Automatisches Reload!
5. **Browser:** Änderungen sofort sichtbar

## Performance Tipps

- Logs nur bei Bedarf: `docker-compose logs -f backend`
- Nicht genutzter Container stoppen: `docker-compose stop marker-api`
- Regelmäßig aufräumen: `docker system prune`

## Cheat Sheet

| Aktion | Command |
|--------|---------|
| Start | `docker-compose up -d` |
| Stop | `docker-compose stop` |
| Restart | `docker-compose restart` |
| Logs | `docker-compose logs -f` |
| Shell | `docker-compose exec backend sh` |
| Migrate | `docker-compose exec backend python manage.py migrate` |
| Build | `docker-compose build` |
| Clean | `docker-compose down` |
| Status | `docker-compose ps` |

---

**Fertig! Happy Coding! 🎉**

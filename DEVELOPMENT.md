# Entwicklung mit Docker - Live Code Changes

## 🔥 Hot Reload ist aktiv!

Alle Code-Änderungen werden automatisch erkannt:
- **Django Backend:** Auto-Reload bei .py Änderungen
- **Next.js Frontend:** Hot Module Replacement (HMR)
- **Volumes:** Lokaler Code wird in Container gemountet

---

## 🚀 Entwicklung starten

### 1. Container starten
```bash
docker-compose up -d
```

### 2. Logs live verfolgen
```bash
# Alle Services
docker-compose logs -f

# Nur Backend
docker-compose logs -f backend

# Nur Frontend
docker-compose logs -f frontend
```

### 3. Code ändern
Editiere Dateien in:
- `backend/api/views.py` → Django lädt automatisch neu
- `frontend/app/page.tsx` → Next.js HMR aktiv
- `frontend/components/*.tsx` → Sofort im Browser sichtbar

### 4. Testen
Öffne: http://localhost:3000

---

## 📝 Häufige Entwicklungsaufgaben

### Backend: Django Migrations
```bash
# Migration erstellen
docker-compose exec backend python manage.py makemigrations

# Migration ausführen
docker-compose exec backend python manage.py migrate

# Admin-User erstellen
docker-compose exec backend python manage.py createsuperuser
```

### Backend: Django Shell
```bash
docker-compose exec backend python manage.py shell
```

### Frontend: NPM Pakete installieren
```bash
# Paket hinzufügen
docker-compose exec frontend npm install package-name

# Oder lokal (wird in Container synchronisiert)
cd frontend
npm install package-name
docker-compose restart frontend
```

### Datenbank: Direkter Zugriff
```bash
docker-compose exec db psql -U postgres -d pdf_ocr
```

### Container neu starten
```bash
# Alle
docker-compose restart

# Einzelner Service
docker-compose restart backend
```

---

## 🔍 Debugging

### Backend Logs live
```bash
docker-compose logs -f backend
```

### Frontend Logs live
```bash
docker-compose logs -f frontend
```

### In Container einsteigen
```bash
# Backend
docker-compose exec backend sh

# Frontend
docker-compose exec frontend sh

# Datenbank
docker-compose exec db psql -U postgres -d pdf_ocr
```

### Python Debugger (pdb)
In deinem Code:
```python
import pdb; pdb.set_trace()
```

Dann:
```bash
docker-compose attach backend
```

---

## 🎨 Workflow-Beispiele

### Neues Feature im Backend
1. Editiere `backend/api/views.py`
2. Django reloaded automatisch (siehe Logs)
3. Teste in Browser/Postman: http://localhost:8000/api/

### Neue React Component
1. Erstelle `frontend/components/MyComponent.tsx`
2. Importiere in `frontend/app/page.tsx`
3. Speichern → HMR zeigt sofort Änderung

### Datenbankschema ändern
1. Ändere `backend/api/models.py`
2. `docker-compose exec backend python manage.py makemigrations`
3. `docker-compose exec backend python manage.py migrate`
4. Django reloaded automatisch

### Dependencies aktualisieren
```bash
# Backend
cd backend
# Editiere requirements.txt
docker-compose build backend
docker-compose up -d backend

# Frontend
cd frontend
npm install new-package
docker-compose restart frontend
```

---

## 🐛 Troubleshooting

### Code-Änderungen werden nicht übernommen
```bash
# Container neu bauen
docker-compose build

# Mit Cache clearing
docker-compose build --no-cache

# Neu starten
docker-compose up -d
```

### Frontend HMR funktioniert nicht
```bash
# In docker-compose.yml ist WATCHPACK_POLLING=true gesetzt
# Das sollte es beheben. Sonst:
docker-compose restart frontend
docker-compose logs -f frontend
```

### Django lädt nicht neu
```bash
# Prüfe ob PYTHONUNBUFFERED=1 gesetzt ist
# Prüfe Logs:
docker-compose logs backend | grep -i reload
```

### Permission Probleme (Linux/Mac)
```bash
# Volumes gehören root:
docker-compose exec backend chown -R $(id -u):$(id -g) /app
```

### Kompletter Neustart
```bash
# Alles stoppen und löschen
docker-compose down -v

# Neu bauen und starten
docker-compose build
docker-compose up -d

# Migrationen
docker-compose exec backend python manage.py migrate
```

---

## 📊 Performance Tipps

### Für schnelleres Volume Mounting (Mac/Windows):
```yaml
# In docker-compose.yml bereits gesetzt:
volumes:
  - ./backend:/app:cached  # Cached read/write
```

### Marker-API auf separatem Server:
Nutze `docker-compose-marker-only.yml` auf UGreen NAS für bessere Performance.

---

## 🎯 Best Practices

1. **Logs beobachten** während Entwicklung: `docker-compose logs -f`
2. **Regelmäßig rebuilden** nach dependency changes
3. **Volumes nicht löschen** außer bei DB-Reset: `docker-compose down` (ohne `-v`)
4. **Tests schreiben** und in Container laufen lassen
5. **Hot Reload nutzen** - kein manuelles Neustarten nötig!

---

## 🚢 Von Dev zu Production

Wenn fertig entwickelt, für Production bauen:
```bash
# Production docker-compose
docker-compose -f docker-compose.prod.yml up -d
```

Siehe [docker-compose.prod.yml](./docker-compose.prod.yml) (noch zu erstellen).

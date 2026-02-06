# Komplettes Deployment auf UGreen NAS 4800plus

## Methode 1: Via DSM File Station (GUI - EMPFOHLEN)

### Schritt 1: Ordner vorbereiten

1. DSM öffnen: http://192.168.178.84:5000
2. File Station → docker → Neuer Ordner: `pdf-ocr`

### Schritt 2: Dateien hochladen

Öffne auf PC: `C:\Users\Administrator.BETRIEBSMEDIZIN\Documents\django\mark-api`

Lade folgende Ordner/Dateien in File Station hoch (nach `/docker/pdf-ocr/`):

- ✅ `backend/` (kompletter Ordner)
- ✅ `frontend/` (kompletter Ordner)
- ✅ `docker-compose.yml`
- ✅ `Dockerfile.marker-api`

**Tipp:** Packe alles in eine ZIP-Datei:

```powershell
# Auf PC
Compress-Archive -Path backend,frontend,docker-compose.yml,Dockerfile.marker-api -DestinationPath pdf-ocr.zip
```

Dann ZIP hochladen und auf NAS entpacken.

### Schritt 3: Via SSH auf NAS

```powershell
ssh bjoern@192.168.178.84
```

### Schritt 4: Container starten

```bash
cd /volume1/docker/pdf-ocr

# Prüfe ob Dateien da sind
ls -la

# Backend Dockerfile erstellen (falls nicht vorhanden)
# Frontend Dockerfile erstellen (falls nicht vorhanden)

# Starte alle Container
sudo docker-compose up -d

# Logs ansehen (beim ersten Start 10-15 Min warten!)
sudo docker-compose logs -f
```

### Schritt 5: Zugriff

- Frontend: http://192.168.178.84:3000
- Backend: http://192.168.178.84:8000
- Admin: http://192.168.178.84:8000/admin/

---

## Methode 2: Via WinSCP (Schneller Upload)

### Download WinSCP

https://winscp.net/eng/download.php

### Verbindung einrichten

- Host: 192.168.178.84
- Port: 22
- User: bjoern
- Passwort: [dein Passwort]

### Upload

1. Lokal: `C:\Users\Administrator.BETRIEBSMEDIZIN\Documents\django\mark-api`
2. Remote: `/volume1/docker/pdf-ocr/`
3. Drag & Drop alle Dateien

### SSH Container starten

```bash
ssh bjoern@192.168.178.84
cd /volume1/docker/pdf-ocr
sudo docker-compose up -d
sudo docker-compose logs -f
```

---

## Was beim ersten Start passiert

1. **PostgreSQL** startet (10s)
2. **Backend** baut Image und startet (2-3 Min)
3. **Frontend** baut Image und startet (3-5 Min)
4. **Marker-API** baut Image, lädt AI-Modelle (~5GB, 10-15 Min!)

**Gesamt: ~20 Minuten beim ersten Start**

---

## Troubleshooting

### Dateien fehlen auf NAS

```bash
# Prüfe
ssh bjoern@192.168.178.84
ls -la /volume1/docker/pdf-ocr/
```

### Docker Compose fehlt

```bash
# DSM 7 nutzt "docker compose" (ohne Bindestrich)
sudo docker compose up -d
```

### Container bauen fehlgeschlagen

```bash
# Logs ansehen
sudo docker-compose logs backend
sudo docker-compose logs frontend
sudo docker-compose logs marker-api
```

### Port bereits belegt

```bash
# Prüfe welche Ports verwendet werden
sudo netstat -tulpn | grep :3000
sudo netstat -tulpn | grep :8000
```

### Zu wenig Speicher

```bash
# Prüfe Docker Stats
sudo docker stats

# Reduziere Memory in docker-compose.yml
```

---

## Checkliste

- [ ] File Station: `/docker/pdf-ocr/` Ordner erstellt
- [ ] Alle Dateien hochgeladen (backend/, frontend/, docker-compose.yml)
- [ ] SSH eingeloggt auf NAS
- [ ] `sudo docker-compose up -d` ausgeführt
- [ ] Logs beobachtet: `sudo docker-compose logs -f`
- [ ] Nach 20 Min: Browser-Test http://192.168.178.84:3000
- [ ] PDF Upload getestet

---

## Nächste Schritte

Nach erfolgreichem Start:

1. Admin-User erstellen: `sudo docker-compose exec backend python manage.py createsuperuser`
2. Firewall Ports öffnen (falls von extern erreichbar)
3. Reverse Proxy einrichten (optional)
4. Backups einrichten

---

**Hinweis:** Der erste Start dauert lang weil Docker Images gebaut werden und Marker-API 5GB Modelle lädt!

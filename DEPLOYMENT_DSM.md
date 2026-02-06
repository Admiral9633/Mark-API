# Deployment auf UGreen NAS mit DSM (DiskStation Manager)

## Voraussetzungen auf dem UGreen NAS

- DSM 7.x installiert
- Container Manager (Docker) installiert
- SSH aktiviert (optional, aber empfohlen)
- Mindestens 8GB RAM verfügbar

---

## 🚀 Methode 1: Via File Station + SSH (Empfohlen)

### Schritt 1: SSH auf UGreen NAS aktivieren

1. DSM öffnen: http://UGREEN_IP:5000
2. Systemsteuerung → Terminal & SNMP
3. SSH-Dienst aktivieren
4. Port: 22 (Standard)

### Schritt 2: Projekt-Ordner auf NAS erstellen

Via File Station:

1. File Station öffnen
2. Navigiere zu `/docker/` (oder erstelle den Ordner)
3. Neuer Ordner: `pdf-ocr`

### Schritt 3: Projekt-Dateien hochladen

**Option A: Via File Station (GUI)**

1. File Station → `/docker/pdf-ocr/`
2. Hochladen → Ordner auswählen
3. Wähle das komplette `mark-api` Verzeichnis
4. ⚠️ **Kann bei vielen Dateien lange dauern**

**Option B: Via SCP (Schneller - Empfohlen)**

```powershell
# Von lokalem Windows PC
cd C:\Users\Administrator.BETRIEBSMEDIZIN\Documents\django\mark-api

# Komplettes Projekt kopieren
scp -r . admin@UGREEN_IP:/volume1/docker/pdf-ocr/

# Oder mit WinSCP (GUI Tool)
# Download: https://winscp.net/
```

**Option C: Via Git (Am besten für Updates)**

```bash
# Auf UGreen NAS via SSH
ssh admin@UGREEN_IP
cd /volume1/docker
git clone https://github.com/DEIN_USERNAME/mark-api.git pdf-ocr
# Oder: git init und dann manuell pushen
```

### Schritt 4: Via SSH auf NAS einloggen

```powershell
ssh admin@UGREEN_IP
```

### Schritt 5: Docker Container starten

```bash
cd /volume1/docker/pdf-ocr

# Container starten
sudo docker-compose up -d

# Logs ansehen (beim ersten Start 5-10 Min warten)
sudo docker-compose logs -f

# Status prüfen
sudo docker-compose ps
```

### Schritt 6: Zugriff testen

- Frontend: http://UGREEN_IP:3000
- Backend: http://UGREEN_IP:8000
- Marker-API: http://UGREEN_IP:8001

---

## 🎨 Methode 2: Via DSM Container Manager (GUI)

### Schritt 1: Container Manager öffnen

1. DSM → Paket-Zentrum
2. Suche "Container Manager"
3. Installieren (falls noch nicht installiert)
4. Container Manager öffnen

### Schritt 2: Projekt hochladen

1. File Station → Projekt-Dateien hochladen nach `/docker/pdf-ocr/`

### Schritt 3: Docker Compose via GUI

1. Container Manager → Projekt
2. "Erstellen" klicken
3. Name: `pdf-ocr`
4. Pfad: `/docker/pdf-ocr/docker-compose.yml`
5. "Erstellen" klicken

### Schritt 4: Container starten

1. Projekt auswählen
2. "Aktion" → "Starten"
3. Logs ansehen unter "Details"

---

## 🔧 Methode 3: Nur Marker-API auf NAS (Hybrid - Empfohlen für Entwicklung)

Falls du Backend + Frontend lokal auf deinem PC behalten willst:

### Auf UGreen NAS:

```bash
ssh admin@UGREEN_IP
cd /volume1/docker

# Nur marker-api starten
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  marker-api:
    image: ghcr.io/adithya-s-k/marker-api:latest
    container_name: marker-api
    restart: unless-stopped
    environment:
      - TORCH_DEVICE=cpu
      - MARKER_USE_GPU=0
    volumes:
      - marker_cache:/root/.cache
    ports:
      - "8001:8000"
    deploy:
      resources:
        limits:
          memory: 12G

volumes:
  marker_cache:
EOF

# Starten
sudo docker-compose up -d
```

### Auf lokalem PC:

```bash
cd backend

# .env erstellen
echo "MARKER_API_URL=http://UGREEN_IP:8001" > .env

# Backend starten
python manage.py runserver
```

```bash
cd frontend

# .env.local erstellen
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Frontend starten
npm run dev
```

**Vorteil:** Nur die RAM-intensive Marker-API läuft auf NAS, Rest lokal für schnelle Entwicklung!

---

## 📋 Detaillierte Schritt-für-Schritt mit Screenshots

### 1. File Station Setup

```
DSM Login → File Station → docker → Neuer Ordner "pdf-ocr"
```

### 2. SCP Upload (Windows PowerShell)

```powershell
# In deinem Projekt-Verzeichnis
cd C:\Users\Administrator.BETRIEBSMEDIZIN\Documents\django\mark-api

# Teste Verbindung
ssh admin@UGREEN_IP
# Passwort eingeben, dann exit

# Projekt kopieren (dauert 2-5 Min)
scp -r * admin@UGREEN_IP:/volume1/docker/pdf-ocr/

# Oder mit Ordnerstruktur
scp -r . admin@UGREEN_IP:/volume1/docker/pdf-ocr/mark-api
```

### 3. SSH auf NAS und Container starten

```bash
# SSH Login
ssh admin@UGREEN_IP

# Navigiere zum Projekt
cd /volume1/docker/pdf-ocr

# Prüfe ob Dateien da sind
ls -la

# Docker Compose starten
sudo docker-compose up -d

# Logs beobachten (Strg+C zum Beenden)
sudo docker-compose logs -f

# In separatem Terminal: Status prüfen
sudo docker-compose ps
```

### 4. Firewall Ports öffnen (falls nötig)

```
DSM → Systemsteuerung → Sicherheit → Firewall
Regel hinzufügen:
- Ports: 3000, 8000, 8001
- Protokoll: TCP
- Quelle: Alle
```

### 5. Zugriff testen

```powershell
# Von Windows PC
curl http://UGREEN_IP:8000/api/documents/
curl http://UGREEN_IP:8001/health
# Browser: http://UGREEN_IP:3000
```

---

## 🐛 Troubleshooting

### "Permission denied" bei SCP

```powershell
# Nutze WinSCP GUI Tool stattdessen
# Oder aktiviere root Login auf NAS
```

### "docker-compose: command not found"

```bash
# DSM 7 nutzt docker compose (ohne Bindestrich)
sudo docker compose up -d

# Oder nutze Container Manager GUI
```

### "Port already in use"

```bash
# Prüfe welche Ports belegt sind
sudo netstat -tulpn | grep :3000

# Ändere Ports in docker-compose.yml:
ports:
  - "3001:3000"  # Frontend auf 3001
```

### Container startet nicht - zu wenig RAM

```bash
# Prüfe RAM
free -h

# Reduziere Memory Limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 6G  # Statt 12G
```

### Erste OCR dauert ewig

```bash
# Normal! Marker-API lädt beim ersten Start Modelle (~5GB)
# Logs ansehen:
sudo docker-compose logs -f marker-api

# Warte bis du siehst: "Downloading ... model"
# Kann 10-15 Minuten dauern!
```

---

## 🔄 Updates einspielen

### Code-Änderungen übertragen

```powershell
# Von Windows PC
scp -r backend/api/views.py admin@UGREEN_IP:/volume1/docker/pdf-ocr/backend/api/

# Container neu starten
ssh admin@UGREEN_IP "cd /volume1/docker/pdf-ocr && sudo docker-compose restart backend"
```

### Komplettes Update

```bash
# Auf NAS
cd /volume1/docker/pdf-ocr

# Code pullen (falls Git)
git pull

# Container neu bauen und starten
sudo docker-compose down
sudo docker-compose build
sudo docker-compose up -d
```

---

## 📊 Monitoring

### Container Status anzeigen

```bash
sudo docker-compose ps
sudo docker stats
```

### Logs live verfolgen

```bash
sudo docker-compose logs -f backend
sudo docker-compose logs -f marker-api
```

### DSM Resource Monitor nutzen

```
DSM → Resource Monitor → Docker Container
```

---

## ✅ Checkliste

- [ ] SSH auf UGreen aktiviert
- [ ] Projekt-Ordner `/volume1/docker/pdf-ocr` erstellt
- [ ] Dateien via SCP/File Station hochgeladen
- [ ] Via SSH eingeloggt
- [ ] `docker-compose.yml` geprüft
- [ ] Container gestartet: `sudo docker-compose up -d`
- [ ] Logs gecheckt: `sudo docker-compose logs -f`
- [ ] Ports erreichbar: 3000, 8000, 8001
- [ ] Frontend im Browser getestet

---

**Fertig! Dein PDF-OCR läuft jetzt auf dem NAS! 🎉**

Bei Problemen: `sudo docker-compose logs -f` ansehen.

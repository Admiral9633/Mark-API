# 🚀 Schnellstart: Deployment auf UGreen NAS

## Option 1: Automatisches Deployment (Empfohlen)

### Voraussetzung: SSH aktiviert auf NAS

```powershell
# Auf Windows PC im Projekt-Ordner
cd C:\Users\Administrator.BETRIEBSMEDIZIN\Documents\django\mark-api

# Deploy Script ausführen
.\deploy-to-nas.ps1 -NasIP "192.168.1.XXX"

# Fertig! 🎉
```

Das war's! Öffne Browser: `http://192.168.1.XXX:3000`

---

## Option 2: Manuelles Deployment

### 1️⃣ SSH auf NAS aktivieren
```
DSM Login → Systemsteuerung → Terminal & SNMP → SSH aktivieren ✅
```

### 2️⃣ Projekt auf NAS kopieren
```powershell
# Windows PowerShell
cd C:\Users\Administrator.BETRIEBSMEDIZIN\Documents\django\mark-api

# Kopiere alles
scp -r . admin@192.168.1.XXX:/volume1/docker/pdf-ocr/
```

### 3️⃣ Via SSH auf NAS einloggen
```powershell
ssh admin@192.168.1.XXX
```

### 4️⃣ Container starten
```bash
cd /volume1/docker/pdf-ocr
sudo docker-compose up -d

# Logs ansehen
sudo docker-compose logs -f
```

### 5️⃣ Browser öffnen
```
http://192.168.1.XXX:3000
```

---

## Option 3: Nur Marker-API auf NAS (Hybrid)

**Am besten für Entwicklung!**

### Auf NAS:
```bash
ssh admin@192.168.1.XXX
mkdir -p /volume1/docker/marker-api
cd /volume1/docker/marker-api

# Docker Compose erstellen
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  marker-api:
    image: ghcr.io/adithya-s-k/marker-api:latest
    ports:
      - "8001:8000"
    volumes:
      - marker_cache:/root/.cache
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

### Auf Windows PC:
```powershell
# Backend
cd backend
echo "MARKER_API_URL=http://192.168.1.XXX:8001" > .env
python manage.py runserver

# Frontend (neues Terminal)
cd frontend
npm run dev
```

Öffne: `http://localhost:3000`

---

## ❓ Welche Option?

| Option | Wann nutzen | Performance |
|--------|-------------|-------------|
| **Option 1 - Auto** | Erstes Deployment | ⭐⭐⭐ |
| **Option 2 - Manuell** | Wenn du SSH kennst | ⭐⭐⭐ |
| **Option 3 - Hybrid** | Entwicklung | ⭐⭐⭐⭐⭐ |

**Empfehlung:** Starte mit Option 1 (Auto-Deploy), dann nutze Option 3 für Entwicklung.

---

## 🔧 Troubleshooting Quick Fixes

### SSH funktioniert nicht
```
DSM → Systemsteuerung → Terminal & SNMP → SSH aktivieren ✅
Firewall prüfen: Port 22 offen?
```

### Container startet nicht
```bash
ssh admin@NAS_IP
cd /volume1/docker/pdf-ocr
sudo docker-compose logs -f
```

### Ports nicht erreichbar
```
DSM → Systemsteuerung → Sicherheit → Firewall
Ports 3000, 8000, 8001 freigeben
```

### Zu wenig RAM
Nutze Option 3 (Hybrid) - nur Marker-API auf NAS.

---

## 📱 Nach dem Deployment

1. **Öffne Browser:** `http://NAS_IP:3000`
2. **Warte 5-10 Min** beim ersten Start (Modelle laden)
3. **Teste Upload:** PDF hochladen
4. **Logs checken:** `sudo docker-compose logs -f marker-api`

---

## 🎯 Nächste Schritte

- [ ] Deployment durchgeführt
- [ ] Browser-Test erfolgreich
- [ ] Erste PDF hochgeladen
- [ ] OCR funktioniert
- [ ] Code-Änderungen auf NAS übertragen können

**Siehe:** [DEVELOPMENT.md](./DEVELOPMENT.md) für Live-Code-Änderungen

---

**Viel Erfolg! 🚀**

Bei Fragen: Logs ansehen mit `sudo docker-compose logs -f`

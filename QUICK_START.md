# Quick Start für UGreen NAS Deployment

## Option 1: Gesamtes System auf UGreen

```bash
# 1. Projekt auf UGreen kopieren
scp -r mark-api/ user@ugreen-ip:/volume1/docker/

# 2. Auf UGreen
ssh user@ugreen-ip
cd /volume1/docker/mark-api
docker-compose up -d

# 3. Warte 5 Minuten (Modelle werden geladen)

# 4. Öffne Browser
http://ugreen-ip:3000
```

## Option 2: Nur Marker-API auf UGreen (empfohlen für Entwicklung)

Auf UGreen NAS nur die marker-api starten:

```bash
# docker-compose-marker-only.yml auf UGreen
docker-compose -f docker-compose-marker-only.yml up -d
```

Lokal auf PC:

```env
# backend/.env
MARKER_API_URL=http://ugreen-ip:8001
```

Dann Django + Next.js lokal starten wie bisher.

## Was ist der Vorteil?

- Marker-API läuft auf UGreen (viel RAM für AI-Modelle)
- Django + Next.js laufen lokal (schnellere Entwicklung)
- Beste Performance für OCR ohne lokalen RAM zu verbrauchen

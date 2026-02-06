# Docker Permission Fix für DSM/UGreen NAS

## Lösung 1: Mit sudo (Schnell)

```bash
sudo docker run -d --name marker-api \
  -p 8001:8000 \
  -v marker_cache:/root/.cache \
  --memory=12g \
  ghcr.io/adithya-s-k/marker-api:latest
```

## Lösung 2: User zur docker-Gruppe hinzufügen (Dauerhaft)

```bash
# Als root/admin
sudo usermod -aG docker bjoern

# Neu einloggen (oder neues Terminal)
exit
ssh bjoern@192.168.178.84

# Jetzt ohne sudo
docker run -d --name marker-api -p 8001:8000 -v marker_cache:/root/.cache --memory=12g ghcr.io/adithya-s-k/marker-api:latest
```

## Testen ob es läuft

```bash
# Container Status
sudo docker ps

# Logs ansehen
sudo docker logs -f marker-api

# Nach 2-3 Minuten testen
curl http://localhost:8001/health
```

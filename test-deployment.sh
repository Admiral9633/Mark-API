#!/bin/bash

# Test-Script für Marker-API Deployment

echo "=== PDF OCR System Test ==="
echo ""

# 1. Container Status prüfen
echo "1. Prüfe Container Status..."
docker-compose ps

echo ""
echo "2. Prüfe Marker-API Health..."
curl -f http://localhost:8001/health || echo "Marker-API nicht erreichbar!"

echo ""
echo "3. Prüfe Django Backend..."
curl -f http://localhost:8000/api/documents/ || echo "Backend nicht erreichbar!"

echo ""
echo "4. Prüfe PostgreSQL..."
docker-compose exec db pg_isready -U postgres || echo "Datenbank nicht bereit!"

echo ""
echo "5. RAM Usage:"
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}"

echo ""
echo "=== Test abgeschlossen ==="
echo "Wenn alle Checks OK sind, öffne: http://localhost:3000"

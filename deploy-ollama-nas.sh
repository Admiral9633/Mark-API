#!/bin/bash
# Deployment Script für NAS mit Ollama + Lexoffice Integration
# Verwendung: bash deploy-ollama-nas.sh

set -e  # Exit on error

echo "🚀 Deploying Ollama + Lexoffice Integration to NAS..."
echo "=================================================="

# 1. Ollama Container prüfen/starten
echo ""
echo "📦 Checking Ollama container..."
if ! sudo docker ps | grep -q ollama; then
    echo "   Starting Ollama container..."
    sudo docker run -d \
        --name ollama \
        --restart unless-stopped \
        -p 11434:11434 \
        -v /volume1/docker/ollama:/root/.ollama \
        ollama/ollama
    
    echo "   Waiting for Ollama to start..."
    sleep 5
    
    echo "   Pulling llama3.2 model (this may take a few minutes)..."
    sudo docker exec ollama ollama pull llama3.2
else
    echo "   ✅ Ollama is already running"
fi

# 2. Ollama mit Netzwerk verbinden
echo ""
echo "🌐 Connecting Ollama to pdf_ocr_network..."
sudo docker network connect pdf_ocr_network ollama 2>/dev/null || echo "   Already connected"

# 3. Projekt aktualisieren
echo ""
echo "📥 Updating project from GitHub..."
cd /volume1/docker/pdf-ocr
sudo wget https://github.com/Admiral9633/Mark-API/archive/refs/heads/main.zip -O main.zip
sudo unzip -o main.zip
sudo cp -r Mark-API-main/* .
sudo rm -rf Mark-API-main main.zip

# 4. .env prüfen
echo ""
echo "🔐 Checking environment variables..."
if ! grep -q "OLLAMA_API_URL" .env; then
    echo "   Adding Ollama configuration to .env..."
    echo "" >> .env
    echo "# Ollama AI" >> .env
    echo "OLLAMA_API_URL=http://ollama:11434" >> .env
    echo "OLLAMA_MODEL=llama3.2" >> .env
fi

if ! grep -q "LEXOFFICE_API_KEY" .env; then
    echo "   ⚠️  WARNING: LEXOFFICE_API_KEY not found in .env!"
    echo "   Please add manually: sudo nano .env"
else
    echo "   ✅ Lexoffice API Key configured"
fi

# 5. Container neu starten
echo ""
echo "🔄 Restarting containers..."
sudo docker-compose down
sudo docker-compose up -d

# 6. Migrations ausführen
echo ""
echo "📊 Running database migrations..."
sleep 5  # Wait for DB to be ready
sudo docker-compose exec -T backend python manage.py migrate

# 7. Health Checks
echo ""
echo "🏥 Running health checks..."
echo ""

echo -n "   PostgreSQL: "
if sudo docker-compose exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅"
else
    echo "❌"
fi

echo -n "   Backend: "
if curl -sf http://localhost:8000/api/documents/ > /dev/null; then
    echo "✅"
else
    echo "❌"
fi

echo -n "   Frontend: "
if curl -sf http://localhost:3000 > /dev/null; then
    echo "✅"
else
    echo "❌"
fi

echo -n "   Marker-API: "
if curl -sf http://localhost:8001/health > /dev/null; then
    echo "✅"
else
    echo "❌"
fi

echo -n "   Ollama: "
if curl -sf http://localhost:11434/api/tags > /dev/null; then
    echo "✅"
else
    echo "❌"
fi

echo ""
echo "=================================================="
echo "✅ Deployment complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Check logs: sudo docker-compose logs -f backend"
echo "   2. Test upload: http://192.168.178.84:3000"
echo "   3. Monitor: sudo docker-compose logs -f | grep -E '\\[AI\\]|\\[LEXOFFICE\\]'"
echo ""
echo "🔧 Troubleshooting:"
echo "   - View all logs: sudo docker-compose logs"
echo "   - Restart: sudo docker-compose restart backend"
echo "   - Reset: sudo docker-compose down && sudo docker-compose up -d"

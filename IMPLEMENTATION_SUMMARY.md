# ✅ Implementation Complete: Ollama AI + Lexoffice Integration

## Was wurde implementiert?

### 🤖 AI Classification (Ollama)
- **Datei**: `backend/api/ollama_classifier.py`
- **Funktion**: Klassifiziert OCR-Texte automatisch
- **Erkennung**: 
  - Ist es eine Rechnung? (is_invoice)
  - Typ: Eingangsrechnung vs. Ausgangsrechnung
  - Confidence Score (0-1)
  - Reasoning (KI-Begründung)

### 📤 Lexoffice API Client
- **Datei**: `backend/api/lexoffice_client.py`
- **Funktion**: Upload von PDF-Belegen zu Lexoffice
- **Features**:
  - Bearer Token Authentication
  - Multipart/Form-Data Upload
  - Health Check & Profile Abruf
  - Error Handling & Retry Logic

### 🗄️ Datenbank-Erweiterungen
- **Datei**: `backend/api/models.py`
- **Neue Felder**:
  - `ai_classification` (JSON) - Komplette AI Response
  - `is_invoice` (Boolean) - Rechnung erkannt?
  - `invoice_type` (String) - 'incoming' / 'outgoing'
  - `lexoffice_sent` (Boolean) - Upload Status
  - `lexoffice_file_id` (String) - Lexoffice File ID
  - `lexoffice_voucher_id` (String) - Lexoffice Voucher ID
  - `lexoffice_error` (Text) - Fehlermeldung

### 🔄 Workflow Integration
- **Datei**: `backend/api/views.py`
- **Ablauf**:
  1. PDF Upload → Marker OCR
  2. OCR Text → Ollama AI Klassifizierung
  3. Wenn Rechnung → Lexoffice Upload
  4. Speichern aller Results in DB

### ⚙️ Konfiguration
- **Dateien**: `.env`, `docker-compose.yml`
- **Environment Variables**:
  - `OLLAMA_API_URL=http://host.docker.internal:11434`
  - `OLLAMA_MODEL=llama3.2`
  - `LEXOFFICE_API_KEY=your-key-here`
  - `LEXOFFICE_API_URL=https://api.lexware.io`

### 📚 Dokumentation
- **OLLAMA_LEXOFFICE_SETUP.md** - Vollständiges Setup-Handbuch
- **test-integrations.py** - Test-Script für beide APIs
- Migration: `0002_ai_lexoffice_fields.py`

## 🚀 Nächste Schritte

### 1. Ollama installieren
```bash
# Windows: Download von https://ollama.ai
ollama run llama3.2

# Oder Docker:
docker run -d -p 11434:11434 ollama/ollama
docker exec -it ollama ollama pull llama3.2
```

### 2. .env aktualisieren
```bash
# API Key eintragen
nano .env
# LEXOFFICE_API_KEY=whz6Oofxi0Hud2Y8947oU2-GNe3KlFJiTJ_BI_CzaSnW.oc.
```

### 3. Docker Container neu starten
```bash
docker-compose down
docker-compose up -d backend
```

### 4. Migrations ausführen
```bash
docker-compose exec backend python manage.py makemigrations
docker-compose exec backend python manage.py migrate
```

### 5. Testen
```bash
# Connectivity Test
python test-integrations.py

# PDF hochladen und Logs ansehen
docker-compose logs -f backend
# Suche nach: [AI] und [LEXOFFICE]
```

## ⚠️ Wichtige Hinweise

### Ollama → Docker Kommunikation
- **Windows/Mac**: `host.docker.internal:11434` ✅
- **Linux**: `--add-host=host.docker.internal:host-gateway` erforderlich

### Lexoffice API Limits
- **2 Requests/Sekunde** (Token Bucket)
- Bei 429 Error: Automatisches Retry implementieren

### Sicherheit
- ⚠️ **API Key NIEMALS committen!**
- `.env` ist in `.gitignore`
- Auf NAS: `chmod 600 .env`

## 📊 Deployment auf NAS

```bash
# 1. Code hochladen
git add .
git commit -m "Add: Ollama AI + Lexoffice integration"
git push

# 2. Auf NAS
cd /volume1/docker/pdf-ocr
sudo wget https://github.com/Admiral9633/Mark-API/archive/refs/heads/main.zip
sudo unzip -o main.zip
sudo cp -r Mark-API-main/* .

# 3. .env anpassen
sudo nano .env
# OLLAMA_API_URL und LEXOFFICE_API_KEY eintragen

# 4. Container neu starten
sudo docker-compose down
sudo docker-compose up -d

# 5. Migrations
sudo docker-compose exec backend python manage.py migrate

# 6. Logs checken
sudo docker-compose logs -f backend
```

## 🎯 Testing Checklist

- [ ] Ollama läuft und ist erreichbar
- [ ] Lexoffice API Key konfiguriert
- [ ] `test-integrations.py` läuft durch
- [ ] PDF Upload → OCR funktioniert
- [ ] AI Klassifizierung wird ausgeführt
- [ ] Rechnung wird in DB als `is_invoice=True` gespeichert
- [ ] Lexoffice Upload erfolgreich
- [ ] Beleg erscheint in Lexoffice "Zu prüfen"

## 📝 Bekannte Limitierungen

1. **Nur PDF-Upload**: Keine direkten Bild-Uploads (muss erst zu PDF konvertiert werden)
2. **OCR Quality**: Marker-API braucht 8-9 Min für komplexe PDFs
3. **AI Model**: llama3.2 ist schnell aber nicht perfekt - bei Bedarf auf mistral upgraden
4. **Lexoffice Rate Limits**: 2 req/sec - keine Bulk-Uploads möglich

## 🔧 Troubleshooting

### "Ollama API connection error"
→ Prüfe: `curl http://localhost:11434/api/tags`

### "Lexoffice API key not configured"
→ Prüfe: `echo $LEXOFFICE_API_KEY` in `.env`

### "Upload failed with status 401"
→ API Key abgelaufen? Neu generieren in Lexoffice

### AI erkennt Rechnung nicht
→ Prompt in `ollama_classifier.py` anpassen
→ Größeres Model probieren (`mistral` statt `llama3.2`)

## ✅ Was fehlt noch?

Frontend Integration:
- [ ] Lexoffice Status Badge in Document List
- [ ] Manual Retry Button für fehlgeschlagene Uploads
- [ ] Invoice Type Badge (Eingang/Ausgang)
- [ ] AI Confidence Score anzeigen

Geplant für nächsten Sprint!

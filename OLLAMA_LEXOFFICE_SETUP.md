# Ollama AI + Lexoffice Integration

Dieses Projekt wurde erweitert mit **automatischer Rechnungserkennung** mittels Ollama AI und **automatischem Upload zu Lexoffice**.

## 🎯 Features

- **AI-Klassifizierung**: Ollama LLM analysiert OCR-Texte und erkennt automatisch:
  - Ist es eine Rechnung? ✅
  - Eingangsrechnung (von Lieferanten) oder Ausgangsrechnung (eigene)?
  - Konfidenz-Score der Erkennung

- **Lexoffice Integration**: Automatischer Upload erkannter Rechnungen:
  - Wird als Beleg (Voucher) in Lexoffice hochgeladen
  - Erscheint im "Zu prüfen" Ordner in Lexoffice
  - Tracking von Upload-Status und Fehlern

## 🚀 Setup

### 1. Ollama Installation

#### Option A: Lokale Installation (Windows PC)
```powershell
# Download von https://ollama.ai
# Installieren und starten
ollama run llama3.2
```

#### Option B: Docker Installation
```bash
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
docker exec -it ollama ollama pull llama3.2
```

### 2. Lexoffice API Key

1. Gehe zu [https://app.lexware.de/addons/public-api](https://app.lexware.de/addons/public-api)
2. Generiere einen neuen API Key
3. Kopiere den Key (beginnt mit "whz6...")

### 3. Umgebungsvariablen

Füge in `.env` hinzu:

```env
# Ollama AI
OLLAMA_API_URL=http://host.docker.internal:11434
OLLAMA_MODEL=llama3.2

# Lexoffice API
LEXOFFICE_API_KEY=dein-api-key-hier
LEXOFFICE_API_URL=https://api.lexware.io
```

⚠️ **Wichtig**: `host.docker.internal` für Docker → Host-PC Kommunikation verwenden!

### 4. Docker Container neu starten

```bash
docker-compose down
docker-compose up -d
```

## 📊 Workflow

1. **PDF Upload** → OCR mit Marker-API
2. **AI Analyse** → Ollama klassifiziert das Dokument
3. **Automatischer Upload** → Bei erkannter Rechnung: Upload zu Lexoffice
4. **Tracking** → Status wird in Datenbank gespeichert

## 🗄️ Neue Datenbankfelder

Das `Document` Model wurde erweitert:

```python
# AI Classification
ai_classification = JSONField()  # Komplette AI Response
is_invoice = BooleanField()      # True wenn Rechnung erkannt
invoice_type = CharField()       # 'incoming' oder 'outgoing'

# Lexoffice Integration
lexoffice_sent = BooleanField()        # Upload erfolgt?
lexoffice_file_id = CharField()        # Lexoffice File ID
lexoffice_voucher_id = CharField()     # Lexoffice Voucher ID
lexoffice_error = TextField()          # Fehlermeldung bei Upload
```

## 🧪 Testen

### Ollama Health Check
```bash
curl http://localhost:11434/api/tags
```

### Lexoffice API Test
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.lexware.io/v1/profile
```

### Backend Logs ansehen
```bash
docker-compose logs -f backend
```

Suche nach:
- `[AI]` - AI Klassifizierung
- `[LEXOFFICE]` - Lexoffice Upload

## 📝 API Response Beispiel

```json
{
  "id": 1,
  "original_filename": "rechnung-hornbach.pdf",
  "status": "completed",
  "marker_markdown": "# Rechnung\n...",
  "ai_classification": {
    "is_invoice": true,
    "invoice_type": "incoming",
    "confidence": 0.95,
    "reasoning": "Dokument enthält Rechnungsnummer, Lieferantendaten..."
  },
  "is_invoice": true,
  "invoice_type": "incoming",
  "lexoffice_sent": true,
  "lexoffice_file_id": "abc-123-def",
  "lexoffice_voucher_id": "xyz-456-uvw",
  "lexoffice_error": null
}
```

## 🔧 Konfiguration

### Ollama Model wechseln

In `.env`:
```env
OLLAMA_MODEL=mistral  # oder llama2, codellama, etc.
```

Verfügbare Modelle: https://ollama.ai/library

### Lexoffice API Rate Limits

- **2 Requests/Sekunde** (Token Bucket Algorithm)
- Automatisches Retry bei 429 (Too Many Requests)

## 🐛 Troubleshooting

### Ollama nicht erreichbar

**Problem**: `Ollama API connection error`

**Lösung**:
```bash
# Test ob Ollama läuft
curl http://localhost:11434/api/tags

# Docker: Stelle sicher host.docker.internal funktioniert
# Windows: Sollte funktionieren
# Linux: docker run --add-host=host.docker.internal:host-gateway
```

### Lexoffice Upload fehlgeschlagen

**Problem**: `Upload failed with status 401`

**Lösung**:
- API Key korrekt in `.env`?
- API Key in Lexoffice nicht abgelaufen?
- Teste mit: `curl -H "Authorization: Bearer KEY" https://api.lexware.io/v1/profile`

### AI Klassifizierung falsch

**Lösung**:
- Prompt in `ollama_classifier.py` anpassen
- Größeres Modell verwenden (z.B. `llama3.2` → `mistral`)
- Mehr Kontext mitgeben (aktuell 2000 Zeichen)

## 📚 Weiterführende Links

- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Lexoffice API Docs](https://developers.lexware.io/docs/)
- [Lexoffice Files Endpoint](https://developers.lexware.io/docs/#files-endpoint)

## 🔐 Sicherheit

⚠️ **API Keys niemals in Git committen!**

- `.env` ist in `.gitignore`
- Lexoffice API Key rotieren bei Verdacht auf Kompromittierung
- Auf NAS: `.env` Datei mit chmod 600 schützen

## 📈 Nächste Schritte

- [ ] Frontend: Lexoffice Status Badges anzeigen
- [ ] Manueller Retry-Button für fehlgeschlagene Uploads
- [ ] Filtering: Nur Eingangsrechnungen hochladen
- [ ] Kontakt-Matching: Lieferant automatisch zuordnen
- [ ] E-Mail Benachrichtigung bei neuen Rechnungen

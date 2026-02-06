from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import tempfile
import os
from pathlib import Path

app = FastAPI(title="Marker OCR API")

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/convert")
async def convert_pdf(pdf: UploadFile = File(...)):
    try:
        # Import hier um Modelle lazy zu laden
        from marker.converters.pdf import PdfConverter
        from marker.models import create_model_dict
        
        # Temporäre Datei
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            content = await pdf.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Modelle laden
        model_dict = create_model_dict()
        
        # Converter initialisieren
        converter = PdfConverter(artifact_dict=model_dict)
        
        # PDF konvertieren
        rendered = converter(tmp_path)
        
        # Cleanup
        os.unlink(tmp_path)
        
        # Metadata extrahieren
        metadata = {}
        if hasattr(rendered, 'metadata'):
            metadata = rendered.metadata
        elif hasattr(rendered, '__dict__'):
            metadata = {k: v for k, v in rendered.__dict__.items() 
                       if k != 'markdown' and not k.startswith('_')}
        
        return JSONResponse({
            "markdown": rendered.markdown,
            "metadata": metadata
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

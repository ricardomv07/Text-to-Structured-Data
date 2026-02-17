from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from .extractors import extract_text
from .validators import validate_json_response
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@app.post("/api/process")
async def process_file(file: UploadFile = File(...)):
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate file is not empty
        if not file_content:
            return {"error": "El archivo está vacío"}, 400
        
        # Extract text from file
        raw_text = extract_text(file.filename, file_content)
        
        # Validate extracted text
        if not raw_text.strip():
            return {"error": "No se pudo extraer texto del archivo"}, 400
        
        # Process with Gemini
        prompt = f"""
        Extrae la siguiente información del texto y devuelve SOLO un JSON válido con estos campos:
        - cliente: nombre del cliente
        - monto: cantidad en números
        - fecha: fecha del documento
        - tipo_solicitud: tipo de solicitud (Venta, Queja, Factura, etc.)
        
        Texto:
        {raw_text}
        
        Responde SOLO con JSON válido, sin explicaciones adicionales.
        """
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        # Parse and validate JSON
        try:
            json_response = json.loads(response.text)
            validate_json_response(json_response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            json_str = response.text.strip()
            if json_str.startswith('```'):
                json_str = json_str.split('```')[1].replace('json', '').strip()
            json_response = json.loads(json_str)
            validate_json_response(json_response)
        
        return {
            "raw_text": raw_text,
            "structured_data": json_response
        }
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

@app.get("/")
async def root():
    return {"message": "API Text-to-Structured-Data running"}
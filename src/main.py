from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .extractors import extract_text
from .validators import validate_json_response
import google.generativeai as genai
import json
import os
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Validate API key exists
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables!")
    raise ValueError("GEMINI_API_KEY is required but not configured")

genai.configure(api_key=GEMINI_API_KEY)
logger.info("Gemini API configured successfully")

@app.post("/api/process")
async def process_file(file: UploadFile = File(...)):
    try:
        logger.info(f"Processing file: {file.filename}")
        
        # Read file content
        file_content = await file.read()
        
        # Validate file is not empty
        if not file_content:
            logger.warning("Empty file received")
            raise HTTPException(status_code=400, detail="El archivo está vacío")
        
        # Extract text from file
        logger.info(f"Extracting text from {file.filename}")
        raw_text = extract_text(file.filename, file_content)
        
        # Validate extracted text
        if not raw_text.strip():
            logger.warning("No text could be extracted from file")
            raise HTTPException(status_code=400, detail="No se pudo extraer texto del archivo")
        
        logger.info(f"Extracted {len(raw_text)} characters of text")
        
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
        
        logger.info("Calling Gemini API...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        logger.info("Gemini API response received")
        
        # Parse and validate JSON
        try:
            json_response = json.loads(response.text)
            validate_json_response(json_response)
        except json.JSONDecodeError:
            logger.info("Attempting to extract JSON from formatted response")
            # Try to extract JSON from response
            json_str = response.text.strip()
            if json_str.startswith('```'):
                json_str = json_str.split('```')[1].replace('json', '').strip()
            json_response = json.loads(json_str)
            validate_json_response(json_response)
        
        logger.info("File processed successfully")
        return {
            "raw_text": raw_text,
            "structured_data": json_response
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/")
async def root():
    return {"message": "API Text-to-Structured-Data running"}
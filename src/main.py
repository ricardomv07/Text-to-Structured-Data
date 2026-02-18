from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from .extractors import extract_text
from .validators import validate_json_response
from . import database
import google.generativeai as genai
import json
import os
import logging
import re
from dotenv import load_dotenv
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(
    title="Text-to-Structured-Data API",
    description="API para extraer datos estructurados de documentos usando IA",
    version="2.0"
)

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

# Initialize database
database.init_database()

def format_date(date_str: str) -> str:
    """Convert date from text to DD/MM/YYYY format"""
    months_es = {
        'enero': '01', 'febrero': '02', 'marzo': '03', 'abril': '04',
        'mayo': '05', 'junio': '06', 'julio': '07', 'agosto': '08',
        'septiembre': '09', 'octubre': '10', 'noviembre': '11', 'diciembre': '12'
    }
    
    # Try to match "16 de febrero de 2026" format
    pattern = r'(\d+)\s+de\s+(\w+)\s+de\s+(\d{4})'
    match = re.search(pattern, date_str.lower())
    if match:
        day = match.group(1).zfill(2)
        month = months_es.get(match.group(2), '01')
        year = match.group(3)
        return f"{day}/{month}/{year}"
    
    return date_str

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
        
        # Basic validation: Only reject if document is empty or too short
        if len(raw_text.strip()) < 20:
            logger.warning(f"Document too short ({len(raw_text)} characters)")
            raise HTTPException(
                status_code=400,
                detail="El documento está vacío o es demasiado corto. Por favor, sube un documento con contenido."
            )
        
        logger.info("Document validation passed - proceeding to extraction")
        
        # Extract structured data with retry mechanism
        logger.info("Extracting structured data...")
        model = genai.GenerativeModel('gemini-2.5-flash')
        max_retries = 3
        json_response = None
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Attempt {attempt}/{max_retries} to extract JSON data")
                
                if attempt == 1:
                    prompt = f"""
                    Extrae la siguiente información del texto y devuelve SOLO un JSON válido con estos campos:
                    - cliente: nombre del cliente
                    - monto: cantidad en números
                    - fecha: fecha del documento en formato DD/MM/YYYY
                    - tipo_solicitud: tipo de solicitud (Venta, Queja, Factura, etc.)
                    
                    Texto:
                    {raw_text}
                    
                    Responde SOLO con JSON válido, sin explicaciones adicionales.
                    """
                else:
                    # Retry with more explicit instructions
                    prompt = f"""
                    IMPORTANTE: Debes responder ÚNICAMENTE con un objeto JSON válido. No incluyas texto adicional, explicaciones ni formato markdown.
                    
                    Extrae del siguiente texto estos campos exactos:
                    {{
                        "cliente": "nombre del cliente",
                        "monto": número_sin_símbolos,
                        "fecha": "DD/MM/YYYY",
                        "tipo_solicitud": "Venta|Queja|Factura|Cotización|Servicio"
                    }}
                    
                    Texto:
                    {raw_text}
                    
                    Responde SOLO el JSON, nada más.
                    """
                
                response = model.generate_content(prompt)
                response_text = response.text.strip()
                logger.info(f"Received response (length: {len(response_text)} chars)")
                
                # Try to parse JSON directly
                try:
                    json_response = json.loads(response_text)
                    logger.info("Successfully parsed JSON directly")
                except json.JSONDecodeError:
                    logger.info("Direct JSON parse failed, attempting to extract from markdown")
                    # Try to extract JSON from markdown code blocks
                    if '```' in response_text:
                        # Extract content between ``` markers
                        parts = response_text.split('```')
                        for part in parts:
                            part = part.strip()
                            if part.startswith('json'):
                                part = part[4:].strip()
                            if part.startswith('{'):
                                try:
                                    json_response = json.loads(part)
                                    logger.info("Successfully extracted JSON from markdown")
                                    break
                                except:
                                    continue
                    
                    # If still no JSON, try to find JSON object in text
                    if not json_response:
                        import re
                        json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response_text)
                        if json_match:
                            try:
                                json_response = json.loads(json_match.group())
                                logger.info("Successfully extracted JSON using regex")
                            except:
                                pass
                
                # Validate the JSON response structure only
                if json_response:
                    validate_json_response(json_response)
                    logger.info(f"JSON validation successful on attempt {attempt}")
                    logger.info(f"Extracted - Cliente: {json_response.get('cliente', 'N/A')}, Monto: {json_response.get('monto', 'N/A')}")
                    break
                else:
                    raise ValueError("No valid JSON found in response")
                    
            except Exception as e:
                logger.warning(f"Attempt {attempt} failed: {str(e)}")
                if attempt == max_retries:
                    logger.error("All retry attempts exhausted")
                    raise HTTPException(
                        status_code=500,
                        detail=f"La IA no pudo generar una respuesta en formato JSON válido después de {max_retries} intentos. Por favor, intenta con otro documento o contacta a soporte."
                    )
                # Wait a bit before retrying
                import time
                time.sleep(0.5)
        
        if not json_response:
            raise HTTPException(
                status_code=500,
                detail="No se pudo extraer datos estructurados del documento."
            )
        
        # Format date if present
        if 'fecha' in json_response and json_response['fecha']:
            json_response['fecha'] = format_date(json_response['fecha'])
        
        # Save to database automatically (if configured)
        # Note: db_id is not exposed in the response, only logged
        try:
            db_record = database.save_extracted_data(
                cliente=json_response.get('cliente', 'Unknown'),
                monto=float(json_response.get('monto', 0)) if json_response.get('monto') else 0,
                fecha=json_response.get('fecha'),
                tipo_solicitud=json_response.get('tipo_solicitud', 'Unknown'),
                raw_text=raw_text,
                filename=file.filename
            )
            if db_record:
                logger.info(f"Data saved to database with ID: {db_record['id']}")
        except Exception as e:
            logger.warning(f"Could not save to database: {str(e)}")
            # Don't fail the request if database save fails
        
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
    """Root endpoint with API information"""
    return {
        "message": "API Text-to-Structured-Data running",
        "version": "2.0",
        "endpoints": {
            "process": "/api/process [POST] - Process document and extract data",
            "save": "/api/save [POST] - Save edited JSON to database",
            "history": "/api/history [GET] - Get all saved records",
            "records": "/api/records [GET] - Get all saved records (with pagination)",
            "search_client": "/api/records/search?cliente=name [GET] - Search by client",
            "search_type": "/api/records/search?tipo=type [GET] - Search by type",
            "stats": "/api/stats [GET] - Get database statistics"
        },
        "database_status": "configured" if database.SessionLocal else "not_configured"
    }

@app.get("/api/records")
async def get_records(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """
    Get all saved records from database
    
    Args:
        limit: Maximum number of records to return (1-1000)
        offset: Number of records to skip
    
    Returns:
        List of saved records
    """
    if database.SessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no configurada. Configura DATABASE_URL en las variables de entorno."
        )
    
    records = database.get_all_records(limit=limit, offset=offset)
    return {
        "total": len(records),
        "limit": limit,
        "offset": offset,
        "records": records
    }

@app.get("/api/records/search")
async def search_records(
    cliente: Optional[str] = Query(default=None),
    tipo: Optional[str] = Query(default=None)
):
    """
    Search records by client name or request type
    
    Args:
        cliente: Client name to search for (partial match)
        tipo: Request type to filter by (partial match)
    
    Returns:
        List of matching records
    """
    if database.SessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no configurada. Configura DATABASE_URL en las variables de entorno."
        )
    
    if not cliente and not tipo:
        raise HTTPException(
            status_code=400,
            detail="Debes proporcionar al menos un parámetro de búsqueda: 'cliente' o 'tipo'"
        )
    
    if cliente:
        records = database.get_records_by_client(cliente)
    else:
        records = database.get_records_by_type(tipo)
    
    return {
        "total": len(records),
        "search_criteria": {
            "cliente": cliente,
            "tipo": tipo
        },
        "records": records
    }

@app.get("/api/stats")
async def get_stats():
    """
    Get database statistics
    
    Returns:
        Statistics about stored data
    """
    if database.SessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no configurada. Configura DATABASE_URL en las variables de entorno."
        )
    
    stats = database.get_database_stats()
    return stats

@app.post("/api/save")
async def save_to_database(request_data: dict):
    """
    Save manually edited JSON data to database
    
    Request body:
    {
        "data": {
            "cliente": "Juan Pérez",
            "monto": 15000,
            "fecha": "15/02/2026",
            "tipo_solicitud": "Factura"
        }
    }
    
    Returns:
        Success message with record ID
    """
    if database.SessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no configurada. Configura DATABASE_URL en las variables de entorno."
        )
    
    try:
        data = request_data.get('data', {})
        
        # Validate required fields
        if not data.get('cliente'):
            raise HTTPException(
                status_code=400,
                detail="El campo 'cliente' es requerido"
            )
        
        if not data.get('tipo_solicitud'):
            raise HTTPException(
                status_code=400,
                detail="El campo 'tipo_solicitud' es requerido"
            )
        
        # Save to database
        db_record = database.save_extracted_data(
            cliente=data.get('cliente', 'Unknown'),
            monto=float(data.get('monto', 0)) if data.get('monto') else 0,
            fecha=data.get('fecha'),
            tipo_solicitud=data.get('tipo_solicitud', 'Unknown'),
            raw_text=None,
            filename=None
        )
        
        if db_record:
            logger.info(f"Manually edited data saved to database with ID: {db_record['id']}")
            return {
                "success": True,
                "message": "Registro guardado exitosamente",
                "id": db_record['id']
            }
        else:
            return {
                "success": False,
                "error": "Error al guardar en la base de datos"
            }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving data: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": f"Error al guardar: {str(e)}"
        }

@app.get("/api/history")
async def get_history(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0)
):
    """
    Get all saved records from database (alias for /api/records)
    Compatible with frontend expectations
    
    Args:
        limit: Maximum number of records to return (1-1000)
        offset: Number of records to skip
    
    Returns:
        List of saved records in format expected by frontend
    """
    if database.SessionLocal is None:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no configurada. Configura DATABASE_URL en las variables de entorno."
        )
    
    records = database.get_all_records(limit=limit, offset=offset)
    return {
        "records": records
    }
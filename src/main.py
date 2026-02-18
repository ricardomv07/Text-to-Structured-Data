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
import time
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
    """Process uploaded file and extract structured data"""
    try:
        logger.info(f"=== NEW REQUEST: Processing file: {file.filename} ===")
        
        # Read file content
        try:
            file_content = await file.read()
            logger.info(f"File read successfully ({len(file_content)} bytes)")
        except Exception as read_error:
            logger.error(f"Error reading file: {read_error}")
            raise HTTPException(status_code=400, detail=f"Error al leer el archivo: {str(read_error)}")
        
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
        
        # Basic validation: Check if document is empty
        if len(raw_text.strip()) < 20:
            logger.warning(f"Document too short ({len(raw_text)} characters)")
            raise HTTPException(
                status_code=400,
                detail="El documento está vacío o es demasiado corto. Por favor, sube un documento con contenido."
            )
        
        # Light keyword validation (fast, minimal false positives)
        logger.info("Validating document content...")
        text_lower = raw_text.lower()
        
        # Check for business-related keywords
        commercial_keywords = [
            'factura', 'cotización', 'cotizacion', 'presupuesto', 'pedido',
            'venta', 'compra', 'solicitud', 'orden', 'contrato', 'servicio',
            'monto', 'precio', 'total', 'subtotal', 'iva', '$', 'pesos', 'usd', 'cantidad'
        ]
        
        # Check for obvious non-commercial document types
        non_commercial_keywords = [
            'política', 'politica', 'procedimiento', 'lineamiento', 'manual técnico', 'reglamento',
            'investigación', 'investigacion', 'tesis', 'tesina', 'proyecto de grado',
            'universidad', 'instituto', 'facultad', 'carrera', 'materia',
            'abstract', 'resumen', 'introducción teórica', 'marco teórico',
            'bibliografía', 'referencias', 'anexos', 'objetivos generales',
            'arquitectura de software', 'patrones de diseño', 'metodología de investigación'
        ]
        
        # Strong commercial indicators (almost always mean it's a real commercial doc)
        strong_commercial = ['rfc:', 'número de factura:', 'folio:', 'cuenta bancaria:', 'razón social:']
        
        has_commercial = any(keyword in text_lower for keyword in commercial_keywords)
        has_non_commercial = any(keyword in text_lower for keyword in non_commercial_keywords)
        has_strong_commercial = any(indicator in text_lower for indicator in strong_commercial)
        
        # Reject if clearly academic/policy AND no strong commercial indicators
        if has_non_commercial and not has_strong_commercial:
            logger.warning("Document appears to be academic/policy/manual without strong commercial indicators")
            raise HTTPException(
                status_code=400,
                detail="Este documento parece ser académico, manual o política interna. Por favor, sube una factura, cotización o solicitud de compra."
            )
        
        logger.info(f"Document validation passed (has_commercial: {has_commercial}, has_non_commercial: {has_non_commercial}, has_strong: {has_strong_commercial})")
        
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
                    Extrae esta información del texto y responde SOLO con JSON:
                    
                    {{"cliente": "nombre del cliente o empresa", "monto": 1234, "fecha": "DD/MM/YYYY", "tipo_solicitud": "Factura"}}
                    
                    Texto:
                    {raw_text[:2000]}
                    
                    Responde SOLO el JSON, sin explicaciones.
                    """
                else:
                    # Retry with even simpler prompt
                    prompt = f"""
                    Del siguiente texto extrae cliente, monto, fecha y tipo.
                    Responde en formato JSON sin texto adicional.
                    
                    Texto: {raw_text[:1000]}
                    
                    JSON:
                    """
                
                # Call Gemini API with error handling
                try:
                    response = model.generate_content(prompt)
                    response_text = response.text.strip()
                    logger.info(f"Received response (length: {len(response_text)} chars)")
                    # Log preview of response for debugging
                    logger.info(f"Response preview: {response_text[:300]}")
                except Exception as gemini_error:
                    logger.error(f"Gemini API error on attempt {attempt}: {str(gemini_error)}")
                    # Check if it's a rate limit or quota error
                    error_msg = str(gemini_error).lower()
                    if 'quota' in error_msg or 'rate' in error_msg or 'limit' in error_msg:
                        logger.warning("Rate limit or quota exceeded, waiting longer before retry...")
                        time.sleep(2 * attempt)  # Exponential backoff
                        raise ValueError(f"Gemini API rate limit (attempt {attempt})")
                    else:
                        raise  # Re-raise if it's not a rate limit issue
                
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
                
                # Validate the JSON response structure
                if json_response:
                    # Validate and normalize (converts null to defaults, maps 'tipo' to 'tipo_solicitud')
                    validate_json_response(json_response)
                    
                    # Additional validation: ensure cliente is not empty
                    cliente = json_response.get('cliente', '')
                    if isinstance(cliente, str):
                        cliente = cliente.strip()
                    else:
                        cliente = str(cliente) if cliente else ''
                    
                    # If cliente is empty or generic, retry (except on last attempt)
                    if not cliente or cliente.lower() in ['no especificado', 'n/a', 'na', 'unknown']:
                        if attempt < max_retries:
                            logger.warning(f"Cliente empty or generic on attempt {attempt}: '{cliente}' - retrying...")
                            raise ValueError(f"Cliente field is empty, retrying (attempt {attempt})")
                        else:
                            # Last attempt - set default value instead of failing
                            logger.warning(f"Cliente still empty on final attempt, using default")
                            json_response['cliente'] = "Sin nombre especificado"
                            json_response['cliente'] = "Sin nombre especificado"
                    
                    logger.info(f"JSON validation successful on attempt {attempt}")
                    logger.info(f"Extracted - Cliente: {json_response.get('cliente', 'N/A')}, Monto: {json_response.get('monto', 'N/A')}")
                    break
                else:
                    # Last resort: if still no JSON and it's the final attempt, log the full response
                    if attempt == max_retries:
                        logger.error("All parsing methods failed. Full response:")
                        logger.error(response_text)
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
                time.sleep(0.5)
        
        if not json_response:
            raise HTTPException(
                status_code=500,
                detail="No se pudo extraer datos estructurados del documento."
            )
        
        # Format date if present
        if 'fecha' in json_response and json_response['fecha']:
            json_response['fecha'] = format_date(json_response['fecha'])
        
        # NOTE: Data is NOT saved automatically - user must click "Guardar" to save
        logger.info("File processed successfully (not saved to database yet)")
        return {
            "raw_text": raw_text,
            "structured_data": json_response,
            "message": "Datos extraídos correctamente. Revisa y presiona 'Guardar' para almacenar en la base de datos."
        }
    
    except HTTPException as http_ex:
        logger.error(f"HTTP Exception: {http_ex.detail}")
        raise
    except Exception as e:
        logger.error(f"CRITICAL ERROR processing file: {str(e)}", exc_info=True)
        # Return more detailed error for debugging
        error_type = type(e).__name__
        error_detail = f"Error tipo {error_type}: {str(e)}"
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "API Text-to-Structured-Data running",
        "version": "2.0",
        "endpoints": {
            "health": "/api/health [GET] - Check API health and dependencies",
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

@app.get("/api/health")
async def health_check():
    """Health check endpoint to verify all dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "checks": {}
    }
    
    # Check Gemini API
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            test_model = genai.GenerativeModel('gemini-2.5-flash')
            # Quick test
            test_response = test_model.generate_content("Respond with: OK")
            health_status["checks"]["gemini_api"] = "operational"
        else:
            health_status["checks"]["gemini_api"] = "missing_api_key"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["gemini_api"] = f"error: {str(e)[:100]}"
        health_status["status"] = "degraded"
    
    # Check Database
    try:
        if database.SessionLocal:
            # Try to get count of records
            stats = database.get_database_stats()
            health_status["checks"]["database"] = f"operational ({stats.get('total_records', 0)} records)"
        else:
            health_status["checks"]["database"] = "not_configured"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)[:100]}"
        health_status["status"] = "degraded"
    
    return health_status

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
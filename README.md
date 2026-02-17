# Text-to-Structured-Data

## Overview
Text-to-Structured-Data is a Python project designed to extract key information from various text file formats, including TXT, DOCX, and XLSX. The project utilizes the Google Gemini API to convert unstructured text data into a structured JSON format.

## Project Structure
```
Text-to-Structured-Data
├── src
│   ├── main.py            # Orchestrator for the application
│   ├── extractors.py      # Logic for reading different file formats
│   ├── validators.py      # Validation logic for JSON responses
│   └── __init__.py        # Marks the directory as a Python package
├── tests
│   ├── test_extractors.py  # Unit tests for extractors
│   └── __init__.py        # Marks the tests directory as a Python package
├── .env                   # Configuration for environment variables
├── .gitignore             # Files and directories to ignore by Git
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Installation
To set up the project, follow these steps:

1. Clone the repository:
   ```
   git clone <repository-url>
   cd Text-to-Structured-Data
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory and add your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Usage
To run the application, execute the following command:
```bash
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST /api/process
Procesa un archivo cargado y extrae información estructurada.

**Headers:**
```
Content-Type: multipart/form-data
```

**Parameters:**
- `file`: Archivo a procesar (TXT, DOCX o XLSX)

**Success Response (200):**
```json
{
  "raw_text": "Texto completo extraído del archivo",
  "structured_data": {
    "cliente": "Nombre del cliente",
    "monto": "1000",
    "fecha": "2025-02-16",
    "tipo_solicitud": "Venta"
  }
}
```

**Error Response (400/500):**
```json
{
  "error": "Descripción del error"
}
```

### GET /
Verifica que el servidor está ejecutándose.

**Response:**
```json
{
  "message": "API Text-to-Structured-Data running"
}
```

## 🔧 Componentes Principales

### src/main.py
- Configura el servidor FastAPI
- Define los endpoints de la API
- Integra Google Gemini para procesamiento
- Maneja CORS para solicitudes del frontend

### src/extractors.py
Extrae texto de diferentes formatos de archivo:

```python
def extract_text(filename: str, file_content: bytes) -> str:
    # .txt: Decodificación UTF-8/Latin-1
    # .docx: Extrae párrafos del documento
    # .xlsx: Convierte a string usando pandas
```

**Características:**
- Manejo de múltiples codificaciones
- Soporte para UTF-8, Latin-1 con fallback
- Extracción limpia de contenido

### src/validators.py
Valida que la respuesta JSON de Gemini tenga los campos requeridos:
- `cliente`
- `monto`
- `fecha`
- `tipo_solicitud`

## 🤖 Integración con Google Gemini

El backend utiliza **Gemini 2.5 Flash**, un modelo rápido y eficiente.

**Proceso:**
1. Extrae texto del archivo cargado
2. Crea un prompt estructurado con instrucciones
3. Envía el texto a Gemini para procesamiento
4. Parsea la respuesta JSON
5. Valida que contenga los campos requeridos

**Prompt utilizado:**
```
Extrae la siguiente información del texto y devuelve SOLO un JSON válido:
- cliente: nombre del cliente
- monto: cantidad en números
- fecha: fecha del documento
- tipo_solicitud: tipo de solicitud (Venta, Queja, Factura, etc.)

Responde SOLO con JSON válido, sin explicaciones adicionales.
```

## 🔐 Variables de Entorno

Crear un archivo `.env` en la raíz con:
```
GEMINI_API_KEY=tu_clave_api_de_google_gemini
```

## 🧪 Tests

Ejecutar los tests:
```bash
pytest tests/
```

El proyecto incluye tests para validar:
- Extracción de texto de diferentes formatos
- Manejo de archivos vacíos
- Validación de respuestas JSON

## 📦 Instalación de Dependencias

```bash
pip install -r requirements.txt
```

**Dependencias principales:**
- `fastapi>=0.104.0` - Framework web
- `uvicorn>=0.24.0` - Servidor ASGI
- `python-docx>=0.8.11` - Lectura de DOCX
- `pandas>=2.0.0` - Lectura de XLSX
- `python-dotenv>=1.0.0` - Manejo de .env
- `google-generativeai>=0.3.0` - API de Gemini

## 🔄 Flujo de Procesamiento

```
1. Usuario carga archivo (Frontend)
   ↓
2. POST /api/process (Backend)
   ↓
3. Extracción de texto (extractors.py)
   ↓
4. Procesamiento con Gemini (main.py)
   ↓
5. Validación de JSON (validators.py)
   ↓
6. Respuesta al cliente (Frontend)
```

## ⚠️ Manejo de Errores

El backend maneja varios tipos de errores:

| Error | Causa | Solución |
|-------|-------|----------|
| Archivo vacío | El archivo no contiene datos | Selecciona un archivo con contenido |
| Formato no soportado | Extensión diferente a .txt/.docx/.xlsx | Usa formatos soportados |
| Encoding inválido | Archivo con encoding desconocido | Convierte a UTF-8 |
| JSON inválido | Gemini no devolvió JSON válido | Reintenta o verifica el prompt |

## 🚀 Mejoras Realizadas

### Codificación de Archivos
- Soporte automático para UTF-8 y Latin-1
- Fallback a ignorar errores de encoding
- Prevención de crashes por archivos mal codificados

### Validación
- Validación de archivos no vacíos
- Verificación de extracción exitosa
- Validación de JSON con campos requeridos

### Logging
- Mensajes de error detallados
- Traceback para debugging
- Responses con descripciones claras

## 📞 Contacto

Para preguntas o problemas, por favor abre un issue en el repositorio.
python src/main.py
```

The application will read the specified text files and extract the required information, returning it in a structured JSON format.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.
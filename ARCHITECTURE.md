# 🏗️ Arquitectura del Proyecto - Text-to-Structured-Data

Documentación técnica de la arquitectura, componentes y flujo de datos del proyecto.

---

## 📊 Diagrama General

```
┌─────────────────────────────────────────────────────────────────┐
│                        USUARIO                                   │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     │ Arrastra archivo
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                             │
│                 http://localhost:5173                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ DragDropUpload Component                                 │   │
│  │ - Maneja drag & drop                                     │   │
│  │ - Valida archivos                                        │   │
│  │ - Envía archivo al backend                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                       │
│                          │ POST /api/process                     │
│                          ▼                                       │
└─────────────────────────────────────────────────────────────────┘
                            │
                   ┌────────┴────────┐
                   │                 │
                   ▼                 │
         ┌──────────────────┐        │
         │ Validar archivo  │        │
         │ - No vacío       │        │
         │ - Formato válido │        │
         └──────────────────┘        │
                   │                 │
                   ├─ Error ─────────┼──┐
                   │                 │  │
                   ▼                 │  │
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (FastAPI)                            │
│                 http://localhost:8000                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ POST /api/process                                        │   │
│  │ (src/main.py)                                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                       │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ extract_text()                                           │   │
│  │ (src/extractors.py)                                      │   │
│  │                                                           │   │
│  │ TXT  → decode UTF-8/Latin-1                              │   │
│  │ DOCX → extract paragraphs                                │   │
│  │ XLSX → convert to string                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                       │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Google Gemini API                                        │   │
│  │ Model: gemini-2.5-flash                                  │   │
│  │                                                           │   │
│  │ Input: raw_text + prompt                                 │   │
│  │ Output: JSON response                                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                       │
│                          ▼                                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ validate_json_response()                                 │   │
│  │ (src/validators.py)                                      │   │
│  │                                                           │   │
│  │ Verifica campos:                                         │   │
│  │ ✓ cliente                                                │   │
│  │ ✓ monto                                                  │   │
│  │ ✓ fecha                                                  │   │
│  │ ✓ tipo_solicitud                                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                          │                                       │
└──────────────────────────┼───────────────────────────────────────┘
                           │
                ┌──────────┴──────────┐
                │                     │
                ▼ Success             ▼ Error
         ┌────────────────┐    ┌────────────────┐
         │  JSON válido   │    │ Error message  │
         └────────────────┘    └────────────────┘
                │                     │
                └──────────┬──────────┘
                           │
                           ▼ Response
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Actualiza UI)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ ProcessViewer Component                                  │   │
│  │ - Muestra texto extraído                                 │   │
│  │ - Muestra JSON estructurado                              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ StatusDashboard Component                                │   │
│  │ - Cliente: [nombre]                                      │   │
│  │ - Monto: [cantidad]                                      │   │
│  │ - Fecha: [fecha]                                         │   │
│  │ - Tipo: [tipo_solicitud]                                 │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ Estructura de Archivos Detallada

### Backend (Text-to-Structured-Data)

```
Text-to-Structured-Data/
│
├── src/
│   ├── __init__.py
│   │
│   ├── main.py                    # Núcleo del servidor
│   │   ├── FastAPI app setup
│   │   ├── CORS configuration
│   │   ├── POST /api/process
│   │   │   ├── Validación de archivo
│   │   │   ├── Extracción de texto
│   │   │   ├── Procesamiento con Gemini
│   │   │   ├── Validación de JSON
│   │   │   └── Respuesta al cliente
│   │   ├── GET /
│   │   └── Manejo de errores global
│   │
│   ├── extractors.py               # Lógica de extracción
│   │   ├── extract_text()
│   │   │   ├── .txt handling
│   │   │   │   ├── UTF-8 decoding
│   │   │   │   ├── Latin-1 fallback
│   │   │   │   └── Error handling
│   │   │   ├── .docx handling
│   │   │   │   └── Paragraph extraction
│   │   │   └── .xlsx handling
│   │   │       └── DataFrame to string
│   │
│   └── validators.py               # Validación de respuestas
│       └── validate_json_response()
│           ├── Check: cliente
│           ├── Check: monto
│           ├── Check: fecha
│           └── Check: tipo_solicitud
│
├── tests/
│   ├── __init__.py
│   └── test_extractors.py         # Tests unitarios
│
├── .env                           # Variables de entorno
├── .gitignore
├── requirements.txt               # Dependencias Python
└── README.md

```

### Frontend (text-to-structured-data-ui)

```
text-to-structured-data-ui/
│
├── src/
│   ├── components/
│   │   ├── DragDropUpload.tsx      # Componente principal de carga
│   │   │   ├── State: dragActive, error
│   │   │   ├── handleDrag()
│   │   │   ├── handleDrop()
│   │   │   ├── processFile()
│   │   │   └── Render upload area + error message
│   │   │
│   │   ├── ProcessViewer.tsx       # Visualizador de resultados
│   │   │   ├── Props: rawText, jsonData
│   │   │   ├── Left panel: raw text
│   │   │   └── Right panel: formatted JSON
│   │   │
│   │   ├── StatusDashboard.tsx     # Panel de resumen
│   │   │   ├── Props: data
│   │   │   └── Display: cliente, monto, fecha, tipo
│   │   │
│   │   └── index.ts               # Exports
│   │
│   ├── pages/
│   │   ├── Home.tsx               # Página principal
│   │   │   ├── State management
│   │   │   ├── Layout
│   │   │   └── Component composition
│   │   └── index.ts
│   │
│   ├── styles/
│   │   └── globals.css            # Tailwind + estilos globales
│   │
│   ├── types/
│   │   └── index.ts               # TypeScript types
│   │
│   ├── App.tsx                    # Root component
│   └── main.tsx                   # Entry point
│
├── public/
│   └── index.html
│
├── package.json                   # Dependencias npm
├── tsconfig.json
├── vite.config.ts                 # Configuración Vite
├── postcss.config.cjs             # Configuración PostCSS (CommonJS)
├── tailwind.config.js             # Configuración Tailwind
└── README.md

```

---

## 🔄 Flujo de Datos Detallado

### 1. Upload Phase (Usuario → Frontend)

```
Usuario arrastra archivo
    ↓
DragDropUpload.handleDrop() captura el evento
    ↓
ValidationChecks:
  - files.length > 0?
  - Archivo no vacío?
  - Extensión soportada?
    ↓
processFile(file: File)
    ↓
FormData.append('file', file)
    ↓
setLoading(true)
setError(null)
```

### 2. Network Phase (Frontend → Backend)

```
axios.post('http://localhost:8000/api/process', formData)
    ↓
Content-Type: multipart/form-data
    ↓
POST body:
{
  file: <bytes del archivo>
}
    ↓
Backend recibe la solicitud
```

### 3. Processing Phase (Backend)

```
/api/process endpoint recibe request
    ↓
Validación 1: ¿Archivo vacío?
    ├─ Sí → return 400 "El archivo está vacío"
    └─ No → continuar
    ↓
Validación 2: Extracción de texto
    ├─ extract_text(filename, content)
    ├─ Según extensión:
    │  ├─ .txt: decode UTF-8/Latin-1
    │  ├─ .docx: extract paragraphs
    │  └─ .xlsx: convert dataframe
    └─ No → return 400 "No se pudo extraer texto"
    ↓
Validación 3: Enviar a Gemini
    ├─ Crear prompt con instrucciones
    ├─ Llamar modelo gemini-2.5-flash
    └─ Recibir respuesta JSON
    ↓
Validación 4: Parse JSON
    ├─ Intenta json.loads(response)
    ├─ Si falla, intenta extraer JSON de markdown
    └─ Si falla, error 500
    ↓
Validación 5: Validar campos
    ├─ validate_json_response(data)
    ├─ Check: cliente, monto, fecha, tipo_solicitud
    └─ Si faltan campos, error
    ↓
Response 200 OK:
{
  "raw_text": "...",
  "structured_data": {...}
}
```

### 4. Rendering Phase (Backend → Frontend)

```
response.data recibida por frontend
    ↓
Validación: ¿Contiene error?
    ├─ Sí → setError(message)
    └─ No → setJsonData(data)
    ↓
Callback: onUpload(rawText)
    ↓
setLoading(false)
    ↓
UI renderiza:
  ├─ ProcessViewer con raw_text y structured_data
  ├─ StatusDashboard con los datos
  └─ Oculta el upload area (mientras haya datos)
```

---

## 🔗 Integración de Componentes

### Frontend Component Tree

```
App.tsx
└── Home.tsx
    ├── DragDropUpload.tsx
    │   └── Maneja: onUpload, setLoading, setJsonData
    ├── StatusDashboard.tsx
    │   └── Props: data (jsonData)
    └── ProcessViewer.tsx (condicional: {rawText && jsonData})
        └── Props: rawText, jsonData
```

### State Management (Home.tsx)

```typescript
const [rawText, setRawText] = useState<string>('');
const [jsonData, setJsonData] = useState<any>(null);
const [loading, setLoading] = useState<boolean>(false);

// Flow:
// 1. User uploads → setLoading(true)
// 2. Backend responds → setRawText() + setJsonData()
// 3. Components render updated data
// 4. Done → setLoading(false)
```

---

## 🔐 Seguridad y Validación

### Frontend Security

```
✓ Validación de tipo de archivo en cliente
✓ No almacena datos sensibles
✓ CORS habilitado en backend
✓ Usa axios para sanitizar requests
✓ Error handling sin exponer internals
```

### Backend Security

```
✓ Validación de archivo no vacío
✓ Validación de campos JSON requeridos
✓ Manejo de excepciones global
✓ Logging seguro sin datos sensibles
✓ API Key en variables de entorno
```

---

## 🚀 Performance Considerations

### Frontend

```
Optimizaciones:
- React.FC con TypeScript tipado
- Uso de hooks eficientes
- Tailwind CSS (build-time purge)
- Vite para bundling rápido
- Hot module replacement en desarrollo

Limitaciones:
- Máximo 1 archivo por vez
- No hay compresión de archivo en cliente
```

### Backend

```
Optimizaciones:
- FastAPI (async/await ready)
- Gemini 2.5 Flash (rápido y eficiente)
- Manejo de errores con early returns
- Caching potencial de respuestas

Limitaciones:
- Sin rate limiting
- Sin almacenamiento de resultados
- API calls síncronos
```

---

## 📡 Protocolos y Estándares

### HTTP Communication

```
POST /api/process
├── Request:
│   ├── Content-Type: multipart/form-data
│   ├── Body: FormData con archivo
│   └── Timeout: 30s (por defecto axios)
│
└── Response:
    ├── Status: 200 (éxito), 400/500 (error)
    ├── Content-Type: application/json
    └── Body: {raw_text, structured_data} o {error}
```

### JSON Schema

```json
// Request
{
  "file": "<multipart binary>"
}

// Success Response (200)
{
  "raw_text": "Texto extraído del archivo...",
  "structured_data": {
    "cliente": "string",
    "monto": "string",
    "fecha": "string",
    "tipo_solicitud": "string"
  }
}

// Error Response (400/500)
{
  "error": "Descripción del error"
}
```

---

## 🧪 Testing Strategy

### Backend Tests (tests/test_extractors.py)

```python
✓ test_txt_extraction()
✓ test_docx_extraction()
✓ test_xlsx_extraction()
✓ test_empty_file()
✓ test_invalid_encoding()
✓ test_json_validation()
```

### Frontend Testing (Manual)

```
✓ Drag & drop file
✓ Display raw text
✓ Display structured JSON
✓ Show status dashboard
✓ Handle errors gracefully
✓ Responsive on mobile
```

---

## 📊 Escalabilidad

### Mejoras Futuras

**Frontend:**
- [ ] Múltiples archivos simultáneamente
- [ ] Historial de procesamientos
- [ ] Exportar JSON/CSV
- [ ] Dark/Light mode toggle
- [ ] Autenticación de usuarios

**Backend:**
- [ ] Rate limiting
- [ ] Caché de resultados
- [ ] Base de datos para histórico
- [ ] Soporte para más formatos (PDF, JSON)
- [ ] Autenticación API
- [ ] Webhooks para notificaciones

**Infraestructura:**
- [ ] Docker containers
- [ ] Kubernetes orchestration
- [ ] CI/CD pipeline
- [ ] Monitoring y logging
- [ ] Load balancing

---

## 🔗 Dependencias Clave

### Backend Dependencies

```
fastapi>=0.104.0         # Web framework
uvicorn>=0.24.0          # ASGI server
python-docx>=0.8.11      # DOCX reading
pandas>=2.0.0            # XLSX reading
python-dotenv>=1.0.0     # .env loading
google-generativeai      # Gemini API
```

### Frontend Dependencies

```
react@18.2.0             # UI library
typescript@5.0.0         # Type safety
tailwindcss@3.0.0        # CSS framework
axios@1.6.0              # HTTP client
lucide-react@0.263.0     # Icons
vite@4.0.0               # Build tool
```

---

## 📚 Referencias de Documentación

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Hooks](https://react.dev/reference/react)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Google Gemini API](https://ai.google.dev/)

---

**Última actualización:** Febrero 16, 2026

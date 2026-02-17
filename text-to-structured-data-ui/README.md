# Text to Structured Data UI

Una interfaz web moderna construida con React y TypeScript para convertir documentos no estructurados en datos JSON estructurados. El frontend se comunica con un servidor FastAPI que utiliza Google Gemini para el procesamiento de datos.

## ✨ Características

- **Drag & Drop Upload**: Interfaz intuitiva para cargar archivos `.txt`, `.docx` y `.xlsx`
- **Process Viewer**: Visualiza el texto extraído y los datos JSON lado a lado
- **Status Dashboard**: Panel de estado que muestra cliente, monto, fecha y tipo de solicitud
- **Manejo de Errores**: Mensajes claros cuando algo falla
- **Interfaz Responsiva**: Diseño adaptable con Tailwind CSS
- **Indicadores de Carga**: Feedback visual durante el procesamiento

## 🛠️ Tecnologías Utilizadas

- **React 18**: Librería de UI con hooks
- **TypeScript**: Tipado estático para mayor seguridad
- **Tailwind CSS**: Framework CSS moderno y responsive
- **Vite**: Build tool rápido y eficiente
- **Axios**: Cliente HTTP para comunicación con backend
- **Lucide React**: Iconos modernos

## 🚀 Inicio Rápido

### Requisitos

- Node.js 14+
- npm o yarn
- Backend ejecutándose en `http://localhost:8000`

### Instalación

1. **Instala dependencias:**
   ```bash
   npm install
   ```

2. **Inicia el servidor de desarrollo:**
   ```bash
   npm run dev
   ```

3. **Abre en el navegador:**
   ```
   http://localhost:5173
   ```

### Build para Producción

```bash
npm run build
```

Genera un build optimizado en la carpeta `dist/`.

## 📁 Estructura del Proyecto

```
src/
├── components/
│   ├── DragDropUpload.tsx    # Componente de carga de archivos
│   ├── ProcessViewer.tsx     # Visualizador de texto y JSON
│   ├── StatusDashboard.tsx   # Panel de datos extraídos
│   └── index.ts              # Exports de componentes
├── pages/
│   ├── Home.tsx              # Página principal
│   └── index.ts
├── styles/
│   └── globals.css           # Estilos globales + Tailwind
├── types/
│   └── index.ts              # Tipos TypeScript
├── App.tsx                   # Componente raíz
└── main.tsx                  # Punto de entrada
```

## 🎨 Componentes Principales

### DragDropUpload.tsx
Componente para cargar archivos mediante drag & drop.

**Props:**
- `onUpload: (text: string) => void` - Callback cuando se extrae texto
- `setLoading: (loading: boolean) => void` - Controla estado de carga
- `setJsonData: (data: any) => void` - Establece datos estructurados

**Features:**
- Drag & drop intuitivo
- Validación de archivos
- Manejo de errores con mensajes claros
- Indicador visual de área activa

**Formatos soportados:**
- `.txt` - Archivos de texto plano
- `.docx` - Documentos Word
- `.xlsx` - Hojas de cálculo Excel

### ProcessViewer.tsx
Muestra el texto extraído y los datos JSON procesados.

**Props:**
- `rawText: string` - Texto extraído del archivo
- `jsonData: any` - Datos estructurados JSON

**Vista:**
- Panel izquierdo: Texto extraído (Dirty Text)
- Panel derecho: JSON estructurado (Pretty JSON)

### StatusDashboard.tsx
Panel que muestra los campos clave extraídos.

**Props:**
- `data: any` - Objeto JSON con los datos estructurados

**Campos mostrados:**
- 👤 Cliente: Nombre del cliente
- 💵 Monto: Cantidad numérica
- 📅 Fecha: Fecha del documento
- 📋 Tipo de Solicitud: Categoría (Venta, Queja, Factura, etc.)

## 🔄 Flujo de Datos

```
Usuario arrastra archivo
    ↓
DragDropUpload valida el archivo
    ↓
axios.post('http://localhost:8000/api/process')
    ↓
Backend procesa y devuelve datos
    ↓
ProcessViewer muestra resultados
    ↓
StatusDashboard muestra resumen
```

## 🌐 Comunicación con Backend

### Endpoint Usado
```
POST http://localhost:8000/api/process
Content-Type: multipart/form-data
```

### Request
```javascript
const formData = new FormData();
formData.append('file', file);
axios.post('http://localhost:8000/api/process', formData)
```

### Response
```json
{
  "raw_text": "Texto completo extraído...",
  "structured_data": {
    "cliente": "Nombre del cliente",
    "monto": "1000",
    "fecha": "2025-02-16",
    "tipo_solicitud": "Venta"
  }
}
```

## 🎨 Estilos y Theming

### Configuración Tailwind
- **Colores**: Esquema oscuro (gray-900, blue-500)
- **Tipografía**: Fuentes moderna y legible
- **Espaciado**: Proporcional y coherente
- **Componentes**: Fully responsive

### Archivos CSS
- `globals.css` - Estilos globales y configuración Tailwind

## 🔧 Scripts Disponibles

| Script | Descripción |
|--------|-----------|
| `npm run dev` | Inicia servidor de desarrollo con Vite |
| `npm run build` | Crea build optimizado para producción |
| `npm run preview` | Sirve el build de producción localmente |

## ⚠️ Manejo de Errores

El frontend muestra mensajes de error claros:

```typescript
// Ejemplo de manejo de error
catch (error: any) {
  const errorMessage = error.response?.data?.error || 'Error al procesar el archivo';
  setError(errorMessage);
}
```

**Errores comunes:**
- Archivo vacío
- Formato no soportado
- Encoding inválido
- Falla en la API

## 🔒 Configuración PostCSS

El proyecto usa `postcss.config.cjs` (CommonJS) debido a que `package.json` tiene `"type": "module"`.

**Plugins incluidos:**
- Tailwind CSS
- Autoprefixer

## 🚀 Mejoras Realizadas

### Problemas Solucionados
1. **PostCSS Error**: Convertido a `.cjs` con sintaxis CommonJS
2. **Manejo de Errores**: Mensajes claros en la UI
3. **Estados de Carga**: Feedback visual mejorado
4. **Validación de Archivos**: Soporte para múltiples formatos

### Enhancements
- Mejor UX con indicadores visuales
- Errores capturados y mostrados al usuario
- Componentes reutilizables y bien tipados
- Estilos modernos y responsivos

## 📦 Dependencias Principales

```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.0.0",
  "axios": "^1.6.0",
  "lucide-react": "^0.263.0",
  "tailwindcss": "^3.0.0",
  "typescript": "^5.0.0",
  "vite": "^4.0.0"
}
```

## 🐛 Debugging

### Chrome DevTools
Abre las DevTools con `F12`:
- **Console**: Errores y logs de JavaScript
- **Network**: Ver las peticiones al backend
- **Sources**: Debugging de código TypeScript

### Logs Útiles
```typescript
console.error('Error al procesar:', error);
console.log('Respuesta del servidor:', response.data);
```

## 📱 Responsividad

El diseño es totalmente responsivo:
- **Mobile**: Columna única, optimizado para touch
- **Tablet**: Grid 2 columnas
- **Desktop**: Layout completo con 2 columnas

## 🔐 Consideraciones de Seguridad

- ✅ CORS habilitado en backend
- ✅ Validación de archivos en frontend
- ✅ No almacena datos sensibles en el cliente
- ✅ Comunica a través de HTTPS (en producción)

## 📝 Ejemplo de Uso

```typescript
// Home.tsx
const [rawText, setRawText] = useState<string>('');
const [jsonData, setJsonData] = useState<any>(null);
const [loading, setLoading] = useState<boolean>(false);

return (
  <div className="min-h-screen bg-gray-900">
    <DragDropUpload 
      onUpload={setRawText}
      setLoading={setLoading}
      setJsonData={setJsonData}
    />
    {jsonData && (
      <>
        <ProcessViewer rawText={rawText} jsonData={jsonData} />
        <StatusDashboard data={jsonData} />
      </>
    )}
  </div>
);
```

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor:
1. Haz fork del repositorio
2. Crea una rama para tu feature
3. Comitea tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT.

## 👤 Autor

Ricardo MV

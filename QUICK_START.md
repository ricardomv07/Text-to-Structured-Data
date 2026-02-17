# 🚀 Guía de Inicio Rápido - Text-to-Structured-Data

Una guía paso a paso para poner en funcionamiento la aplicación completa en tu máquina local.

## 📋 Requisitos Previos

- **Python 3.8+** - [Descargar](https://www.python.org/downloads/)
- **Node.js 14+** - [Descargar](https://nodejs.org/)
- **API Key de Google Gemini** - [Obtener](https://ai.google.dev/)
- **Git** (opcional) - [Descargar](https://git-scm.com/)

### Verificar Instalaciones

Abre una terminal y ejecuta:

```powershell
# Verificar Python
python --version

# Verificar Node.js y npm
node --version
npm --version
```

---

## 🔑 Configuración Inicial - API Key

1. Obtén tu API Key en: https://ai.google.dev/
2. Copia la clave
3. Navega a la carpeta `Text-to-Structured-Data`
4. Crea un archivo `.env`:
   ```
   GEMINI_API_KEY=tu_clave_aqui
   ```

---

## 🏗️ Instalación - Backend

### Paso 1: Navega a la carpeta del backend

```powershell
cd Text-to-Structured-Data
```

### Paso 2: Crea un entorno virtual (Recomendado)

```powershell
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### Paso 3: Instala dependencias

```powershell
pip install -r requirements.txt
```

### Paso 4: Verifica la instalación

```powershell
python -c "import fastapi; import google.generativeai; print('✅ Dependencias OK')"
```

### Paso 5: Inicia el servidor

```powershell
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Esperarás ver:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

✅ **Backend está listo** - Accede a `http://localhost:8000`

---

## 🎨 Instalación - Frontend

### Paso 1: Abre una nueva terminal y navega a la carpeta

```powershell
cd text-to-structured-data-ui
```

### Paso 2: Instala dependencias

```powershell
npm install
```

### Paso 3: Inicia el servidor de desarrollo

```powershell
npm run dev
```

**Esperarás ver:**
```
VITE v4.0.0  ready in XXX ms

➜  Local:   http://localhost:5173/
```

✅ **Frontend está listo** - Accede a `http://localhost:5173`

---

## 🧪 Prueba la Aplicación

### Opción 1: Crear un archivo de prueba

1. Abre un editor de texto (Notepad, VSCode, etc.)
2. Copia este contenido:

```
Cliente: Juan García
Monto: $5,000.00
Fecha: 15 de febrero de 2025
Tipo: Venta de servicios de consultoría

Se realizó una consulta de 5 horas para optimización de procesos.
Factura #001-2025
```

3. Guarda como `prueba.txt`

### Opción 2: Cargar el archivo

1. Abre `http://localhost:5173` en tu navegador
2. Arrastra el archivo `prueba.txt` al área de drag & drop
3. Espera a que procese
4. Verifica los resultados

---

## 📊 Resultado Esperado

Deberías ver:

**Texto extraído (izquierda):**
```
Cliente: Juan García
Monto: $5,000.00
Fecha: 15 de febrero de 2025
Tipo: Venta de servicios de consultoría
...
```

**Datos estructurados (derecha):**
```json
{
  "cliente": "Juan García",
  "monto": "5000",
  "fecha": "15/02/2025",
  "tipo_solicitud": "Venta"
}
```

**Dashboard:**
- 👤 Cliente: Juan García
- 💵 Monto: $5000
- 📅 Fecha: 15/02/2025
- 📋 Tipo: Venta

---

## 🆘 Troubleshooting

### Error: "module is not found"

**Problema:** Backend no inicia

**Solución:**
```powershell
# Asegúrate de estar en la carpeta correcta
cd Text-to-Structured-Data

# Instala las dependencias nuevamente
pip install -r requirements.txt

# Reinicia
python -m uvicorn src.main:app --reload
```

### Error: "Port 8000 already in use"

**Problema:** Otro proceso usa el puerto 8000

**Solución:**
```powershell
# Usa otro puerto
python -m uvicorn src.main:app --reload --port 8001

# Luego actualiza la URL en frontend
# src/components/DragDropUpload.tsx
# Cambia: http://localhost:8000
# Por: http://localhost:8001
```

### Error: "Port 5173 already in use"

**Problema:** Otro proceso usa el puerto 5173

**Solución:**
```powershell
# Vite usará el siguiente puerto disponible automáticamente
npm run dev
```

### El archivo no procesa

**Solución:**
1. Verifica que el backend esté corriendo (deberías ver logs)
2. Abre DevTools (F12) → Console → verifica si hay errores
3. Revisa que el API Key sea válido
4. Prueba con un archivo más pequeño

### "GEMINI_API_KEY not found"

**Problema:** No se encuentra la clave de API

**Solución:**
1. Verifica que existe el archivo `.env` en `Text-to-Structured-Data/`
2. Verifica que la clave sea correcta
3. Reinicia el servidor backend

---

## 📁 Estructura de Carpetas

```
ricardo/
├── README.md                          # Guía general
├── CHANGELOG.md                       # Cambios realizados
├── QUICK_START.md                     # Este archivo
│
├── Text-to-Structured-Data/           # Backend (FastAPI)
│   ├── .env                          # Variables de entorno
│   ├── src/
│   │   ├── main.py                   # Servidor
│   │   ├── extractors.py             # Extracción de texto
│   │   └── validators.py             # Validación JSON
│   ├── tests/
│   ├── requirements.txt              # Dependencias
│   └── README.md
│
└── text-to-structured-data-ui/        # Frontend (React)
    ├── src/
    │   ├── components/
    │   ├── pages/
    │   ├── App.tsx
    │   └── main.tsx
    ├── package.json
    ├── tsconfig.json
    └── README.md
```

---

## 🔧 Comandos Útiles

### Backend

```powershell
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar con hot reload
python -m uvicorn src.main:app --reload

# Ejecutar en puerto diferente
python -m uvicorn src.main:app --port 8001

# Ver documentación interactiva
# Abre: http://localhost:8000/docs

# Ver esquema OpenAPI
# Abre: http://localhost:8000/openapi.json
```

### Frontend

```powershell
# Instalar dependencias
npm install

# Desarrollo con hot reload
npm run dev

# Build para producción
npm run build

# Previsualizar build
npm run preview

# Limpiar node_modules
rm -r node_modules
npm install
```

---

## 🌐 URLs Importantes

| Servicio | URL | Descripción |
|----------|-----|-----------|
| Frontend | http://localhost:5173 | Interfaz web |
| Backend API | http://localhost:8000 | API REST |
| API Docs | http://localhost:8000/docs | Documentación Swagger |
| API Redoc | http://localhost:8000/redoc | Documentación ReDoc |

---

## 📚 Documentación Completa

Para más detalles, consulta:

- **[README.md](./README.md)** - Descripción general
- **[Text-to-Structured-Data/README.md](./Text-to-Structured-Data/README.md)** - Documentación backend
- **[text-to-structured-data-ui/README.md](./text-to-structured-data-ui/README.md)** - Documentación frontend
- **[CHANGELOG.md](./CHANGELOG.md)** - Cambios realizados

---

## 🎯 Próximos Pasos

Una vez que tengas la aplicación funcionando:

1. ✅ Prueba con diferentes tipos de archivos (TXT, DOCX, XLSX)
2. ✅ Prueba con archivos más grandes
3. ✅ Explora la API en http://localhost:8000/docs
4. ✅ Lee el código y entiende la arquitectura
5. ✅ Considera hacer cambios o mejoras

---

## 💡 Tips y Trucos

### Desarrollo Eficiente

1. **Mantén dos terminales abiertas:**
   - Una para el backend
   - Una para el frontend

2. **DevTools del navegador:**
   - Abre F12 para ver la consola
   - Network tab para ver las peticiones
   - Console para debugging

3. **Logging:**
   - En backend: `print()` para ver logs
   - En frontend: `console.log()` en DevTools

### Archivos de Prueba

Crea archivos de prueba en diferentes formatos:

**TXT:**
```
Cliente: Test User
Monto: 1000
Fecha: 2025-02-16
Tipo: Venta
```

**DOCX:** Crea en Word con el mismo contenido

**XLSX:** Crea en Excel con columnas: Cliente, Monto, Fecha, Tipo

---

## 🆘 Contacto y Soporte

Si tienes problemas:

1. Revisa el [CHANGELOG.md](./CHANGELOG.md) para ver qué se cambió
2. Verifica los logs del terminal
3. Abre DevTools (F12) en el navegador
4. Consulta la documentación de cada módulo

---

## ✨ ¡Listo!

Ahora estás listo para:
- 🚀 Usar la aplicación
- 📖 Estudiar el código
- 🔧 Hacer modificaciones
- 📈 Escalar la aplicación

**Buena suerte! 🎉**

---

**Última actualización:** Febrero 16, 2026

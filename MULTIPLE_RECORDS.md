# Funcionalidad de Múltiples Registros

## 📊 Descripción General

El sistema ahora puede extraer automáticamente **múltiples registros** de documentos que contienen tablas o listas de transacciones, y guardarlos todos en la base de datos en una sola operación.

## ✨ Características Principales

### 1. Extracción Automática de Múltiples Registros
Cuando procesas un archivo Excel, imagen o documento que contiene una tabla con múltiples filas, el sistema:
- ✅ Detecta automáticamente cada fila/transacción
- ✅ Extrae cada una como un registro independiente
- ✅ Normaliza y valida todos los registros
- ✅ Devuelve un array con todos los datos extraídos

### 2. Guardado en Batch
El endpoint `/api/save` ahora soporta:
- ✅ Guardar un solo registro (compatibilidad hacia atrás)
- ✅ Guardar múltiples registros en una sola transacción
- ✅ Mejor rendimiento al guardar muchos registros a la vez

## 📝 Ejemplo Práctico

### Escenario: Procesar una tabla de ventas

**Entrada: Archivo Excel con tabla**
```
| Fecha              | Cliente                    | Tipo        | Producto/Servicio        | Cantidad | Monto  | Estatus     |
|--------------------|----------------------------|-------------|--------------------------|----------|--------|-------------|
| 01 de enero 2026   | Ana Patricia Gómez Vargas  | Venta       | Laptop HP Pavilion       | 2        | 25000  | Completada  |
| 05 de enero 2026   | Jorge Luis Ramírez Ortiz   | Venta       | Impresora Multifuncional | 1        | 8500   | Completada  |
| 10 de enero 2026   | Sofía Martínez Delgado     | Venta       | Tablet Samsung Galaxy    | 3        | 18900  | En proceso  |
```

**Salida del Endpoint `/api/process`:**
```json
{
  "raw_text": "Texto extraído completo del archivo...",
  "structured_data": [
    {
      "cliente": "Ana Patricia Gómez Vargas",
      "monto": 25000,
      "fecha": "01/01/2026",
      "tipo_solicitud": "Venta"
    },
    {
      "cliente": "Jorge Luis Ramírez Ortiz",
      "monto": 8500,
      "fecha": "05/01/2026",
      "tipo_solicitud": "Venta"
    },
    {
      "cliente": "Sofía Martínez Delgado",
      "monto": 18900,
      "fecha": "10/01/2026",
      "tipo_solicitud": "Venta"
    }
  ],
  "record_count": 3,
  "message": "Se extrajeron 3 registros. Revisa y presiona 'Guardar' para almacenar todos en la base de datos."
}
```

## 🔧 Uso del API

### 1. Procesar Documento
```bash
curl -X POST http://localhost:8000/api/process \
  -H "Content-Type: multipart/form-data" \
  -F "file=@ventas_enero_2026.xlsx"
```

**Respuesta:**
- `structured_data`: Array de registros extraídos
- `record_count`: Número de registros encontrados
- `message`: Mensaje descriptivo basado en la cantidad de registros

### 2. Guardar Múltiples Registros

**Opción A: Guardar todos los registros extraídos**
```bash
curl -X POST http://localhost:8000/api/save \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "cliente": "Ana Patricia Gómez Vargas",
        "monto": 25000,
        "fecha": "01/01/2026",
        "tipo_solicitud": "Venta"
      },
      {
        "cliente": "Jorge Luis Ramírez Ortiz",
        "monto": 8500,
        "fecha": "05/01/2026",
        "tipo_solicitud": "Venta"
      }
    ]
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "message": "2 registros guardados exitosamente",
  "saved_count": 2,
  "records": [
    {
      "id": 101,
      "cliente": "Ana Patricia Gómez Vargas",
      "monto": 25000,
      "fecha": "01/01/2026",
      "tipo_solicitud": "Venta",
      "created_at": "2026-02-18T10:30:00"
    },
    {
      "id": 102,
      "cliente": "Jorge Luis Ramírez Ortiz",
      "monto": 8500,
      "fecha": "05/01/2026",
      "tipo_solicitud": "Venta",
      "created_at": "2026-02-18T10:30:00"
    }
  ]
}
```

**Opción B: Guardar un solo registro (backwards compatible)**
```bash
curl -X POST http://localhost:8000/api/save \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "cliente": "Ana Patricia Gómez Vargas",
      "monto": 25000,
      "fecha": "01/01/2026",
      "tipo_solicitud": "Venta"
    }
  }'
```

**Respuesta:**
```json
{
  "success": true,
  "message": "Registro guardado exitosamente",
  "id": 101
}
```

## 🏗️ Arquitectura Interna

### Flujo de Procesamiento

```
1. Usuario sube archivo Excel/imagen con tabla
   ↓
2. extractors.py extrae texto del archivo
   ↓
3. Gemini AI analiza el texto y detecta múltiples registros
   ↓
4. validators.py valida cada registro en el array
   ↓
5. Normalización: convierte fechas, limpia datos
   ↓
6. Retorna array de registros al frontend
   ↓
7. Usuario revisa y confirma
   ↓
8. database.save_batch_data() guarda todos en una transacción
   ↓
9. Confirmación con IDs de todos los registros guardados
```

### Componentes Modificados

#### `src/validators.py`
```python
def validate_json_response(response):
    """
    Valida respuesta de la IA
    - Si es un dict → lo convierte a [dict]
    - Si es una lista → valida cada elemento
    - Retorna siempre una lista normalizada
    """
```

#### `src/database.py`
```python
def save_batch_data(records: list, raw_text: str = None, filename: str = None):
    """
    Guarda múltiples registros en una sola transacción
    - Más eficiente que guardar uno por uno
    - Rollback automático si hay error en cualquier registro
    """
```

#### `src/main.py`
- **Prompt mejorado**: Instruye explícitamente a Gemini para extraer arrays
- **Parsing flexible**: Detecta arrays `[]` y objetos `{}` en la respuesta
- **Endpoint `/api/save`**: Ahora maneja tanto objetos individuales como arrays

## 🎯 Ventajas

### Performance
- **Una transacción** en lugar de N transacciones
- Reduce llamadas a la base de datos
- Más rápido para grandes volúmenes

### Confiabilidad
- **Atomicidad**: O se guardan todos o ninguno (rollback automático)
- Evita registros parcialmente guardados
- Mejor manejo de errores

### Experiencia de Usuario
- **Un solo click** para guardar 10, 50 o 100 registros
- Mensaje claro de cuántos registros se extrajeron
- Confirmación con todos los IDs generados

## 📊 Casos de Uso

### ✅ Funciona Perfecto Para:
- Tablas de ventas mensuales
- Listas de facturas
- Reportes de transacciones
- Catálogos de productos
- Inventarios
- Listados de clientes

### ⚠️ Límites Recomendados
- **Óptimo**: 1-100 registros por archivo
- **Máximo**: ~200 registros (limitado por tamaño de respuesta de Gemini)
- Para archivos muy grandes (>200 filas), considerar dividir en múltiples archivos

## 🔍 Troubleshooting

### Problema: No extrae todos los registros
**Solución**: El texto extraído está limitado a 2000 caracteres en el prompt
- Ajustar `raw_text[:2000]` en main.py línea 162
- O usar extraction en chunks para archivos muy grandes

### Problema: Error al guardar algunos registros
**Solución**: Revisa los logs para ver qué registro específico falló
- Verifica campos requeridos: `cliente` y `tipo_solicitud`
- Todos los registros deben tener datos válidos

## 🚀 Próximas Mejoras Sugeridas

1. **Paginación en frontend**: Mostrar registros de 10 en 10 si hay muchos
2. **Edición individual**: Permitir editar/eliminar registros antes de guardar
3. **Preview mejorado**: Vista de tabla para múltiples registros
4. **Export**: Descargar registros extraídos como CSV/Excel
5. **Undo/Redo**: Deshacer guardado en batch si hubo error

---

**Versión**: 2.0
**Fecha**: Febrero 2026
**Autor**: Sistema Text-to-Structured-Data

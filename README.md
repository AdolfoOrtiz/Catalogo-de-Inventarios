# API REST Catálogo de Inventario - Proyecto Final Tópicos

API REST robusta desarrollada con **Django REST Framework (DRF)** para la gestión y administración de un **Catálogo de Inventario**, incluyendo autenticación por Token / Bearer, relaciones con proveedores, categorización de productos, búsqueda y filtros avanzados, administración de existencias (stock) y panel de administración en español.

---

## 🛠️ Tecnologías Utilizadas
- **Python 3.14**
- **Django 6.1**
- **Django REST Framework (DRF)**
- **django-filter** (Filtros avanzados por categoría, proveedor, estado y rangos)
- **Pillow** (Gestión de imágenes de productos)
- **SQLite3** (Base de datos preconfigurada y migrada)

---

## 🚀 Puesta en Marcha

### 1. Activar el Entorno Virtual
Desde una terminal (PowerShell o CMD) en la carpeta del proyecto:
```powershell
cd C:\Users\ortiz\OneDrive\Desktop\catalogo_inventario
.\.venv\Scripts\Activate.ps1
```

### 2. Iniciar el Servidor de Desarrollo
```powershell
python manage.py runserver
```
La API estará disponible en: `http://127.0.0.1:8000/`

---

## 👤 Cuentas y Credenciales Precreadas

| Rol | Usuario | Contraseña | Token de Autenticación |
|---|---|---|---|
| **Superusuario / Admin** | `admin` | `admin12345` | `e55bb2f0086484cf295f9ce0b0baf93ad9608f4b` |
| **Vendedor / Empleado** | `vendedor1` | `vendedor12345` | `2d26ddbdc32508988bd5363872d3000569be16eb` |

> El panel de administración está disponible en: `http://127.0.0.1:8000/admin/`

---

## 🔑 Autenticación en Encabezados (Headers)
La API acepta los dos estándares:
- `Authorization: Bearer <tu_token>`
- `Authorization: Token <tu_token>`

---

## 📋 Lista de Endpoints de la API

### 1. Autenticación y Cuentas
| Método | Endpoint | Descripción | Requiere Auth |
|---|---|---|---|
| `POST` | `/api/register/` | Registro de nuevos usuarios con confirmación de password | No |
| `POST` | `/api/custom-token/` o `/api/login/` | Obtiene el token de acceso enviando `username` y `password` | No |
| `GET` | `/api/me/` | Consulta información y rol del usuario autenticado | Sí |
| `PATCH` | `/api/me/` | Actualiza nombre, correo o contraseña del usuario | Sí |
| `POST` | `/api/reset-token/` | Invalida el token actual y genera uno nuevo | Sí |
| `POST` | `/api/logout/` | Cierra sesión y elimina el token de la base de datos | Sí |

### 2. Categorías
| Método | Endpoint | Descripción | Requiere Auth |
|---|---|---|---|
| `GET` | `/api/categorias/` | Lista todas las categorías (incluye contador y productos anidados) | Sí |
| `POST` | `/api/categorias/` | Crea una nueva categoría (`codigo`, `nombre`, `descripcion`) | Sí |
| `GET` | `/api/categorias/{id}/` | Detalle de categoría con sus productos anidados | Sí |
| `PUT` / `PATCH` | `/api/categorias/{id}/` | Actualiza una categoría | Sí |
| `DELETE` | `/api/categorias/{id}/` | Elimina una categoría | Sí |

### 3. Proveedores
| Método | Endpoint | Descripción | Requiere Auth |
|---|---|---|---|
| `GET` | `/api/proveedores/` | Lista proveedores con sus datos de contacto y total de productos | Sí |
| `POST` | `/api/proveedores/` | Registra un nuevo proveedor | Sí |
| `GET` | `/api/proveedores/{id}/` | Detalle del proveedor con productos suministrados | Sí |
| `PUT` / `PATCH` | `/api/proveedores/{id}/` | Actualiza datos del proveedor | Sí |
| `DELETE` | `/api/proveedores/{id}/` | Elimina un proveedor | Sí |

### 4. Productos (Catálogo de Inventario)
| Método | Endpoint | Descripción | Requiere Auth |
|---|---|---|---|
| `GET` | `/api/productos/` | Catálogo completo con paginación y serializers anidados | Sí |
| `POST` | `/api/productos/` | Crea un producto asociando `categoria` y `proveedor` | Sí |
| `GET` | `/api/productos/{id}/` | Detalle completo de producto (con `categoria_detalle` y `proveedor_detalle`) | Sí |
| `PUT` / `PATCH` | `/api/productos/{id}/` | Modifica datos del producto | Sí |
| `DELETE` | `/api/productos/{id}/` | Elimina un producto | Sí |
| `GET` | `/api/productos/bajo_stock/` | Lista rápida de productos con existencias en alerta o agotadas | Sí |
| `POST` | `/api/productos/{id}/ajustar_stock/` | Ajusta directamente el stock registrando el movimiento de almacén | Sí |

### 5. Administración de Existencias (Movimientos de Inventario)
| Método | Endpoint | Descripción | Requiere Auth |
|---|---|---|---|
| `GET` | `/api/movimientos/` | Historial de movimientos (entradas, salidas, ajustes) | Sí |
| `POST` | `/api/movimientos/` | Registra entrada o salida con validación atómica de existencias | Sí |
| `GET` | `/api/movimientos/{id}/` | Detalle del movimiento con producto y usuario responsable | Sí |

---

## 🔍 Búsquedas y Filtros Disponibles

1. **Filtro por Categoría:**
   `GET /api/productos/?categoria=1`
2. **Filtro por Proveedor:**
   `GET /api/productos/?proveedor=2`
3. **Búsqueda por texto (SKU, nombre, descripción, nombre de proveedor):**
   `GET /api/productos/?search=Dell`
   `GET /api/productos/?search=Makita`
4. **Filtro por Rango de Precios:**
   `GET /api/productos/?min_precio=1000&max_precio=15000`
5. **Filtro de Existencias Bajas / Agotadas:**
   `GET /api/productos/?bajo_stock=true`
6. **Ordenamiento:**
   `GET /api/productos/?ordering=precio` (ascendente)
   `GET /api/productos/?ordering=-precio` (descendente)
   `GET /api/productos/?ordering=stock_actual`

---

## 📮 Cómo Probarlo en Postman

1. Abre **Postman**.
2. Haz clic en el botón superior **Import**.
3. Selecciona el archivo:
   `C:\Users\ortiz\OneDrive\Desktop\catalogo_inventario\Postman_Collection_Inventario.json`
4. Verás la colección **"API Catálogo de Inventario - Proyecto Final Tópicos"** con todas las peticiones organizadas en carpetas con ejemplos listos para enviar.
5. Inicia el servidor con:
   ```powershell
   python manage.py runserver
   ```
6. En Postman, ejecuta la petición **"Obtener Token (Login / Custom Token)"**. Automáticamente se guardará el token en las variables y todas las demás solicitudes funcionarán sin configurar nada adicional.

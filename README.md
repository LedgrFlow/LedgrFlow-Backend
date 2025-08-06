# LedgerFlow Backend

Backend API para el sistema de gestión de libros contables desarrollado con Flask y PostgreSQL.

## Requisitos

- Python 3.8+
- PostgreSQL
- pip

## Instalación

1. Clona el repositorio:
```bash
git clone <repository-url>
cd ledgerflow-backend
```

2. Crea un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instala las dependencias:
```bash
pip install -r requirements.txt
```

4. Configura las variables de entorno:
```bash
cp env.example .env
# Edita el archivo .env con tus credenciales de base de datos
```

5. Configura la base de datos PostgreSQL:
   - Crea una base de datos llamada `ledgerflow_db`
   - Actualiza las credenciales en el archivo `.env`

6. Inicializa la base de datos:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## Ejecución

### Opción 1: Flask con recarga automática (Recomendado)
```bash
python app.py
```

### Opción 2: Usando Flask CLI
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000 --debug
```

### Opción 3: Usando Uvicorn (con adaptador WSGI)
```bash
uvicorn wsgi:app --host 0.0.0.0 --port 5000 --reload
```

El servidor estará disponible en `http://localhost:5000`

## Endpoints disponibles

### Rutas principales
- `GET /` - Página de bienvenida
- `GET /health` - Verificación del estado del servidor

### Autenticación
- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Iniciar sesión
- `GET /auth/me` - Obtener información del usuario actual (requiere JWT)

### Gestión de usuarios
- `GET /users/` - Obtener lista de usuarios (requiere JWT)
- `GET /users/<user_id>` - Obtener usuario específico (requiere JWT)
- `POST /users/` - Crear usuario (solo admin, requiere JWT)
- `PUT /users/<user_id>` - Actualizar usuario (requiere JWT)
- `DELETE /users/<user_id>` - Eliminar usuario (requiere JWT)

### Gestión de archivos
- `GET /files/` - Obtener lista de archivos del usuario (requiere JWT)
- `GET /files/<file_id>` - Obtener archivo específico con contenido (requiere JWT)
- `POST /files/` - Crear nuevo archivo (requiere JWT)
- `PUT /files/<file_id>` - Actualizar archivo (requiere JWT)
- `DELETE /files/<file_id>` - Eliminar archivo (requiere JWT)
- `GET /files/search` - Buscar archivos por nombre o extensión (requiere JWT)

### Análisis de archivos Ledger
- `GET /ledger/parser/<file_id>` - Análisis completo usando LedgerParser (requiere JWT)
- `GET /ledger/analyst/<file_id>` - Análisis completo usando LedgerAnalyst (requiere JWT)
- `POST /ledger/compare/<file_id>` - Comparar dos meses específicos (requiere JWT)
- `POST /ledger/alerts/<file_id>` - Detectar gastos inusuales (requiere JWT)
- `POST /ledger/cleanup` - Limpiar archivos temporales (requiere JWT)

### Noticias y Cambios de Moneda
- `GET /news/currency/rates` - Obtener tasas de cambio actuales
- `GET /news/currency/convert` - Convertir entre monedas
- `GET /news/news` - Obtener noticias por categoría
- `GET /news/news/finance` - Noticias financieras
- `GET /news/news/technology` - Noticias de tecnología
- `GET /news/news/crypto` - Noticias de criptomonedas
- `GET /news/news/status` - Estado de los servicios

**Nota**: Para más detalles sobre los endpoints de noticias y moneda, consulta [README_NEWS.md](README_NEWS.md)

### Parámetros de consulta para listado de usuarios
- `page` - Número de página (default: 1)
- `per_page` - Elementos por página (default: 10, máximo: 50)

### Parámetros de consulta para listado de archivos
- `page` - Número de página (default: 1)
- `per_page` - Elementos por página (default: 10, máximo: 50)

### Parámetros de consulta para búsqueda de archivos
- `q` - Término de búsqueda en el nombre del archivo
- `extension` - Filtrar por extensión (.ledger, .md, .txt, .markdown)

## Ejemplos de uso

### Registrar un usuario
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "username": "usuario123",
    "first_name": "Juan",
    "last_name": "Pérez",
    "password": "password123"
  }'
```

### Iniciar sesión
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "password": "password123"
  }'
```

### Obtener información del usuario actual
```bash
curl -X GET http://localhost:5000/auth/me \
  -H "Authorization: Bearer <tu_token_jwt>"
```

### Crear un archivo
```bash
curl -X POST http://localhost:5000/files/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <tu_token_jwt>" \
  -d '{
    "name": "mi_archivo.ledger",
    "file_content": "2024-01-01 * Compra de suministros\n  Gastos:Suministros     $50.00\n  Activos:Efectivo",
    "file_extension": ".ledger"
  }'
```

### Obtener lista de archivos
```bash
curl -X GET http://localhost:5000/files/ \
  -H "Authorization: Bearer <tu_token_jwt>"
```

### Buscar archivos
```bash
curl -X GET "http://localhost:5000/files/search?q=ledger&extension=.ledger" \
  -H "Authorization: Bearer <tu_token_jwt>"
```

### Analizar archivo Ledger (Parser)
```bash
curl -X GET http://localhost:5000/ledger/parser/<file_id> \
  -H "Authorization: Bearer <tu_token_jwt>"
```

### Analizar archivo Ledger (Analyst)
```bash
curl -X GET http://localhost:5000/ledger/analyst/<file_id> \
  -H "Authorization: Bearer <tu_token_jwt>"
```

### Comparar meses
```bash
curl -X POST http://localhost:5000/ledger/compare/<file_id> \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <tu_token_jwt>" \
  -d '{
    "month1": "2024-01",
    "month2": "2024-02"
  }'
```

### Detectar alertas
```bash
curl -X POST http://localhost:5000/ledger/alerts/<file_id> \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <tu_token_jwt>" \
  -d '{
    "threshold": 2.0
  }'
```

### Obtener tasas de cambio
```bash
curl -X GET http://localhost:5000/news/currency/rates
```

### Convertir monedas
```bash
curl -X GET "http://localhost:5000/news/currency/convert?amount=100&from=USD&to=EUR"
```

### Obtener noticias financieras
```bash
curl -X GET "http://localhost:5000/news/news/finance?count=5"
```

## Estructura del proyecto

```
ledgerflow-backend/
├── app.py              # Archivo principal de la aplicación
├── config.py           # Configuración de la aplicación
├── extensions.py       # Extensiones de Flask
├── requirements.txt    # Dependencias del proyecto
├── env.example         # Plantilla de variables de entorno
├── wsgi.py            # Archivo WSGI para Uvicorn
├── README.md          # Documentación del proyecto
├── README_NEWS.md     # Documentación de noticias y moneda
├── routes/            # Blueprints y rutas
│   ├── __init__.py
│   ├── main.py        # Rutas principales
│   ├── auth.py        # Rutas de autenticación
│   ├── users.py       # Rutas de gestión de usuarios
│   ├── files.py       # Rutas de gestión de archivos
│   ├── ledger_analysis.py # Rutas de análisis de ledger
│   └── news.py        # Rutas de noticias y moneda
├── models/            # Modelos de base de datos
│   ├── __init__.py
│   ├── user.py        # Modelo de Usuario
│   └── file.py        # Modelo de Archivo
├── schemas/           # Esquemas de validación
│   ├── __init__.py
│   ├── user_schema.py # Esquemas de Usuario
│   ├── file_schema.py # Esquemas de Archivo
│   └── news_schema.py # Esquemas de Noticias
├── utils/             # Utilidades
│   ├── __init__.py
│   ├── temp_file_manager.py # Gestor de archivos temporales
│   └── api_services.py      # Servicios de APIs externas
└── docs/              # Documentación adicional
    └── news_api.md    # Documentación detallada de API de noticias
``` 
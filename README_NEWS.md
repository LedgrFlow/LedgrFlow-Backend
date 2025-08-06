# Sección de Noticias y Cambios de Moneda

Esta sección del backend proporciona endpoints para obtener información sobre cambios de moneda y noticias financieras, tecnológicas y de criptomonedas.

## Características

### 🔄 Cambios de Moneda
- **Moneda base**: USD (Dólar estadounidense)
- **APIs utilizadas**:
  - **Primaria**: Free Currency API (requiere API key)
  - **Fallback**: Frankfurter API (gratuita, sin límites)
- **Conversión automática**: Si se usa Frankfurter API, convierte automáticamente de EUR a USD para mantener consistencia
- **Monedas soportadas**: 23 monedas principales incluyendo EUR, GBP, JPY, CNY, CAD, AUD, etc.

### 📰 Noticias
- **API utilizada**: Bing News Search API (requiere API key)
- **Categorías disponibles**:
  - **Finance**: Noticias financieras y económicas
  - **Technology**: Noticias de tecnología e innovación
  - **Crypto**: Noticias de criptomonedas y blockchain
  - **General**: Noticias generales
- **Límites**: Máximo 50 artículos por petición

## Configuración

### Variables de Entorno

Agrega las siguientes variables a tu archivo `.env`:

```bash
# Para cambios de moneda (opcional)
FREE_CURRENCY_API_KEY=tu_api_key_aqui

# Para noticias (requerido)
BING_NEWS_API_KEY=tu_api_key_aqui
```

### Obtención de API Keys

#### Free Currency API
1. Ve a [Free Currency API](https://freecurrencyapi.com/)
2. Regístrate para obtener una cuenta gratuita
3. Copia tu API key
4. **Nota**: Si no configuras esta API key, automáticamente usará Frankfurter API

#### Bing News Search API
1. Ve a [Microsoft Azure Portal](https://portal.azure.com/)
2. Crea un recurso de "Bing Search v7"
3. Obtén tu API key desde el portal
4. **Importante**: Esta API key es requerida para los endpoints de noticias

## Endpoints Disponibles

### Moneda

#### 1. Obtener Tasas de Cambio
```
GET /news/currency/rates
```

**Respuesta:**
```json
{
  "success": true,
  "base_currency": "USD",
  "rates": {
    "EUR": 0.85,
    "GBP": 0.73,
    "JPY": 110.25,
    // ... más monedas
  },
  "timestamp": "2024-01-15T10:30:00",
  "source": "Free Currency API"
}
```

#### 2. Convertir Monedas
```
GET /news/currency/convert?amount=100&from=USD&to=EUR
```

**Parámetros:**
- `amount` (float): Cantidad a convertir
- `from` (string): Moneda de origen
- `to` (string): Moneda de destino

**Respuesta:**
```json
{
  "success": true,
  "amount": 100,
  "from_currency": "USD",
  "to_currency": "EUR",
  "converted_amount": 85.0,
  "rate": 0.85,
  "timestamp": "2024-01-15T10:30:00",
  "source": "Free Currency API"
}
```

### Noticias

#### 1. Noticias por Categoría
```
GET /news/news?category=finance&count=10
```

**Parámetros:**
- `category`: finance, technology, crypto, general
- `count`: 1-50 (default: 10)

#### 2. Noticias Específicas
```
GET /news/news/finance?count=5
GET /news/news/technology?count=5
GET /news/news/crypto?count=5
```

**Respuesta:**
```json
{
  "success": true,
  "category": "finance",
  "count": 5,
  "news": [
    {
      "title": "Federal Reserve Announces New Policy",
      "description": "The Federal Reserve has announced...",
      "url": "https://example.com/news/article1",
      "published_date": "2024-01-15T09:00:00Z",
      "provider": "Financial Times",
      "category": "Business",
      "image_url": "https://example.com/images/article1.jpg"
    }
  ],
  "timestamp": "2024-01-15T10:30:00",
  "source": "Bing News API"
}
```

### Estado de Servicios

#### Verificar Estado
```
GET /news/news/status
```

**Respuesta:**
```json
{
  "currency_service": {
    "available": true,
    "source": "Free Currency API"
  },
  "news_service": {
    "available": true,
    "api_key_configured": true
  },
  "timestamp": "2024-01-15T10:30:00"
}
```

## Manejo de Errores

### Errores de Moneda
```json
{
  "success": false,
  "error": "Both currency APIs are unavailable",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Errores de Noticias
```json
{
  "success": false,
  "error": "Bing News API key not configured",
  "timestamp": "2024-01-15T10:30:00"
}
```

## Estructura del Código

```
routes/
├── news.py                 # Endpoints principales
utils/
├── api_services.py         # Servicios para APIs externas
schemas/
├── news_schema.py          # Esquemas de respuesta
docs/
├── news_api.md            # Documentación detallada
```

### Clases Principales

- **CurrencyService**: Maneja las APIs de cambio de moneda
- **NewsService**: Maneja la API de noticias
- **ServiceStatus**: Verifica el estado de los servicios

## Instalación y Uso

1. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

2. **Configurar variables de entorno:**
```bash
cp env.example .env
# Editar .env con tus API keys
```

3. **Ejecutar la aplicación:**
```bash
python app.py
```

4. **Probar endpoints:**
```bash
# Obtener tasas de cambio
curl http://localhost:5000/news/currency/rates

# Convertir monedas
curl "http://localhost:5000/news/currency/convert?amount=100&from=USD&to=EUR"

# Obtener noticias financieras
curl "http://localhost:5000/news/news/finance?count=5"
```

## Notas Importantes

1. **Moneda Base**: Todos los cambios usan USD como base para consistencia
2. **Fallback Automático**: Si Free Currency API falla, usa Frankfurter API
3. **Límites de API**: Respeta los límites de las APIs externas
4. **Logging**: Todos los errores y eventos se registran para debugging
5. **Timeouts**: Las peticiones tienen timeout de 10 segundos

## Troubleshooting

### Problemas Comunes

1. **Error "Bing News API key not configured"**
   - Verifica que `BING_NEWS_API_KEY` esté configurado en `.env`

2. **Error "Both currency APIs are unavailable"**
   - Verifica tu conexión a internet
   - Si tienes API key de Free Currency, verifica que sea válida

3. **Rates no disponibles**
   - Algunas monedas pueden no estar disponibles en todas las APIs
   - Verifica la lista de monedas soportadas

### Logs

Los logs se pueden encontrar en la consola donde ejecutas la aplicación. Busca mensajes que empiecen con:
- `INFO`: Información general
- `WARNING`: Advertencias (ej: API fallback)
- `ERROR`: Errores que requieren atención 
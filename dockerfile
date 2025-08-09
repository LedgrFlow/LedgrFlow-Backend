# Usamos una imagen oficial de Python
FROM python:3.11-slim

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el archivo de dependencias
COPY requirements.txt .

# Instalamos las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código fuente al contenedor
COPY . .

# Exportamos el puerto que usará Flask
EXPOSE 3000

# Variables de entorno por defecto (puedes sobrescribirlas al correr el contenedor)
ENV FLASK_APP=app.py \
    FLASK_ENV=development \
    PORT=3000 \
    DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ledgerflow \
    DB_HOST=localhost \
    DB_PORT=5432 \
    DB_NAME=ledgerflow_db \
    DB_USER=username \
    DB_PASSWORD=password \
    SECRET_KEY=your-secret-key-here-change-in-production \
    JWT_SECRET_KEY=your-jwt-secret-key-here-change-in-production \
    BCRYPT_LOG_ROUNDS=12 \
    CORS_ORIGINS=https://tuapp.com,http://localhost:5173

# Comando para ejecutar la aplicación Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]

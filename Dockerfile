# Imagen base oficial de Python (ligera)
FROM python:3.12-slim

# Evita archivos .pyc innecesarios y fuerza salida de logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar requirements.txt dentro del contenedor
COPY requirements.txt .

# Instalar las dependencias
# --no-cache-dir reduce bastante el tamaño final de la imagen
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la API dentro del contenedor
COPY . .

# Puerto documentado (hay que publicarlo con -p al hacer run)
EXPOSE 8000

# Puerto 8000 por defecto; si existe la variable PORT, se usa esa
CMD uvicorn api.app_api:app --host 0.0.0.0 --port ${PORT:-8000}

# 1. Imagen base basada en Python 3.10 (según especificación oficial de la práctica)
FROM python:3.10-slim

# Variables de entorno para optimizar la salida de Python en Docker
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 2. Directorio de trabajo
WORKDIR /app

# 3. Instalar herramientas del sistema necesarias para PostgreSQL y compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 4. Instalación de dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. Copiar el código fuente del proyecto
COPY . /app/

# 6. Copiar y dar permisos de ejecución al script ENTRYPOINT
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 7. Exponer el puerto estándar de Django
EXPOSE 8000

# 8. Configuración de ENTRYPOINT y comando por defecto
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

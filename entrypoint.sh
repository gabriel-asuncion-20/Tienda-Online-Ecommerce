#!/bin/sh
set -e

echo "=== Iniciando contenedor Django ==="

# Ejecutar migraciones automáticas en la base de datos
echo "Aplicando migraciones..."
python manage.py migrate --noinput

# Ejecutar el comando principal (por defecto: runserver o gunicorn)
exec "$@"

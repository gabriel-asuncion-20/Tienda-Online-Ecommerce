# Guía y Notas de Despliegue Continuo Simulado (deploy-notes.md)

**Asignatura:** Gestión de la Configuración de Software [GESCONSOF]  
**Práctica Nº:** 3 — Implementación de Flujo CI/CD con GitHub Actions y Docker  
**Institución:** Universidad Estatal de Milagro (UNEMI)  
**Sistema:** Tienda Online E-commerce (Django + PostgreSQL)  

---

## 1. Propósito del Documento
Este documento describe el procedimiento técnico estandarizado para reproducir el despliegue continuo de la aplicación web Django en un entorno simulado local o servidor externo independiente, asegurando paridad entre desarrollo, integración continua y producción mediante contenedores Docker.

---

## 2. Requisitos del Sistema
Antes de iniciar el despliegue, el host de destino debe contar con:
- **Sistema Operativo:** Linux (Ubuntu 22.04+ / Debian 12 / Fedora), macOS o WSL2 en Windows.
- **Docker Engine:** Versión 24.0 o superior (`docker --version`).
- **Docker Compose:** Plugin v2 (`docker compose version`).
- **Git:** Para clonar el repositorio de artefactos (`git --version`).
- **Puertos Disponibles:** Puerto `8000` (HTTP Django) y puerto `5432` (PostgreSQL local).

---

## 3. Procedimiento de Despliegue Paso a Paso (Entorno Externo)

### Paso 1: Preparación del Directorio Externo de Despliegue
Cree una carpeta independiente fuera del árbol de trabajo habitual:
```bash
mkdir -p ~/despliegue_simulado
cd ~/despliegue_simulado
```

### Paso 2: Descarga / Clonación del Proyecto
Clone la rama oficial del repositorio:
```bash
git clone -b actualizacion https://github.com/gabriel-asuncion-20/Tienda-Online-Ecommerce.git .
```
*(O copie los artefactos del proyecto al directorio si realiza una prueba offline)*.

### Paso 3: Configuración de Variables de Entorno
Genere el archivo de entorno de producción local a partir de la plantilla:
```bash
cp .env.example .env
```
Verifique los valores esenciales en `.env`:
```ini
DEBUG=True
SECRET_KEY=django-insecure-simulated-deployment-key-2026
ALLOWED_HOSTS=*
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

### Paso 4: Permisos de Ejecución
Asegúrese de que el script de inicio posea permisos de ejecución:
```bash
chmod +x entrypoint.sh
```

### Paso 5: Construcción y Puesta en Marcha con Docker Compose
Ejecute el orquestador en segundo plano para compilar la imagen base (Python 3.10) y levantar los servicios vinculados:
```bash
docker compose up -d --build
```

El orquestador ejecutará la siguiente secuencia automática:
1. Descarga de la imagen de base de datos `postgres:15-alpine`.
2. Verificación del `healthcheck` de PostgreSQL (`pg_isready`).
3. Construcción de la imagen Docker de Django (`python:3.10-slim`).
4. Ejecución del `entrypoint.sh`: aplicación automática de migraciones pendientes (`migrate --noinput`).
5. Inicio del servidor HTTP en `0.0.0.0:8000`.

---

## 4. Verificación y Validación de la Entrega

### 4.1. Inspección del Estado de Contenedores
```bash
docker compose ps
```
*Salida esperada:*
- `postgres_ecommerce_db`: Estado `Up (healthy)`, puerto `5432->5432`.
- `django_ecommerce_app`: Estado `Up`, puerto `8000->8000`.

### 4.2. Monitoreo de Registros (Logs)
```bash
docker compose logs -f web
```
Debe reflejar la conexión exitosa a la base de datos PostgreSQL y el arranque del servidor de Django.

### 4.3. Validación desde Terminal (Smoke Test)
```bash
curl -I http://localhost:8000/
```
*Resultado esperado:* Cabecera `HTTP/1.1 200 OK`.

### 4.4. Validación desde el Navegador Web
Abra su navegador e ingrese a:
```
http://localhost:8000/
```
Se presentará la interfaz principal de **MY_SHOP**, permitiendo la navegación de catálogo de productos, registro de cuentas de usuario, carrito de compras y gestión de órdenes.

---

## 5. Comandos de Operación y Mantenimiento

| Acción | Comando |
| :--- | :--- |
| **Ver logs en tiempo real** | `docker compose logs -f` |
| **Ejecutar pruebas en el contenedor** | `docker compose exec web python manage.py test` |
| **Crear superusuario admin** | `docker compose exec web python manage.py createsuperuser` |
| **Acceder a la shell de Django** | `docker compose exec web python manage.py shell` |
| **Acceder a la base de datos psql** | `docker compose exec db psql -U postgres -d ecommerce_db` |
| **Reiniciar los servicios** | `docker compose restart` |
| **Detener la aplicación** | `docker compose down` |
| **Detener y purgar volúmenes de datos** | `docker compose down -v` |

---

## 6. Procedimiento de Rollback en Caso de Fallas
Si una nueva versión del contenedor presenta fallos en producción:
1. Revertir a la versión o tag previo de la imagen Docker:
   ```bash
   docker tag django-ecommerce:previous django-ecommerce:latest
   docker compose up -d
   ```
2. Si los cambios involucran esquemas de base de datos:
   ```bash
   docker compose exec web python manage.py migrate <app_name> <migration_number>
   ```
3. Consultar las notas de versión y changelog en el repositorio de GitHub.

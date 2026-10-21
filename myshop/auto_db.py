import os
import sys
from urllib.parse import urlparse

def ensure_postgres_db_and_tables():
    """
    Verifica que la base de datos PostgreSQL configurada exista en el servidor.
    Si no existe, se conecta a la base de datos de administración 'postgres'
    y ejecuta CREATE DATABASE. Luego ejecuta las migraciones de Django
    para crear todas las tablas automáticamente.
    """
    # Evitar doble ejecución en el auto-reloader de runserver
    if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') != 'true':
        return

    # No ejecutar en comandos como makemigrations, collectstatic o test
    if len(sys.argv) > 1 and sys.argv[1] in ['makemigrations', 'collectstatic', 'help', 'test']:
        return

    db_url = os.getenv('DATABASE_URL')
    if db_url:
        parsed = urlparse(db_url)
        db_name = parsed.path.lstrip('/')
        db_user = parsed.username or 'postgres'
        db_password = parsed.password or ''
        db_host = parsed.hostname or 'localhost'
        db_port = parsed.port or 5432
    else:
        db_name = os.getenv('DB_NAME', 'ecommerce_db')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', 'postgres')
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = int(os.getenv('DB_PORT', '5432'))

    # Intentar importar psycopg (v3) o psycopg2
    try:
        import psycopg
        use_v3 = True
    except ImportError:
        try:
            import psycopg2
            use_v3 = False
        except ImportError:
            print("[PostgreSQL Auto-DB] Advertencia: Ni psycopg ni psycopg2 están instalados.")
            return

    # 1. Verificar y crear la base de datos si no existe
    try:
        # Nos conectamos a la BD de mantenimiento por defecto ('postgres')
        if use_v3:
            conn = psycopg.connect(
                dbname='postgres',
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                connect_timeout=5,
                autocommit=True
            )
        else:
            from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
            conn = psycopg2.connect(
                dbname='postgres',
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port,
                connect_timeout=5
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()

        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (db_name,))
        exists = cur.fetchone()

        if not exists:
            print(f"[PostgreSQL Auto-DB] Creando base de datos '{db_name}'...")
            cur.execute(f'CREATE DATABASE "{db_name}" ENCODING \'UTF8\';')
            print(f"[PostgreSQL Auto-DB] Base de datos '{db_name}' creada exitosamente.")
        else:
            print(f"[PostgreSQL Auto-DB] Base de datos '{db_name}' ya existe.")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"[PostgreSQL Auto-DB] Aviso de conexión a PostgreSQL: {e}")
        # Si no se pudo conectar como 'postgres', intentamos continuar
        pass

    # 2. Inicializar Django y ejecutar migraciones para crear tablas automáticamente
    try:
        import django
        from django.core.management import call_command
        
        django.setup()
        print("[PostgreSQL Auto-DB] Verificando y aplicando tablas (migraciones)...")
        call_command('migrate', interactive=False)
        print("[PostgreSQL Auto-DB] Tablas listas: Usuarios, Compras (Orders), Productos y Carrito.")
    except Exception as e:
        print(f"[PostgreSQL Auto-DB] Error al aplicar migraciones: {e}")

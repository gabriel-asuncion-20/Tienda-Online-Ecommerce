"""
WSGI config for myshop project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myshop.settings')

try:
    from myshop.auto_db import ensure_postgres_db_and_tables
    ensure_postgres_db_and_tables()
except Exception as e:
    print(f"[Auto-DB Warning]: {e}")

application = get_wsgi_application()
app = application

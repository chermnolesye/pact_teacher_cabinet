"""
WSGI config for pact project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
import time
import django
from django.core.wsgi import get_wsgi_application
from django.db import connection
from django.db.utils import OperationalError

def wait_for_db():
    connected = False
    while not connected:
        try:
            connection.ensure_connection()
            connected = True
        except OperationalError:
            print("Database unavailable, waiting 1 second...")
            time.sleep(1)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pact.settings')

wait_for_db()  

django.setup()
application = get_wsgi_application()


"""
ASGI config for ecommerce project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os
from decouple import config
from django.core.asgi import get_asgi_application

# Set the default settings module for the 'development' environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.environ.setdefault('ENVIRONMENT', config('ENVIRONMENT', default='development'))

application = get_asgi_application()

"""
ASGI config for quanlito_danpho project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quanlito_danpho.settings')

application = get_asgi_application()
"""
WSGI config for quanlito_danpho project.
"""

import os

from django.core.wsgi import get_wsgi_application

# Thiết lập file settings mặc định
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quanlito_danpho.settings')

application = get_wsgi_application()
# settings.py placeholder — do not add settings manually here yet.

# quanlito_danpho/settings.py

# quanlito_danpho/settings.py

INSTALLED_APPS = [
    # CÁC APPS MẶC ĐỊNH CỦA DJANGO
    'django.contrib.admin',
    'django.contrib.auth',    # <-- CẦN THIẾT cho auth.User
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # APPS CỦA BẠN
    'apps.core',
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'quanlytodanpho',      # <-- Tên database đã tạo
        'USER': 'root',         # <-- Tên người dùng MySQL
        'PASSWORD': '123456', # <-- Mật khẩu MySQL
        'HOST': '127.0.0.1',                  # Thường là localhost
        'PORT': '3306',                       # Port MySQL
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

# quanlito_danpho/settings.py (Thêm vào ĐẦU file)
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-duy(bạn-phải-thay-chuỗi-này-bằng-chuỗi-ngẫu-nhiên-của-riêng-bạn)' # <-- BẮT BUỘC

# ... (Các cấu hình khác như ALLOWED_HOSTS, DEBUG, v.v.)

# BỔ SUNG CÁC BIẾN CÒN LẠI
ROOT_URLCONF = 'quanlito_danpho.urls' # <-- BẮT BUỘC

# Cấu hình Templates (Quan trọng cho admin)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
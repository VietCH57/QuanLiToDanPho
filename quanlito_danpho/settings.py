# settings.py placeholder — do not add settings manually here yet.

# quanlito_danpho/settings.py
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-duy-demo-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']

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
    'apps.api',
    'apps.users',
    'citizen_app',
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Nếu muốn dùng MySQL, uncomment phần dưới và comment phần SQLite trên:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'quanlytodanpho',
#         'USER': 'root',
#         'PASSWORD': '123456',
#         'HOST': '127.0.0.1',
#         'PORT': '3306',
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
#         }
#     }
# }

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
        'DIRS': [BASE_DIR / 'templates'],  # Thêm thư mục templates chung
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

# Cấu hình Login/Logout redirect
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Middleware cơ bản
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Allowed hosts
ALLOWED_HOSTS = ['*']  # Chỉ dùng trong development
DEBUG = True  # Nhớ set False trong production
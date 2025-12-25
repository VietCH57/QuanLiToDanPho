"""
Django settings for quanlito_danpho project.
Cleaned & Optimized for: Vietnamese, REST API, Media Upload.
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ==========================================================
#  1. SECURITY & DEBUG
# ==========================================================
SECRET_KEY = 'django-insecure-change-me-please-complex-string'

# Bật DEBUG = True khi đang code. Khi deploy nhớ sửa thành False.
DEBUG = True

ALLOWED_HOSTS = ['*']


# ==========================================================
#  2. INSTALLED APPS (CÁC ỨNG DỤNG ĐƯỢC CÀI ĐẶT)
# ==========================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # --- Thư viện bên thứ 3 ---
    'rest_framework',          # Hỗ trợ tạo API
    'corsheaders',             # Hỗ trợ gọi API từ domain khác (nếu cần)

    # --- Ứng dụng nội bộ ---
    'apps.core',               # App chính: Quản lý dân cư, Khen thưởng...
    
    # 'citizen_app',           # (Đã tắt để tránh xung đột với apps.core)
]


# ==========================================================
#  3. MIDDLEWARE
# ==========================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # Thêm CORS
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'quanlito_danpho.urls'

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

WSGI_APPLICATION = 'quanlito_danpho.wsgi.application'


# ==========================================================
#  4. DATABASE
# ==========================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ==========================================================
#  5. PASSWORD VALIDATION
# ==========================================================
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    # Có thể comment dòng dưới nếu muốn pass đơn giản (vd: 123456) lúc dev
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# ==========================================================
#  6. LOCALIZATION (CẤU HÌNH TIẾNG VIỆT)
# ==========================================================
LANGUAGE_CODE = 'vi'        # Chuyển sang Tiếng Việt

TIME_ZONE = 'Asia/Ho_Chi_Minh'  # Múi giờ Việt Nam

USE_I18N = True
USE_TZ = True


# ==========================================================
#  7. STATIC & MEDIA FILES (CẤU HÌNH FILE ẢNH/CSS)
# ==========================================================
STATIC_URL = 'static/'

# Nơi lưu file ảnh upload (Minh chứng, Avatar...)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# ==========================================================
#  8. REST FRAMEWORK CONFIG
# ==========================================================
REST_FRAMEWORK = {
    # Sử dụng Session Auth (để dùng được hàm login/logout của Django)
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    # Mặc định phải đăng nhập mới xem được API (An toàn)
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    # Phân trang (Pagination)
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# Cấu hình CORS (Cho phép mọi nguồn truy cập lúc Dev)
CORS_ALLOW_ALL_ORIGINS = True 

# ==========================================================
#  9. OTHER SETTINGS
# ==========================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
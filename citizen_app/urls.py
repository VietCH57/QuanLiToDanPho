from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. Đường dẫn cho Users (Login, Dashboard...)
    path('users/', include('apps.users.urls')),
    
    # 2. Đường dẫn cho Core (Quản lý dân cư, hộ khẩu...)
    # Vì bạn viết logic chính ở đây, nên bắt buộc phải có dòng này
    path('core/', include('apps.core.urls')), 
    
    # 3. Đường dẫn API (TẠM THỜI ĐỂ ẨN)
    # Vì trong thư mục apps/api/ chưa có file urls.py nên ta để dấu # ở đầu
    # Khi nào bạn tạo file apps/api/urls.py thì mới xóa dấu # đi
    # path('api/', include('apps.api.urls')),

    # 4. Trang chủ mặc định -> Chuyển hướng ngay về trang đăng nhập
    path('', lambda request: redirect('users:login')), 
]
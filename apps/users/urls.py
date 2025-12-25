from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    
    # Hộ khẩu
    path('hokhau/', views.hokhau_list_view, name='hokhau_list'),
    path('hokhau/add/', views.hokhau_form_view, name='hokhau_form'),
    path('hokhau/<int:pk>/', views.hokhau_detail_view, name='hokhau_detail'),
    path('hokhau/<int:pk>/edit/', views.hokhau_form_view, name='hokhau_edit'),
    
    # Nhân khẩu
    path('nhankhau/', views.nhankhau_list_view, name='nhankhau_list'),
    path('nhankhau/add/', views.nhankhau_form_view, name='nhankhau_form'),
    path('nhankhau/<int:pk>/', views.nhankhau_detail_view, name='nhankhau_detail'),
    path('nhankhau/<int:pk>/edit/', views.nhankhau_form_view, name='nhankhau_edit'),
    
    # Tạm trú - Tạm vắng
    path('tamtru/', views.tamtru_list_view, name='tamtru_list'),
    path('tamtru/add/', views.tamtru_form_view, name='tamtru_form'),
    
    # Khen thưởng
    path('khenthuong/', views.khenthuong_list_view, name='khenthuong_list'),
    path('khenthuong/add/', views.khenthuong_form_view, name='khenthuong_form'),
    
    # Quản lý người dùng (Admin only)
    path('users/manage/', views.user_list_view, name='user_list'),
    path('users/manage/add/', views.user_form_view, name='user_form'),
    path('users/manage/<int:pk>/edit/', views.user_form_view, name='user_edit'),
    path('users/manage/<int:pk>/delete/', views.user_delete_view, name='user_delete'),
]

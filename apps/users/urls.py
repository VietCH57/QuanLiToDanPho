from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('nhan-khau/', views.nhan_khau_view, name='nhan_khau'),
    path('ho-khau/', views.ho_khau_view, name='ho_khau'),
    path('tam-tru-tam-vang/', views.tam_tru_tam_vang_view, name='tam_tru_tam_vang'),
    path('khen-thuong/', views.khen_thuong_view, name='khen_thuong'),
    path('quan-ly-nguoi-dung/', views.quan_ly_nguoi_dung_view, name='quan_ly_nguoi_dung'),
]
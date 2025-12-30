from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('nhan-khau/', views.nhan_khau_view, name='nhan_khau'),
    path('ho-khau/', views.ho_khau_view, name='ho_khau'),
    path('tam-tru-tam-vang/', views.tam_tru_tam_vang_view, name='tam_tru_tam_vang'),
    path('tam-tru-tam-vang/khai-bao-tam-tru/', views.khai_bao_tam_tru_view, name='khai_bao_tam_tru'),
    path('tam-tru-tam-vang/khai-bao-tam-vang/', views.khai_bao_tam_vang_view, name='khai_bao_tam_vang'),
    path('tam-tru-tam-vang/xem-truoc-tam-tru/', views.xem_truoc_tam_tru_view, name='xem_truoc_tam_tru'),
    path('tam-tru-tam-vang/xem-truoc-tam-vang/', views.xem_truoc_tam_vang_view, name='xem_truoc_tam_vang'),
    path('tam-tru-tam-vang/gui-don-tam-tru/', views.gui_don_tam_tru_view, name='gui_don_tam_tru'),
    path('tam-tru-tam-vang/gui-don-tam-vang/', views.gui_don_tam_vang_view, name='gui_don_tam_vang'),
    path('tam-tru-tam-vang/chi-tiet-tam-tru/<int:pk>/', views.chi_tiet_tam_tru_view, name='chi_tiet_tam_tru'),
    path('tam-tru-tam-vang/chi-tiet-tam-vang/<int:pk>/', views.chi_tiet_tam_vang_view, name='chi_tiet_tam_vang'),
    path('khen-thuong/', views.khen_thuong_view, name='khen_thuong'),
    path('quan-ly-nguoi-dung/', views.quan_ly_nguoi_dung_view, name='quan_ly_nguoi_dung'),
    # Admin CRUD nhân khẩu
    path('admin/nhan-khau/them/', views.admin_them_nhan_khau, name='admin_them_nhan_khau'),
    path('admin/nhan-khau/sua/<int:pk>/', views.admin_sua_nhan_khau, name='admin_sua_nhan_khau'),
    path('admin/nhan-khau/xoa/<int:pk>/', views.admin_xoa_nhan_khau, name='admin_xoa_nhan_khau'),
    # Admin thống kê nhân khẩu
    path('admin/nhan-khau/thong-ke/', views.admin_thong_ke_nhan_khau, name='admin_thong_ke_nhan_khau'),
    # Admin tách hộ
    path('admin/ho-khau/tach/<int:ho_id>/', views.admin_tach_ho, name='admin_tach_ho'),
]
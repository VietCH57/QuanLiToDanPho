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
    path('ho-khau/chi-tiet/<int:ho_id>/', views.chi_tiet_ho_khau_view, name='chi_tiet_ho_khau_view'),
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
    path('admin/nhan-khau/lich-su/<int:thanh_vien_id>/', views.lich_su_nhan_khau, name='lich_su_nhan_khau'),
    # Admin thống kê nhân khẩu
    path('admin/nhan-khau/thong-ke/', views.admin_thong_ke_nhan_khau, name='admin_thong_ke_nhan_khau'),
    # Admin hộ khẩu
    path('admin/ho-khau/lich-su/<int:ho_id>/', views.lich_su_ho_khau, name='lich_su_ho_khau'),
    # Admin tách hộ
    path('admin/ho-khau/tach/<int:ho_id>/', views.admin_tach_ho, name='admin_tach_ho'),
    path('admin/ho-khau/them/', views.admin_them_ho_khau, name='admin_them_ho_khau'),
    path('admin/ho-khau/xoa/<int:ho_id>/', views.admin_xoa_ho_khau, name='admin_xoa_ho_khau'),
    # Admin quản lý phần thưởng
    path('admin/phan-thuong/tao-dot-moi/', views.tao_dot_phat_thuong_moi, name='tao_dot_phat_thuong_moi'),
    path('admin/phan-thuong/cap-nhat-dot/<int:dot_id>/', views.cap_nhat_trang_thai_dot, name='cap_nhat_trang_thai_dot'),
    path('admin/phan-thuong/tao-dot/', views.tao_dot_phat_thuong, name='tao_dot_phat_thuong'),
    path('admin/phan-thuong/phat-thuong-hoc-tap/', views.phat_thuong_hoc_tap, name='phat_thuong_hoc_tap'),
    path('admin/phan-thuong/duyet-thanh-tich/<int:thanh_tich_id>/', views.duyet_thanh_tich, name='duyet_thanh_tich'),
    # Admin - New workflow pages
    path('admin/tao-dot-phat-thuong/', views.tao_dot_phat_thuong_page, name='tao_dot_phat_thuong_page'),
    path('admin/quan-ly-phat-thuong/', views.quan_ly_phat_thuong_page, name='quan_ly_phat_thuong_page'),
    path('admin/duyet-dot/<int:dot_id>/', views.duyet_thanh_tich_theo_dot, name='duyet_thanh_tich_theo_dot'),
    path('admin/chi-tiet-dot/<int:dot_id>/', views.chi_tiet_dot_phat_thuong, name='chi_tiet_dot_phat_thuong'),
    path('admin/sua-dot/<int:dot_id>/', views.sua_dot_phat_thuong, name='sua_dot_phat_thuong'),
    path('admin/xoa-dot/<int:dot_id>/', views.xoa_dot_phat_thuong, name='xoa_dot_phat_thuong'),
    # Citizen - Thành tích học tập và phần thưởng
    path('thanh-tich-hoc-tap/', views.thanh_tich_hoc_tap_view, name='thanh_tich_hoc_tap'),
    path('thanh-tich-hoc-tap/gui/', views.gui_thanh_tich, name='gui_thanh_tich'),
    path('phan-thuong-cua-toi/', views.phan_thuong_cua_toi, name='phan_thuong_cua_toi'),
    path('xac-nhan-nhan-qua/<int:lich_su_id>/', views.xac_nhan_nhan_qua, name='xac_nhan_nhan_qua'),
]
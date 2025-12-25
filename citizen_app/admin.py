from django.contrib import admin
from .models import HoGiaDinh, ThanhVien, ToDanPho

# ==========================================================
#  CẤU HÌNH HIỂN THỊ PHỤ (INLINES)
# ==========================================================

class ThanhVienInline(admin.TabularInline):
    """
    Cho phép xem và thêm nhanh thành viên ngay trong giao diện Hộ gia đình.
    """
    model = ThanhVien
    extra = 1  # Hiển thị sẵn 1 dòng trống để nhập
    fields = ('ho_ten', 'ngay_sinh', 'quan_he_voi_chu_ho') # Chỉ hiện các trường chính cho gọn


# ==========================================================
#  QUẢN LÝ TỔ DÂN PHỐ
# ==========================================================

@admin.register(ToDanPho)
class ToDanPhoAdmin(admin.ModelAdmin):
    """
    Quản lý danh sách Tổ dân phố.
    """
    list_display = ('id', 'ten_to')
    search_fields = ('ten_to',) # Cho phép tìm kiếm theo tên tổ


# ==========================================================
#  QUẢN LÝ HỘ GIA ĐÌNH
# ==========================================================

@admin.register(HoGiaDinh)
class HoGiaDinhAdmin(admin.ModelAdmin):
    """
    Quản lý Hộ gia đình.
    Có tích hợp xem danh sách thành viên bên trong (Inline).
    """
    list_display = ('id', 'chu_ho', 'dia_chi', 'to_dan_pho')
    
    # Tính năng tìm kiếm mạnh mẽ:
    # - Tìm theo tên chủ hộ (nếu chu_ho là ForeignKey)
    # - Tìm theo địa chỉ
    search_fields = ('dia_chi', 'chu_ho__ho_ten') 
    
    # Bộ lọc bên phải: Lọc theo Tổ dân phố
    list_filter = ('to_dan_pho',)
    
    inlines = [ThanhVienInline]


# ==========================================================
#  QUẢN LÝ THÀNH VIÊN
# ==========================================================

@admin.register(ThanhVien)
class ThanhVienAdmin(admin.ModelAdmin):
    """
    Quản lý chi tiết từng Nhân khẩu.
    """
    list_display = ('id', 'ho_ten', 'ngay_sinh', 'quan_he_voi_chu_ho', 'ho_gia_dinh')
    
    # Tìm kiếm theo tên và hộ gia đình
    search_fields = ('ho_ten', 'ho_gia_dinh__id')
    
    # Lọc theo quan hệ (ví dụ: xem bao nhiêu người là Chủ hộ, bao nhiêu là Con...)
    list_filter = ('quan_he_voi_chu_ho', 'ngay_sinh')
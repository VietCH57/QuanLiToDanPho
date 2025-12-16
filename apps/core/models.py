# core.models placeholder

from django.db import models
from django.conf import settings
from django.conf import settings # <--- dòng này phải đúng
# ...
# from apps.users.models import User # Giả sử bạn có User model tùy chỉnh trong apps/users

# ==========================================================
# PHẦN 1: QUẢN LÝ TỔ DÂN PHỐ (Hộ Gia Đình & Thành Viên)
# ==========================================================

class HoGiaDinh(models.Model):
    ma_ho = models.CharField(max_length=10, unique=True, verbose_name="Mã Hộ")
    dia_chi = models.CharField(max_length=255, verbose_name="Địa Chỉ")
    ten_chu_ho = models.CharField(max_length=100, verbose_name="Tên Chủ Hộ")

    def __str__(self):
        return f"Hộ: {self.ma_ho} - Chủ: {self.ten_chu_ho}"
    
    class Meta:
        verbose_name_plural = "Hộ Gia Đình" # Tên hiển thị trong Admin

class ThanhVien(models.Model):
    # Khóa ngoại: Liên kết Thành Viên với một Hộ Gia Đình
    ho_gia_dinh = models.ForeignKey(
        HoGiaDinh, 
        on_delete=models.CASCADE, # Nếu Hộ Gia Đình bị xóa, các thành viên cũng bị xóa
        related_name='thanh_vien_trong_ho'
    )
    ho_ten = models.CharField(max_length=100, verbose_name="Họ Tên")
    ngay_sinh = models.DateField(verbose_name="Ngày Sinh")
    quan_he_chu_ho = models.CharField(max_length=50, verbose_name="Quan Hệ với Chủ Hộ")

    def __str__(self):
        return self.ho_ten

    class Meta:
        verbose_name_plural = "Thành Viên"
        
# ==========================================================
# PHẦN 2: QUẢN LÝ CẤP PHẦN THƯỞNG
# ==========================================================

class DanhMucPhanThuong(models.Model):
    ten_phan_thuong = models.CharField(max_length=150, unique=True, verbose_name="Tên Phần Thưởng")
    mo_ta = models.TextField(blank=True, verbose_name="Mô Tả")
    # Sử dụng DecimalField cho giá trị tiền tệ, tránh sai số float
    gia_tri = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="Giá Trị (VNĐ)")

    def __str__(self):
        return self.ten_phan_thuong
    
    class Meta:
        verbose_name_plural = "Danh Mục Phần Thưởng"

class LichSuPhatThuong(models.Model):
    # Khóa ngoại: Liên kết Lịch sử với Thành Viên nhận thưởng
    thanh_vien = models.ForeignKey(
        ThanhVien, 
        on_delete=models.CASCADE, 
        related_name='lich_su_nhan_thuong'
    )
    # Khóa ngoại: Liên kết với Phần Thưởng đã được cấp
    phan_thuong = models.ForeignKey(DanhMucPhanThuong, on_delete=models.CASCADE)
    ngay_cap_phat = models.DateField(auto_now_add=True, verbose_name="Ngày Cấp Phát")
    
    # Liên kết với User Admin (Người cấp thưởng), settings.AUTH_USER_MODEL là User model mặc định của Django
    nguoi_cap = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, # Nếu người cấp bị xóa, trường này chỉ đặt là NULL
        null=True, 
        blank=True
    ) 
    ghi_chu = models.TextField(blank=True, verbose_name="Ghi Chú")

    def __str__(self):
        return f"{self.thanh_vien.ho_ten} nhận {self.phan_thuong.ten_phan_thuong} ({self.ngay_cap_phat})"
    
    class Meta:
        verbose_name_plural = "Lịch Sử Phát Thưởng"
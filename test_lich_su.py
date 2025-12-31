"""
Script kiểm tra xem các bảng lịch sử đã được tạo chưa
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'citizen_app.settings')
django.setup()

from apps.core.models import LichSuThayDoiHo, LichSuThayDoiThanhVien, HoGiaDinh
from django.db import connection

print("=== KIỂM TRA CÁC BẢNG LỊCH SỬ ===\n")

# Kiểm tra các bảng có tồn tại không
with connection.cursor() as cursor:
    cursor.execute("SHOW TABLES")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("Các bảng trong database:")
    for table in tables:
        if 'lich_su' in table.lower():
            print(f"  ✓ {table}")
    print()

# Thử query các bảng lịch sử
try:
    count_ho = LichSuThayDoiHo.objects.count()
    print(f"✓ Bảng LichSuThayDoiHo: {count_ho} bản ghi")
except Exception as e:
    print(f"✗ Lỗi LichSuThayDoiHo: {e}")

try:
    count_tv = LichSuThayDoiThanhVien.objects.count()
    print(f"✓ Bảng LichSuThayDoiThanhVien: {count_tv} bản ghi")
except Exception as e:
    print(f"✗ Lỗi LichSuThayDoiThanhVien: {e}")

print("\n=== DANH SÁCH HỘ KHẨU ===\n")
ho_list = HoGiaDinh.objects.all()[:5]
for ho in ho_list:
    print(f"Hộ: {ho.ma_ho} - {ho.dia_chi}")
    print(f"  Số thành viên: {ho.thanh_vien_trong_ho.count()}")
    print(f"  Lịch sử thay đổi: {ho.lich_su_thay_doi.count()}")
    print()

print("\n=== HƯỚNG DẪN ===")
print("Nếu các bảng lịch sử chưa tồn tại, chạy:")
print("  python manage.py makemigrations")
print("  python manage.py migrate")

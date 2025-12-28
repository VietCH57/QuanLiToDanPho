import random
from datetime import date, timedelta
from apps.core.models import HoGiaDinh, ThanhVien, DanhMucPhanThuong, LichSuPhatThuong
from django.db import transaction

# Dữ liệu giả để random
HO_LIST = ['Nguyễn', 'Trần', 'Lê', 'Phạm', 'Hoàng', 'Huỳnh', 'Phan', 'Vũ', 'Võ', 'Đặng']
TEN_DEM_NAM = ['Văn', 'Hữu', 'Đức', 'Thành', 'Minh', 'Hoàng']
TEN_DEM_NU = ['Thị', 'Ngọc', 'Thu', 'Mai', 'Phương', 'Thanh']
TEN_NAM = ['Hùng', 'Dũng', 'Nam', 'Khánh', 'Long', 'Quân', 'Bình', 'Cường']
TEN_NU = ['Hoa', 'Lan', 'Hương', 'Thảo', 'Trang', 'Huyền', 'Ly', 'Anh']

DI_CHI_LIST = ['Phố Huế', 'Hàng Bài', 'Tràng Tiền', 'Bà Triệu', 'Lý Thường Kiệt']

def generate_name(gender):
    ho = random.choice(HO_LIST)
    if gender == 'Nam':
        dem = random.choice(TEN_DEM_NAM)
        ten = random.choice(TEN_NAM)
    else:
        dem = random.choice(TEN_DEM_NU)
        ten = random.choice(TEN_NU)
    return f"{ho} {dem} {ten}"

def create_sample_data():
    with transaction.atomic():
        print("🔄 Đang xóa dữ liệu cũ (Core)...")
        LichSuPhatThuong.objects.all().delete()
        ThanhVien.objects.all().delete()
        HoGiaDinh.objects.all().delete()
        DanhMucPhanThuong.objects.all().delete()
        
        print("🔄 Đang tạo Danh mục Phần thưởng...")
        pt1 = DanhMucPhanThuong.objects.create(ten_phan_thuong="Vở ô ly", gia_tri=5000, mo_ta="Vở viết cho học sinh")
        pt2 = DanhMucPhanThuong.objects.create(ten_phan_thuong="Tiền mặt 50k", gia_tri=50000, mo_ta="Quà trung thu")
        pt3 = DanhMucPhanThuong.objects.create(ten_phan_thuong="Giấy khen", gia_tri=2000, mo_ta="Thành tích xuất sắc")

        print("🔄 Đang tạo Hộ gia đình và Cư dân...")
        for i in range(1, 6): # Tạo 5 hộ
            ma_ho = f"HK{i:03d}" # VD: HK001
            dia_chi = f"Số {i * 5}, {random.choice(DI_CHI_LIST)}"
            ho = HoGiaDinh.objects.create(ma_ho=ma_ho, dia_chi=dia_chi)
            
            # 1. Tạo Chủ hộ (Nam)
            chu_ho_name = generate_name('Nam')
            chu_ho = ThanhVien.objects.create(
                ho_gia_dinh=ho,
                ho_ten=chu_ho_name,
                cccd=f"0012{random.randint(10000000, 99999999)}",
                ngay_sinh=date(1975, random.randint(1, 12), random.randint(1, 28)),
                gioi_tinh='Nam',
                quan_he_chu_ho='Chủ hộ',
                la_chu_ho=True,
                trang_thai='ThuongTru'
            )

            # 2. Tạo Vợ (Nữ)
            ThanhVien.objects.create(
                ho_gia_dinh=ho,
                ho_ten=generate_name('Nu'),
                cccd=f"0013{random.randint(10000000, 99999999)}",
                ngay_sinh=date(1978, random.randint(1, 12), random.randint(1, 28)),
                gioi_tinh='Nu',
                quan_he_chu_ho='Vợ',
                la_chu_ho=False,
                trang_thai='ThuongTru'
            )

            # 3. Tạo Con (Random 1-3 đứa)
            for j in range(random.randint(1, 3)):
                gioi_tinh_con = random.choice(['Nam', 'Nu'])
                nam_sinh = random.randint(2010, 2022) # Trẻ em để nhận quà
                ThanhVien.objects.create(
                    ho_gia_dinh=ho,
                    ho_ten=generate_name(gioi_tinh_con),
                    # Trẻ em có thể chưa có CCCD
                    cccd=f"001{nam_sinh}{random.randint(10000, 99999)}" if nam_sinh < 2010 else None,
                    ngay_sinh=date(nam_sinh, random.randint(1, 12), random.randint(1, 28)),
                    gioi_tinh=gioi_tinh_con,
                    quan_he_chu_ho='Con',
                    la_chu_ho=False,
                    trang_thai='ThuongTru'
                )

        print("🔄 Đang phát quà mẫu...")
        # Lấy tất cả trẻ em (sinh sau 2010)
        tre_em = ThanhVien.objects.filter(ngay_sinh__year__gte=2010)
        for chau in tre_em:
            if random.choice([True, False]): # 50% được nhận quà
                LichSuPhatThuong.objects.create(
                    thanh_vien=chau,
                    phan_thuong=pt2, # Tiền 50k
                    dot_phat="Trung Thu 2025",
                    trang_thai='DaNhan',
                    ghi_chu="Cháu ngoan"
                )

    print("\n✅ XONG! Đã tạo dữ liệu mẫu thành công.")
    print(f"👉 Tổng Hộ: {HoGiaDinh.objects.count()}")
    print(f"👉 Tổng Thành viên: {ThanhVien.objects.count()}")

# Chạy hàm
create_sample_data()
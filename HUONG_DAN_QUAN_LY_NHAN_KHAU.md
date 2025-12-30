# 📚 Hướng dẫn Quản lý Nhân khẩu và Hộ khẩu

## 🎯 Tổng quan

Hệ thống quản lý Tổ Dân Phố đã được bổ sung đầy đủ chức năng quản lý nhân khẩu và hộ khẩu theo yêu cầu nghiệp vụ.

## 👥 Chức năng cho Admin (Tổ trưởng)

### 1. Quản lý Nhân khẩu

#### ➕ Thêm nhân khẩu mới
- **URL:** `/admin/nhan-khau/them/`
- **Mô tả:** Thêm thành viên mới vào hệ thống
- **Thông tin cần nhập:**
  - **Thông tin cơ bản:** Hộ gia đình, họ tên, bí danh, CCCD, ngày sinh, giới tính
  - **Thông tin xuất xứ:** Nơi sinh, nguyên quán, dân tộc
  - **Thông tin nghề nghiệp:** Nghề nghiệp, nơi làm việc
  - **Thông tin CCCD:** Ngày cấp, nơi cấp
  - **Thông tin cư trú:** Ngày đăng ký thường trú, địa chỉ trước khi chuyển đến, trạng thái
  - **Vai trò trong hộ:** Là chủ hộ (checkbox), quan hệ với chủ hộ

#### ✏️ Sửa thông tin nhân khẩu
- **URL:** `/admin/nhan-khau/sua/<id>/`
- **Mô tả:** Cập nhật thông tin nhân khẩu đã có
- **Lưu ý:** Có cảnh báo về việc thay đổi ảnh hưởng đến sổ hộ khẩu

#### 🗑️ Xóa nhân khẩu
- **URL:** `/admin/nhan-khau/xoa/<id>/`
- **Mô tả:** Xóa nhân khẩu khỏi hệ thống
- **Lưu ý:** Có trang xác nhận với thông tin chi tiết trước khi xóa

#### 📊 Thống kê nhân khẩu
- **URL:** `/admin/nhan-khau/thong-ke/`
- **Mô tả:** Xem báo cáo thống kê chi tiết
- **Các loại thống kê:**
  - **Theo giới tính:** Nam, Nữ, Khác
  - **Theo trạng thái cư trú:** Thường trú, Tạm trú, Chuyển đi
  - **Theo độ tuổi:**
    - Mầm non (0-5 tuổi)
    - Mẫu giáo (6-7 tuổi)
    - Cấp 1 (8-10 tuổi)
    - Cấp 2 (11-14 tuổi)
    - Cấp 3 (15-17 tuổi)
    - Lao động (18-60 tuổi)
    - Nghỉ hưu (>60 tuổi)

### 2. Quản lý Hộ khẩu

#### 🏠 Thêm hộ khẩu mới
- **URL:** `/admin/ho-khau/them/`
- **Mô tả:** Tạo hộ gia đình mới
- **Thông tin cần nhập:** Mã hộ, địa chỉ

#### 🔀 Tách hộ
- **URL:** `/admin/ho-khau/tach/<ho_id>/`
- **Mô tả:** Tách một số thành viên từ hộ cũ sang hộ mới
- **Quy trình:**
  1. Xem thông tin hộ hiện tại
  2. Nhập thông tin hộ mới (mã hộ, địa chỉ)
  3. Chọn các thành viên muốn tách
  4. Xác nhận tách hộ
- **Ghi nhận:** Tự động ghi lịch sử thay đổi cho cả 2 hộ

### 3. API Endpoints cho Admin

#### API Tách hộ
```
POST /api/ho-gia-dinh/<id>/tach-ho/
```
**Request body:**
```json
{
  "ma_ho_moi": "HK123",
  "dia_chi_moi": "123 Đường ABC",
  "thanh_vien_ids": [1, 2, 3],
  "chu_ho_moi_id": 1
}
```

#### API Cập nhật trạng thái thành viên
```
POST /api/thanh-vien/<id>/cap-nhat-trang-thai/
```
**Request body:**
```json
{
  "trang_thai": "ChuyenDi",
  "ngay_chuyen_di": "2025-01-01",
  "noi_chuyen_den": "TP. HCM",
  "ghi_chu": "Chuyển công tác"
}
```

#### API Thống kê nhân khẩu
```
GET /api/thanh-vien/thong-ke/?loai=<loai_thong_ke>
```
**Các loại thống kê:**
- `loai=gioi_tinh` - Thống kê theo giới tính
- `loai=do_tuoi` - Thống kê theo độ tuổi
- `loai=thoi_gian&tu_ngay=2025-01-01&den_ngay=2025-12-31` - Theo thời gian
- `loai=tam_tru_vang` - Thống kê tạm trú/tạm vắng

#### API Xem lịch sử thay đổi
```
GET /api/thanh-vien/lich-su-thay-doi/?ho_gia_dinh_id=<id>
```

## 👨‍👩‍👧‍👦 Chức năng cho Người dân

### 1. Xem thông tin cá nhân
- **URL:** `/nhan-khau/`
- **Mô tả:** Xem thông tin nhân khẩu của bản thân
- **Hiển thị:**
  - Thông tin cơ bản (họ tên, CCCD, ngày sinh, giới tính)
  - Thông tin xuất xứ (nơi sinh, nguyên quán, dân tộc)
  - Thông tin nghề nghiệp
  - Thông tin CCCD
  - Thông tin cư trú
  - Vai trò trong hộ

### 2. Xem sổ hộ khẩu
- **URL:** `/ho-khau/`
- **Mô tả:** Xem sổ hộ khẩu của gia đình
- **Hiển thị:**
  - Thông tin hộ (mã hộ, địa chỉ, chủ hộ)
  - Danh sách tất cả thành viên trong hộ
  - Thông tin chi tiết từng thành viên

## 🔐 Phân quyền

### Admin (Tổ trưởng)
- ✅ Xem tất cả nhân khẩu, hộ khẩu
- ✅ Thêm/Sửa/Xóa nhân khẩu
- ✅ Thêm hộ khẩu mới
- ✅ Tách hộ
- ✅ Xem thống kê
- ✅ Xem lịch sử thay đổi

### Citizenship Manager (Quản lý công dân)
- ✅ Xem tất cả nhân khẩu, hộ khẩu
- ✅ Thêm/Sửa/Xóa nhân khẩu
- ✅ Thêm hộ khẩu mới
- ✅ Tách hộ
- ✅ Xem thống kê

### Citizen (Người dân)
- ✅ Xem thông tin cá nhân
- ✅ Xem sổ hộ khẩu của mình
- ❌ Không được sửa/xóa thông tin
- ❌ Không xem được thông tin của hộ khác

## 📊 Models và Dữ liệu

### HoGiaDinh (Hộ Gia Đình)
```python
- ma_ho: Mã hộ (unique)
- dia_chi: Địa chỉ
- chu_ho: Chủ hộ (OneToOne với ThanhVien)
```

### ThanhVien (Nhân Khẩu)
```python
# Thông tin cơ bản
- ho_ten, bi_danh, cccd, ngay_sinh, gioi_tinh
- noi_sinh, nguyen_quan, dan_toc

# Nghề nghiệp
- nghe_nghiep, noi_lam_viec

# CCCD
- ngay_cap_cccd, noi_cap_cccd

# Cư trú
- ngay_dang_ky_thuong_tru, dia_chi_truoc_chuyen_den
- trang_thai (ThuongTru/TamTru/ChuyenDi)

# Vai trò
- la_chu_ho (Boolean)
- quan_he_chu_ho

# Biến động
- ngay_chuyen_di, noi_chuyen_den, ghi_chu_thay_doi
```

### LichSuThayDoiHo
```python
- ho_gia_dinh: Hộ bị thay đổi
- loai_thay_doi: DoiChuHo/DoiDiaChi/TachHo/Khac
- noi_dung: Mô tả chi tiết
- ngay_thay_doi: Ngày thực hiện
- nguoi_thuc_hien: User thực hiện
```

## 🚀 Hướng dẫn sử dụng

### Để thêm nhân khẩu mới:
1. Đăng nhập với tài khoản admin
2. Vào menu "Nhân khẩu"
3. Click nút "➕ Thêm mới"
4. Điền đầy đủ thông tin
5. Click "✓ Thêm nhân khẩu"

### Để tách hộ:
1. Đăng nhập với tài khoản admin
2. Vào menu "Hộ khẩu"
3. Tìm hộ cần tách, click nút "🔀 Tách hộ"
4. Nhập thông tin hộ mới
5. Chọn các thành viên muốn tách
6. Click "✓ Xác nhận tách hộ"

### Để xem thống kê:
1. Đăng nhập với tài khoản admin
2. Vào menu "Nhân khẩu"
3. Click nút "📊 Thống kê"
4. Xem các biểu đồ và số liệu

## 🔧 Lưu ý kỹ thuật

### Validation
- CCCD phải duy nhất trong hệ thống
- Mã hộ phải duy nhất
- Một hộ chỉ có 1 chủ hộ
- Khi chuyển chủ hộ, tự động cập nhật quan hệ

### Transaction Safety
- Tách hộ sử dụng atomic transaction
- Đảm bảo tính nhất quán dữ liệu
- Tự động rollback nếu có lỗi

### Performance
- Sử dụng select_related để tối ưu query
- Prefetch_related cho danh sách thành viên
- Index trên CCCD và mã hộ

## 📝 Tài khoản demo

| Username | Password | Role | Quyền |
|----------|----------|------|-------|
| admin | admin123 | Admin | Full quyền |
| manager1 | manager123 | Quản lý công dân | Quản lý nhân khẩu |
| citizen | citizen123 | Dân cư | Xem thông tin cá nhân |

## 🆘 Xử lý lỗi thường gặp

### Lỗi: "CCCD đã tồn tại"
- Kiểm tra xem số CCCD đã được đăng ký chưa
- Nếu trùng, cần sửa số CCCD cũ hoặc nhập số khác

### Lỗi: "Mã hộ đã tồn tại"
- Chọn mã hộ khác khi tạo hộ mới
- Quy ước: HK001, HK002, ...

### Lỗi: "Không thể xóa chủ hộ"
- Cần chuyển chủ hộ sang người khác trước
- Hoặc xóa toàn bộ hộ

## 📞 Hỗ trợ

Nếu gặp vấn đề, vui lòng liên hệ quản trị viên hệ thống.

# Hệ thống Quản lý Tổ Dân Phố - Hướng dẫn chạy Demo

## 🚀 Chạy Demo nhanh (SQLite - Không cần MySQL)

### Bước 1: Tạo và kích hoạt Virtual Environment
```bash
# Tạo virtual environment
python -m venv .venv

# Kích hoạt venv (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Hoặc (Windows CMD)
.venv\Scripts\activate.bat
```

### Bước 2: Cài đặt Django
```bash
pip install django
```

### Bước 3: Tạo database và user demo
```bash
# Tạo database
python manage.py makemigrations
python manage.py migrate

# Tạo user demo
Get-Content create_demo_users.py | python manage.py shell
```

### Bước 4: Chạy server
```bash
python manage.py runserver
```

### Bước 5: Truy cập
Mở browser: **http://127.0.0.1:8000/**

---

## 👤 Tài khoản demo

| Loại | Username | Password | Dashboard hiển thị |
|------|----------|----------|-------------------|
| **Admin** | `admin` | `admin123` | "hú, bạn là tinh hoa, oách vl" 🌟 |
| **Quản lý công dân** | `manager1` | `manager123` | "hú, bạn là tinh hoa, oách vl" 🌟 |
| **Quản lý khen thưởng** | `manager2` | `manager123` | "hú, bạn là tinh hoa, oách vl" 🌟 |
| **Dân cư** | `citizen` | `citizen123` | "con gà máu bùn" 🐔 |

---

## 💡 Lưu ý

- **Virtual Environment**: Luôn kích hoạt venv trước khi chạy lệnh
- **Database hiện tại**: SQLite (file `db.sqlite3`) - Đơn giản, không cần cài gì
- **Cùng URL, khác nội dung**: Tất cả user truy cập `/users/dashboard/` nhưng thấy nội dung khác nhau theo role
- **4 loại user**: admin, citizenship_manager, commendation_manager, citizen

---

## 🔄 (Tùy chọn) Chuyển sang MySQL

Nếu muốn dùng MySQL production:

### 1. Cài MySQL/XAMPP và tạo database
```sql
CREATE DATABASE quanlytodanpho CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Cài thư viện MySQL (trong venv)
```bash
pip install mysqlclient
```

### 3. Sửa `quanlito_danpho/settings.py`
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'quanlytodanpho',
        'USER': 'root',
        'PASSWORD': '123456',  # Đổi password của bạn
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

### 4. Chạy lại migrations
```bash
python manage.py migrate
Get-Content create_demo_users.py | python manage.py shell
```

---

## 📁 Cấu trúc quan trọng

```
QuanLiToDanPho/
├── .venv/                  # Virtual environment (tự tạo)
├── apps/users/
│   ├── models.py           # UserProfile với 4 role
│   ├── views.py            # Login + Dashboard logic
│   └── urls.py
├── templates/users/
│   ├── login.html          # Trang đăng nhập
│   └── dashboard.html      # Dashboard phân quyền
├── db.sqlite3              # Database SQLite (tự tạo)
├── manage.py
└── create_demo_users.py    # Script tạo user demo
```

---

## ❓ Troubleshooting

### Lỗi "python không được nhận dạng"?
```bash
# Thay python bằng py
py -m venv .venv
py manage.py runserver
```

### Lỗi khi kích hoạt venv (PowerShell)?
```bash
# Nếu gặp lỗi ExecutionPolicy, chạy:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Sau đó kích hoạt lại
.venv\Scripts\Activate.ps1
```

### Server không chạy?
```bash
# Kiểm tra port 8000 có bị chiếm không
netstat -ano | findstr :8000

# Chạy port khác
python manage.py runserver 8080
```

### Quên mật khẩu demo?
```bash
# Chạy lại script tạo user
Get-Content create_demo_users.py | python manage.py shell
```

### Lỗi CSRF?
- Xóa cookies browser và thử lại
- Kiểm tra `{% csrf_token %}` có trong form login

---

## 🔐 Phân quyền

Hệ thống sử dụng role-based access control:

1. **admin**: Quản trị viên - Toàn quyền hệ thống
2. **citizenship_manager**: Quản lý công dân - Quản lý hộ khẩu, tạm trú/vắng
3. **commendation_manager**: Quản lý khen thưởng - Quản lý đề xuất & quyết định
4. **citizen**: Dân cư - Chỉ xem thông tin cá nhân

**Đặc điểm**: Cùng URL `/users/dashboard/` nhưng mỗi role thấy nội dung khác nhau!

---

## 🎯 Quick Start (TL;DR)

```bash
# 1. Tạo và kích hoạt venv
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Cài đặt
pip install django

# 3. Setup database và user
python manage.py makemigrations
python manage.py migrate
Get-Content create_demo_users.py | python manage.py shell

# 4. Chạy
python manage.py runserver

# 5. Truy cập http://127.0.0.1:8000/
# Login với: admin/admin123 hoặc citizen/citizen123
```
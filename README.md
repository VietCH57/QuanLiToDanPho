# QuanLiToDanPho
BTL môn Nhập môn Công nghệ phần mềm

## 🎯 Hệ thống quản lý Tổ Dân Phố

Ứng dụng web Django để quản lý:
- 📋 Hộ khẩu & Nhân khẩu
- 🏠 Tạm trú / Tạm vắng
- 🏆 Khen thưởng
- 👥 Phân quyền người dùng

---

## 🚀 Quick Start

### SQLite (Đơn giản - Demo nhanh)
```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt (muốn chạy nhanh nhẹ thì thêm "#" trước mysqlclient==2.2.7 và thêm pymysql vào cuối file requirements.txt)
python manage.py migrate
Get-Content create_demo_users.py | python manage.py shell
python manage.py runserver
```

### MySQL (Production)
Xem: [MYSQL_QUICKSTART.md](MYSQL_QUICKSTART.md)

---

## 📚 Tài liệu

- 📖 [SETUP_GUIDE.md](SETUP_GUIDE.md) - Hướng dẫn SQLite
- 🗄️ [HUONG_DAN_CAI_DAT_MYSQL.md](HUONG_DAN_CAI_DAT_MYSQL.md) - Hướng dẫn MySQL chi tiết
- ⚡ [MYSQL_QUICKSTART.md](MYSQL_QUICKSTART.md) - MySQL nhanh gọn
- 👥 [HUONG_DAN_QUAN_LY_NHAN_KHAU.md](HUONG_DAN_QUAN_LY_NHAN_KHAU.md) - **[MỚI]** Hướng dẫn quản lý Nhân khẩu & Hộ khẩu

---

## 🔐 Tài khoản demo

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Quản trị |
| manager1 | manager123 | Quản lý công dân |
| manager2 | manager123 | Quản lý khen thưởng |
| citizen | citizen123 | Dân cư |

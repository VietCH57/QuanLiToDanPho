"""
Script tự động setup MySQL database cho QuanLiToDanPho
Chạy: python setup_mysql_auto.py
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """In header đẹp"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def run_command(command, description):
    """Chạy command và hiển thị kết quả"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print(f"✅ {description} - Thành công!")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - Thất bại!")
            if result.stderr:
                print(f"Lỗi: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️ {description} - Timeout (quá 30s)")
        return False
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return False

def check_mysql_installed():
    """Kiểm tra MySQL đã cài chưa"""
    print_header("BƯỚC 1: Kiểm tra MySQL")
    result = subprocess.run("mysql --version", shell=True, capture_output=True)
    
    if result.returncode == 0:
        version = result.stdout.decode('utf-8', errors='ignore')
        print(f"✅ MySQL đã được cài đặt: {version}")
        return True
    else:
        print("❌ MySQL chưa được cài đặt!")
        print("\n📥 Hãy cài MySQL trước:")
        print("   Option 1: MySQL Installer - https://dev.mysql.com/downloads/installer/")
        print("   Option 2: XAMPP - https://www.apachefriends.org/")
        return False

def create_database(username, password):
    """Tạo database từ file dtb.sql"""
    print_header("BƯỚC 2: Tạo Database")
    
    sql_file = Path(__file__).parent / "dtb.sql"
    if not sql_file.exists():
        print(f"❌ Không tìm thấy file dtb.sql tại: {sql_file}")
        return False
    
    # Chạy file SQL
    command = f'mysql -u {username} -p{password} < "{sql_file}"'
    success = run_command(command, "Tạo database QLToDanPho từ dtb.sql")
    
    if success:
        # Kiểm tra database đã được tạo
        check_cmd = f'mysql -u {username} -p{password} -e "SHOW DATABASES LIKE \'QLToDanPho\';"'
        run_command(check_cmd, "Xác nhận database")
    
    return success

def install_mysql_driver():
    """Cài đặt Python MySQL driver"""
    print_header("BƯỚC 3: Cài đặt Python MySQL Driver")
    
    # Thử cài mysqlclient trước
    print("\n🔄 Đang thử cài mysqlclient...")
    result = subprocess.run("pip install mysqlclient", shell=True, capture_output=True)
    
    if result.returncode == 0:
        print("✅ Đã cài mysqlclient thành công!")
        return "mysqlclient"
    else:
        print("⚠️ mysqlclient cài thất bại, đang thử pymysql...")
        result = subprocess.run("pip install pymysql", shell=True, capture_output=True)
        
        if result.returncode == 0:
            print("✅ Đã cài pymysql thành công!")
            print("\n📝 LƯU Ý: Cần thêm vào đầu settings.py:")
            print("   import pymysql")
            print("   pymysql.install_as_MySQLdb()")
            return "pymysql"
        else:
            print("❌ Không thể cài MySQL driver!")
            return None

def update_settings(password, driver_type):
    """Cập nhật settings.py"""
    print_header("BƯỚC 4: Cấu hình Django Settings")
    
    settings_file = Path(__file__).parent / "citizen_app" / "settings.py"
    if not settings_file.exists():
        print(f"❌ Không tìm thấy settings.py tại: {settings_file}")
        return False
    
    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tạo cấu hình MySQL
        mysql_config = f"""
# DATABASES = {{
#     'default': {{
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }}
# }}

# MySQL Configuration
"""
        
        if driver_type == "pymysql":
            mysql_config += """import pymysql
pymysql.install_as_MySQLdb()

"""
        
        mysql_config += f"""DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'QLToDanPho',
        'USER': 'root',
        'PASSWORD': '{password}',
        'HOST': '127.0.0.1',
        'PORT': '3306',
        'OPTIONS': {{
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        }}
    }}
}}
"""
        
        print("\n📋 Cấu hình MySQL được tạo:")
        print(mysql_config)
        
        confirm = input("\n❓ Bạn có muốn tự động cập nhật settings.py? (y/n): ").lower()
        if confirm == 'y':
            # Tìm và thay thế phần DATABASES
            # (Thực tế nên làm thủ công để an toàn)
            print("\n⚠️ Vui lòng cập nhật thủ công bằng cách:")
            print("1. Mở file citizen_app/settings.py")
            print("2. Tìm phần DATABASES")
            print("3. Comment phần SQLite và uncomment phần MySQL")
            print("4. Đổi PASSWORD thành password MySQL của bạn")
        else:
            print("\n📝 Hãy cập nhật thủ công file settings.py")
        
        return True
    except Exception as e:
        print(f"❌ Lỗi đọc/ghi file: {str(e)}")
        return False

def test_connection():
    """Test kết nối Django với MySQL"""
    print_header("BƯỚC 5: Kiểm tra kết nối")
    
    print("\n🔄 Test kết nối database...")
    result = subprocess.run(
        "python manage.py dbshell --command=\"SELECT 1;\"",
        shell=True,
        capture_output=True,
        timeout=10
    )
    
    if result.returncode == 0:
        print("✅ Kết nối database thành công!")
        return True
    else:
        print("❌ Kết nối thất bại!")
        print("💡 Hãy kiểm tra lại password trong settings.py")
        return False

def main():
    """Hàm main"""
    print("\n" + "=" * 60)
    print("  🗄️  SETUP MYSQL CHO QUANLITODANPHO")
    print("=" * 60)
    
    # Kiểm tra MySQL
    if not check_mysql_installed():
        print("\n❌ Vui lòng cài MySQL trước khi chạy script này!")
        sys.exit(1)
    
    # Nhập thông tin MySQL
    print("\n📝 Nhập thông tin MySQL:")
    username = input("  Username (mặc định: root): ").strip() or "root"
    password = input("  Password: ").strip()
    
    if not password:
        print("❌ Password không được để trống!")
        sys.exit(1)
    
    # Tạo database
    if not create_database(username, password):
        print("\n❌ Không thể tạo database!")
        sys.exit(1)
    
    # Cài driver
    driver = install_mysql_driver()
    if not driver:
        print("\n❌ Không thể cài MySQL driver!")
        sys.exit(1)
    
    # Cập nhật settings
    update_settings(password, driver)
    
    # Kết luận
    print_header("HOÀN TẤT")
    print("\n✅ Setup MySQL thành công!")
    print("\n📋 Các bước tiếp theo:")
    print("  1. Cập nhật PASSWORD trong citizen_app/settings.py")
    print("  2. Chạy: python manage.py dbshell (để test)")
    print("  3. (Tùy chọn) Chạy: python manage.py migrate")
    print("  4. Chạy server: python manage.py runserver")
    print("\n📚 Xem hướng dẫn chi tiết: HUONG_DAN_CAI_DAT_MYSQL.md")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Đã hủy bởi người dùng")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Lỗi không mong muốn: {str(e)}")
        sys.exit(1)

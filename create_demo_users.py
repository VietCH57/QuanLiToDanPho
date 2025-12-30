"""
Script tạo user demo cho hệ thống
Chạy: python manage.py shell < create_demo_users.py
"""
from django.contrib.auth.models import User
from apps.users.models import UserProfile

# Xóa user cũ nếu có
User.objects.filter(username__in=['admin', 'manager1', 'manager2', 'citizen']).delete()

# Tạo Admin
admin = User.objects.create_user(username='admin', password='admin123', email='admin@example.com')
admin.is_staff = True
admin.is_superuser = True
admin.save()
# Refresh để lấy profile được tạo bởi signal
admin.refresh_from_db()
admin.profile.role = 'admin'
admin.profile.full_name = 'Nguyễn Văn Admin'
admin.profile.cccd_id = '001234567890'
admin.profile.working_unit_id = 'UNIT001'
admin.profile.save()
print('✅ Created admin: admin / admin123')

# Tạo Citizenship Manager
manager1 = User.objects.create_user(username='manager1', password='manager123', email='manager1@example.com')
manager1.profile.role = 'citizenship_manager'
manager1.profile.full_name = 'Trần Thị Quản Lý'
manager1.profile.cccd_id = '001234567891'
manager1.profile.working_unit_id = 'UNIT001'
manager1.profile.save()
print('✅ Created citizenship_manager: manager1 / manager123')

# Tạo Commendation Manager
manager2 = User.objects.create_user(username='manager2', password='manager123', email='manager2@example.com')
manager2.profile.role = 'commendation_manager'
manager2.profile.full_name = 'Lê Văn Khen Thưởng'
manager2.profile.cccd_id = '001234567892'
manager2.profile.working_unit_id = 'UNIT002'
manager2.profile.save()
print('✅ Created commendation_manager: manager2 / manager123')

# Tạo Citizen
citizen = User.objects.create_user(username='citizen', password='citizen123', email='citizen@example.com')
citizen.profile.role = 'citizen'
citizen.profile.full_name = 'Phạm Thị Dân'
citizen.profile.cccd_id = '001234567893'
citizen.profile.save()
print('✅ Created citizen: citizen / citizen123')

print('\n🎉 Tất cả user demo đã được tạo!')
print('\n📝 Thông tin đăng nhập:')
print('   Admin: admin / admin123')
print('   Quản lý công dân: manager1 / manager123')
print('   Quản lý khen thưởng: manager2 / manager123')
print('   Dân cư: citizen / citizen123')

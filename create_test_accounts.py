from django.contrib.auth import get_user_model
from apps.users.models import UserProfile

User = get_user_model()

def create_test_users():
    users = [
        {"username": "manager1", "password": "manager123", "role": "citizenship_manager", "full_name": "Quản lý công dân"},
        {"username": "manager2", "password": "manager123", "role": "commendation_manager", "full_name": "Quản lý khen thưởng"},
        {"username": "citizen", "password": "citizen123", "role": "citizen", "full_name": "Dân cư"},
    ]
    for u in users:
        if not User.objects.filter(username=u["username"]).exists():
            user = User.objects.create_user(username=u["username"], password=u["password"])
            UserProfile.objects.update_or_create(user=user, defaults={"role": u["role"], "full_name": u["full_name"]})
            print(f"Created {u['username']} ({u['role']})")
        else:
            print(f"User {u['username']} already exists.")

if __name__ == "__main__":
    create_test_users()

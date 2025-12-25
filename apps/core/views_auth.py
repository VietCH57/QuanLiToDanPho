from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated

# ==========================================================
#  MODULE XÁC THỰC (AUTHENTICATION)
#  Bao gồm: Đăng ký, Đăng nhập, Đăng xuất, Đổi mật khẩu
# ==========================================================

class RegisterView(APIView):
    """
    API Đăng ký tài khoản cho người dân.
    - Public Access (Ai cũng gọi được).
    - Tự động tạo Profile 'NGUOI_DAN' nhờ Signal (xem apps/core/signals.py).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email', '')

        # 1. Validate dữ liệu đầu vào
        if not username or not password:
            return Response({'error': 'Vui lòng điền đầy đủ Tên đăng nhập và Mật khẩu'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 6:
            return Response({'error': 'Mật khẩu phải có ít nhất 6 ký tự'}, status=status.HTTP_400_BAD_REQUEST)

        # 2. Kiểm tra trùng lặp
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Tên tài khoản này đã được sử dụng'}, status=status.HTTP_400_BAD_REQUEST)

        # 3. Tạo User
        try:
            # Signal 'post_save' trong signals.py sẽ tự động chạy để tạo UserProfile role='NGUOI_DAN'
            user = User.objects.create_user(username=username, password=password, email=email)
            return Response({
                'message': 'Đăng ký thành công! Bạn có thể đăng nhập ngay.',
                'username': user.username
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': f'Lỗi hệ thống: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    """
    API Đăng nhập.
    - Trả về thông tin User + Role để Frontend điều hướng.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        # Xác thực
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({"detail": "Sai tài khoản hoặc mật khẩu"}, status=status.HTTP_401_UNAUTHORIZED)

        # Login session
        login(request, user)
        
        # Lấy Role an toàn
        role = 'Unknown'
        if hasattr(user, 'profile'):
            role = user.profile.role

        return Response({
            "message": "Đăng nhập thành công",
            "username": user.username,
            "role": role,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
        })


class LogoutView(APIView):
    """API Đăng xuất"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Đã đăng xuất thành công"})


class UserProfileView(APIView):
    """API lấy thông tin bản thân (Me)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = getattr(user, 'profile', None).role if hasattr(user, 'profile') else None
        
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": role,
            "is_staff": user.is_staff,
            "date_joined": user.date_joined
        })


class ChangePasswordView(APIView):
    """
    API Đổi mật khẩu (ND-04).
    Yêu cầu: Mật khẩu cũ và Mật khẩu mới.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error": "Mật khẩu cũ không chính xác"}, status=status.HTTP_400_BAD_REQUEST)

        if len(new_password) < 6:
             return Response({'error': 'Mật khẩu mới quá ngắn (tối thiểu 6 ký tự)'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        
        # Quan trọng: Khi đổi pass xong, session cũ vẫn giữ để user không bị văng ra
        login(request, user) 

        return Response({"message": "Đổi mật khẩu thành công"})
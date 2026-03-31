from rest_framework import generics, status, permissions as drf_permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from django.contrib.auth import get_user_model
from .models import User, Role, Permission, UserRole, RolePermission
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer,
    RoleSerializer,
    PermissionSerializer,
    UserRoleSerializer,
    RolePermissionSerializer,
)
from .permissions import IsAdmin, IsSuperAdmin, HasPermission, IsManager

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status.HTTP_201_CREATED,
        )


class LoginView(APIView):

    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        if not user.is_active:
            return Response(
                {"error": "Account is deactivated"}, status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class DeactivateUserView(APIView):

    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user

        if not user.is_active:
            return Response(
                {"error": "Пользователь уже деактивирован"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            user.is_active = False
            user.save()

            return Response(
                {
                    "status": "success",
                    "message": "Пользователь успешно деактивирован",
                    "user_id": user.id,
                    "email": user.email,
                    "is_active": user.is_active,
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"error": f"Ошибка при деактивации: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class UserListView(generics.ListAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = User.objects.all()

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == "true")

        role = self.request.query_params.get("role")
        if role:
            queryset = queryset.filter(roles__role__name=role)

        return queryset


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return User.objects.all()

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()

        if user == request.user:
            return Response(
                {"error": "Нельзя удалить свой аккаунт"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = False
        user.save()

        return Response(
            {"message": f"Пользователь {user.email} деактивирован"},
            status=status.HTTP_200_OK,
        )


class RoleListView(generics.ListCreateAPIView):

    serializer_class = RoleSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return Role.objects.all()


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = RoleSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return Role.objects.all()

    def destroy(self, request, *args, **kwargs):
        role = self.get_object()

        if role.name in ["super_admin", "admin", "manager", "user"]:
            return Response(
                {"error": f"Нельзя удалить системную роль {role.get_name_display()}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().destroy(request, *args, **kwargs)


class PermissionListView(generics.ListCreateAPIView):

    serializer_class = PermissionSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        queryset = Permission.objects.all()

        resource_type = self.request.query_params.get("resource_type")
        if resource_type:
            queryset = queryset.filter(resource_type=resource_type)

        action = self.request.query_params.get("action")
        if action:
            queryset = queryset.filter(action=action)

        return queryset


class PermissionDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = PermissionSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return Permission.objects.all()


class UserRoleListView(generics.ListCreateAPIView):

    serializer_class = UserRoleSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        user_id = self.request.query_params.get("user_id")
        if user_id:
            return UserRole.objects.filter(user_id=user_id)
        return UserRole.objects.all()

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)


class UserRoleDetailView(generics.DestroyAPIView):

    serializer_class = UserRoleSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return UserRole.objects.all()


class RolePermissionListView(generics.ListCreateAPIView):

    serializer_class = RolePermissionSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        role_id = self.request.query_params.get("role_id")
        if role_id:
            return RolePermission.objects.filter(role_id=role_id)
        return RolePermission.objects.all()

    def perform_create(self, serializer):
        serializer.save(granted_by=self.request.user)


class RolePermissionDetailView(generics.DestroyAPIView):

    serializer_class = RolePermissionSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        return RolePermission.objects.all()


class UserPermissionsView(APIView):

    permission_classes = [drf_permissions.IsAuthenticated]

    def get(self, request):
        user = request.user

        roles = UserRole.objects.filter(user=user).select_related("role")

        permissions = []
        for user_role in roles:
            role_perms = RolePermission.objects.filter(
                role=user_role.role
            ).select_related("permission")

            for rp in role_perms:
                permissions.append(
                    {
                        "id": rp.permission.id,
                        "name": rp.permission.name,
                        "resource_type": rp.permission.resource_type,
                        "action": rp.permission.action,
                        "codename": rp.permission.codename,
                    }
                )

        unique_perms = {p["codename"]: p for p in permissions}.values()

        return Response(
            {
                "user_id": user.id,
                "email": user.email,
                "roles": [
                    {"id": ur.role.id, "name": ur.role.get_name_display()}
                    for ur in roles
                ],
                "permissions": list(unique_perms),
                "is_superuser": user.is_superuser,
            }
        )


# MOCK-View


class CanReadContent(BasePermission):

    def has_permission(self, request, view):
        permission = HasPermission("content", "read")
        return permission.has_permission(request, view)


class CanCreateContent(BasePermission):

    def has_permission(self, request, view):
        permission = HasPermission("content", "create")
        return permission.has_permission(request, view)


class CanUpdateContent(BasePermission):

    def has_permission(self, request, view):
        permission = HasPermission("content", "update")
        return permission.has_permission(request, view)


class CanDeleteContent(BasePermission):

    def has_permission(self, request, view):
        permission = HasPermission("content", "delete")
        return permission.has_permission(request, view)


class MockContentListView(APIView):

    MOCK_CONTENT = [
        {
            "id": 1,
            "title": "Введение в Django",
            "content": "Django - это высокоуровневый веб-фреймворк...",
            "author": "admin@example.com",
            "created_at": "2026-03-01T10:00:00Z",
            "status": "published",
        },
        {
            "id": 2,
            "title": "REST API с Django REST Framework",
            "content": "DRF позволяет быстро создавать API...",
            "author": "manager@example.com",
            "created_at": "2026-03-05T14:30:00Z",
            "status": "published",
        },
        {
            "id": 3,
            "title": "JWT аутентификация",
            "content": "JSON Web Tokens для безопасной аутентификации...",
            "author": "admin@example.com",
            "created_at": "2026-03-10T09:15:00Z",
            "status": "draft",
        },
        {
            "id": 4,
            "title": "Система прав доступа RBAC",
            "content": "Role-Based Access Control для управления правами...",
            "author": "super_admin@example.com",
            "created_at": "2026-03-15T16:45:00Z",
            "status": "published",
        },
    ]

    def get_permissions(self):

        if self.request.method == "GET":
            return [IsAuthenticated(), CanReadContent()]
        elif self.request.method == "POST":
            return [IsAuthenticated(), CanCreateContent()]
        return super().get_permissions()

    def get(self, request):

        status_filter = request.query_params.get("status")
        if status_filter:
            filtered = [c for c in self.MOCK_CONTENT if c["status"] == status_filter]
            return Response({"count": len(filtered), "results": filtered})

        return Response({"count": len(self.MOCK_CONTENT), "results": self.MOCK_CONTENT})

    def post(self, request):

        data = request.data
        new_content = {
            "id": len(self.MOCK_CONTENT) + 1,
            "title": data.get("title", "Untitled"),
            "content": data.get("content", ""),
            "author": request.user.email,
            "created_at": "2026-03-30T12:00:00Z",
            "status": data.get("status", "draft"),
        }

        self.MOCK_CONTENT.append(new_content)

        return Response(new_content, status=status.HTTP_201_CREATED)


class MockContentDetailView(APIView):

    MOCK_CONTENT = MockContentListView.MOCK_CONTENT

    def get_permissions(self):

        if self.request.method == "GET":
            return [IsAuthenticated(), CanReadContent()]
        elif self.request.method == "PUT":
            return [IsAuthenticated(), CanUpdateContent()]
        elif self.request.method == "DELETE":
            return [IsAuthenticated(), CanDeleteContent()]
        return super().get_permissions()

    def get_object(self, content_id):

        for item in self.MOCK_CONTENT:
            if item["id"] == content_id:
                return item
        return None

    def get(self, content_id):

        content = self.get_object(content_id)
        if not content:
            return Response(
                {"error": "Контент не найден"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(content)

    def put(self, request, content_id):

        content = self.get_object(content_id)
        if not content:
            return Response(
                {"error": "Контент не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        content.update(request.data)
        content["updated_at"] = "2026-03-30T12:00:00Z"

        return Response(content)

    def delete(self, content_id):

        content = self.get_object(content_id)
        if not content:
            return Response(
                {"error": "Контент не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        self.MOCK_CONTENT.remove(content)

        return Response(
            {"message": f'Контент "{content["title"]}" удален'},
            status=status.HTTP_204_NO_CONTENT,
        )


class MockReportView(APIView):

    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        report_type = request.query_params.get("type", "summary")

        reports = {
            "summary": {
                "total_users": 4,
                "active_users": 4,
                "total_content": 4,
                "published_content": 3,
                "draft_content": 1,
                "roles_distribution": {
                    "super_admin": 1,
                    "admin": 1,
                    "manager": 1,
                    "user": 1,
                },
            },
            "user_activity": {
                "data": [
                    {"date": "2026-03-01", "registrations": 1, "logins": 5},
                    {"date": "2026-03-02", "registrations": 0, "logins": 8},
                    {"date": "2026-03-03", "registrations": 1, "logins": 12},
                    {"date": "2026-03-04", "registrations": 0, "logins": 7},
                    {"date": "2026-03-05", "registrations": 1, "logins": 15},
                ]
            },
            "content_stats": {
                "by_status": {"published": 3, "draft": 1, "archived": 0},
                "by_author": {
                    "admin@example.com": 2,
                    "manager@example.com": 1,
                    "super_admin@example.com": 1,
                },
            },
        }

        if report_type in reports:
            return Response(reports[report_type])

        return Response(
            {"error": f'Тип отчета "{report_type}" не найден'},
            status=status.HTTP_404_NOT_FOUND,
        )


class MockSettingsView(APIView):

    permission_classes = [IsAuthenticated, IsAdmin]

    MOCK_SETTINGS = {
        "site_name": "Auth API Service",
        "site_description": "Сервис аутентификации и авторизации",
        "version": "2.0.0",
        "maintenance_mode": False,
        "allow_registration": True,
        "max_login_attempts": 5,
        "session_timeout_minutes": 60,
        "email_verification_required": False,
        "theme": "dark",
        "notifications_enabled": True,
    }

    def get(self):
        return Response(self.MOCK_SETTINGS)

    def put(self, request):
        if not request.user.is_superuser:
            return Response(
                {"error": "Только супер-администратор может изменять настройки"},
                status=status.HTTP_403_FORBIDDEN,
            )

        self.MOCK_SETTINGS.update(request.data)

        return Response(
            {"message": "Настройки обновлены", "settings": self.MOCK_SETTINGS}
        )


class MockErrorTestView(APIView):

    permission_classes = []

    def get(self, request):
        error_type = request.query_params.get("type", "")

        errors = {
            "401": Response(
                {"error": "Требуется аутентификация", "code": "unauthorized"},
                status=status.HTTP_401_UNAUTHORIZED,
            ),
            "403": Response(
                {"error": "Доступ запрещен", "code": "forbidden"},
                status=status.HTTP_403_FORBIDDEN,
            ),
            "404": Response(
                {"error": "Ресурс не найден", "code": "not_found"},
                status=status.HTTP_404_NOT_FOUND,
            ),
            "400": Response(
                {"error": "Неверный запрос", "code": "bad_request"},
                status=status.HTTP_400_BAD_REQUEST,
            ),
            "500": Response(
                {"error": "Внутренняя ошибка сервера", "code": "internal_error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ),
            "validation": Response(
                {
                    "error": "Ошибка валидации",
                    "errors": {
                        "email": ["Введите корректный email"],
                        "password": ["Пароль должен содержать минимум 8 символов"],
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            ),
            "rate_limit": Response(
                {"error": "Превышен лимит запросов", "code": "rate_limit_exceeded"},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            ),
        }

        if error_type in errors:
            return errors[error_type]

        return Response(
            {
                "available_errors": list(errors.keys()),
                "usage": "/api/auth/mock/error/?type=401",
            }
        )


class MockPermissionTestView(APIView):

    def get_permissions(self):
        level = self.request.query_params.get("level", "user")

        if level == "admin":
            self.permission_classes = [IsAuthenticated, IsAdmin]
        elif level == "super_admin":
            self.permission_classes = [IsAuthenticated, IsSuperAdmin]
        elif level == "manager":
            self.permission_classes = [IsAuthenticated, IsManager]
        else:
            self.permission_classes = [IsAuthenticated]

        return super().get_permissions()

    def get(self, request):
        level = request.query_params.get("level", "user")

        return Response(
            {
                "message": f"Доступ разрешен для уровня: {level}",
                "user": {
                    "email": request.user.email,
                    "is_superuser": request.user.is_superuser,
                    "is_staff": request.user.is_staff,
                },
                "required_level": level,
            }
        )

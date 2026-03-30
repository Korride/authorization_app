from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    DeactivateUserView,

    UserListView,
    UserDetailView,
    RoleListView,
    RoleDetailView,

    PermissionListView,
    PermissionDetailView,
    UserRoleListView,
    UserRoleDetailView,
    RolePermissionListView,
    RolePermissionDetailView,
    UserPermissionsView,
    MockContentListView,
    MockContentDetailView,
    MockReportView,
    MockSettingsView,
    MockErrorTestView,
    MockPermissionTestView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('deactivate/', DeactivateUserView.as_view(), name='deactivate'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('admin/users/', UserListView.as_view(), name='user_list'),
    path('admin/users/<int:pk>/', UserDetailView.as_view(), name='user_detail'),

    path('admin/roles/', RoleListView.as_view(), name='role_list'),
    path('admin/roles/<int:pk>/', RoleDetailView.as_view(), name='role_detail'),

    path('admin/permissions/', PermissionListView.as_view(), name='permission_list'),
    path('admin/permissions/<int:pk>/', PermissionDetailView.as_view(), name='permission_detail'),

    path('admin/user-roles/', UserRoleListView.as_view(), name='user_role_list'),
    path('admin/user-roles/<int:pk>/', UserRoleDetailView.as_view(), name='user_role_detail'),

    path('admin/role-permissions/', RolePermissionListView.as_view(), name='role_permission_list'),
    path('admin/role-permissions/<int:pk>/', RolePermissionDetailView.as_view(), name='role_permission_detail'),

    path('my-permissions/', UserPermissionsView.as_view(), name='my_permissions'),

    path('mock/content/', MockContentListView.as_view(), name='mock_content_list'),
    path('mock/content/<int:content_id>/', MockContentDetailView.as_view(), name='mock_content_detail'),

    path('mock/reports/', MockReportView.as_view(), name='mock_reports'),

    path('mock/settings/', MockSettingsView.as_view(), name='mock_settings'),

    path('mock/error/', MockErrorTestView.as_view(), name='mock_error'),

    path('mock/permission-test/', MockPermissionTestView.as_view(), name='mock_permission_test'),
]

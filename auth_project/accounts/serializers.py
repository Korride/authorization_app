from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from .models import User, Role, Permission, UserRole, RolePermission

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'second_name',
            'email',
            'created_at')
        read_only_fields = ('id', 'created_at', 'updated_at')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'second_name',
            'password',
            'password2')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким именем уже существует")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Пользователь с таким email уже существует")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError('Passwords must match.')
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)

            if not user:
                raise serializers.ValidationError('Invalid credentials.')

            if not user.is_active:
                raise serializers.ValidationError('User has been deactivated.')

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Invalid credentials.')


class RoleSerializer(serializers.ModelSerializer):

    name_display = serializers.CharField(
        source='get_name_display', read_only=True)
    permissions_count = serializers.SerializerMethodField()

    class Meta:
        model = Role
        fields = (
            'id',
            'name',
            'name_display',
            'description',
            'permissions_count',
            'created_at',
            'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_permissions_count(self, obj):
        return obj.permissions.count()


class PermissionSerializer(serializers.ModelSerializer):

    resource_type_display = serializers.CharField(
        source='get_resource_type_display', read_only=True)
    action_display = serializers.CharField(
        source='get_action_display', read_only=True)
    full_codename = serializers.CharField(read_only=True)

    class Meta:
        model = Permission
        fields = (
            'id',
            'name',
            'codename',
            'resource_type',
            'resource_type_display',
            'action',
            'action_display',
            'full_codename',
            'description',
            'created_at')
        read_only_fields = ('id', 'created_at')


class UserRoleSerializer(serializers.ModelSerializer):

    user_email = serializers.EmailField(source='user.email', read_only=True)
    role_name = serializers.CharField(
        source='role.get_name_display', read_only=True)
    assigned_by_email = serializers.EmailField(
        source='assigned_by.email', read_only=True)

    class Meta:
        model = UserRole
        fields = ('id', 'user', 'user_email', 'role', 'role_name',
                  'assigned_at', 'assigned_by', 'assigned_by_email')
        read_only_fields = ('id', 'assigned_at', 'assigned_by')

    def validate(self, attrs):
        user = attrs.get('user')
        role = attrs.get('role')

        if UserRole.objects.filter(user=user, role=role).exists():
            raise serializers.ValidationError(
                'Роль уже назначена этому пользователю')

        return attrs


class RolePermissionSerializer(serializers.ModelSerializer):

    role_name = serializers.CharField(
        source='role.get_name_display', read_only=True)
    permission_name = serializers.CharField(
        source='permission.name', read_only=True)
    granted_by_email = serializers.EmailField(
        source='granted_by.email', read_only=True)

    class Meta:
        model = RolePermission
        fields = ('id', 'role', 'role_name', 'permission', 'permission_name',
                  'granted_at', 'granted_by', 'granted_by_email')
        read_only_fields = ('id', 'granted_at', 'granted_by')

    def validate(self, attrs):
        role = attrs.get('role')
        permission = attrs.get('permission')

        if RolePermission.objects.filter(
                role=role, permission=permission).exists():
            raise serializers.ValidationError(
                'Разрешение уже назначено этой роли')

        return attrs

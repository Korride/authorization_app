from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    email = models.EmailField(unique=True, verbose_name="Email адрес")
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    second_name = models.CharField(
        max_length=150, blank=True, null=True, verbose_name="Отчество"
    )
    phone = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="Телефон"
    )
    date_of_birth = models.DateField(
        blank=True, null=True, verbose_name="Дата рождения"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации"
    )
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email

    def get_full_name(self):
        parts = []
        if self.last_name:
            parts.append(self.last_name)
        if self.first_name:
            parts.append(self.first_name)
        if self.second_name:
            parts.append(self.second_name)
        return " ".join(parts) if parts else self.email


class Role(models.Model):

    ROLE_CHOICES = [
        ("super_admin", "Super Admin"),
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("user", "User"),
    ]

    name = models.CharField(
        max_length=50, unique=True, choices=ROLE_CHOICES, verbose_name="Название"
    )
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "roles"
        verbose_name = "Роль"
        verbose_name_plural = "Роли"
        ordering = ["name"]

    def __str__(self):
        return self.get_name_display()


class Permission(models.Model):

    RESOURCE_TYPES = [
        ("user", "User"),
        ("role", "Role"),
        ("permission", "Permission"),
        ("profile", "Profile"),
        ("content", "Content"),
        ("system", "System"),
    ]

    ACTIONS = [
        ("create", "Create"),
        ("read", "Read"),
        ("update", "Update"),
        ("delete", "Delete"),
        ("manage", "Manage"),
    ]

    name = models.CharField(max_length=100, verbose_name="Название")
    codename = models.CharField(max_length=100, unique=True, verbose_name="Кодовое имя")
    resource_type = models.CharField(
        max_length=50, choices=RESOURCE_TYPES, verbose_name="Тип ресурса"
    )
    action = models.CharField(max_length=20, choices=ACTIONS, verbose_name="Действие")
    description = models.TextField(blank=True, verbose_name="Описание")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "permissions"
        verbose_name = "Разрешение"
        verbose_name_plural = "Разрешения"
        unique_together = ["resource_type", "action"]

    def __str__(self):
        return f"{self.get_resource_type_display()} - {self.get_action_display()}"

    @property
    def full_codename(self):
        return f"{self.resource_type}.{self.action}"


class UserRole(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="users")
    assigned_at = models.DateTimeField(auto_now_add=True)
    assigned_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="assigned_roles"
    )

    class Meta:
        db_table = "user_roles"
        verbose_name = "Роль пользователя"
        verbose_name_plural = "Роли пользователей"
        unique_together = ["user", "role"]

    def __str__(self):
        return f"{self.user.email} - {self.role.get_name_display()}"


class RolePermission(models.Model):

    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    permission = models.ForeignKey(
        Permission, on_delete=models.CASCADE, related_name="roles"
    )
    granted_at = models.DateTimeField(auto_now_add=True)
    granted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "role_permissions"
        verbose_name = "Разрешение роли"
        verbose_name_plural = "Разрешения ролей"
        unique_together = ["role", "permission"]

    def __str__(self):
        return f"{self.role.get_name_display()} - {self.permission}"

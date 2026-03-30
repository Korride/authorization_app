from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Role, Permission, UserRole, RolePermission

User = get_user_model()


class Command(BaseCommand):
    help = 'Инициализация ролей и разрешений тестовыми данными'

    def handle(self, *args, **options):
        self.stdout.write('Инициализация системы прав доступа...')

        roles_data = [
            ('super_admin', 'Супер-администратор - полный доступ ко всему'),
            ('admin', 'Администратор - управление пользователями и контентом'),
            ('manager', 'Менеджер - управление контентом, просмотр отчетов'),
            ('user', 'Пользователь - базовый доступ'),
        ]

        roles = {}
        for name, desc in roles_data:
            role, created = Role.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )
            roles[name] = role
            self.stdout.write(
                f'  {
                    "Создана" if created else "Существует"} роль: {name}')

        permissions_data = [
            ('profile', 'read', 'Просмотр своего профиля'),
            ('profile', 'update', 'Редактирование своего профиля'),
            ('profile', 'read_any', 'Просмотр любых профилей'),
            ('profile', 'update_any', 'Редактирование любых профилей'),

            ('user', 'read', 'Просмотр списка пользователей'),
            ('user', 'create', 'Создание пользователей'),
            ('user', 'update', 'Редактирование пользователей'),
            ('user', 'delete', 'Удаление пользователей'),
            ('user', 'deactivate', 'Деактивация пользователей'),

            ('role', 'read', 'Просмотр ролей'),
            ('role', 'create', 'Создание ролей'),
            ('role', 'update', 'Редактирование ролей'),
            ('role', 'delete', 'Удаление ролей'),
            ('role', 'assign', 'Назначение ролей пользователям'),

            ('permission', 'read', 'Просмотр разрешений'),
            ('permission', 'create', 'Создание разрешений'),
            ('permission', 'update', 'Редактирование разрешений'),
            ('permission', 'delete', 'Удаление разрешений'),
            ('permission', 'assign', 'Назначение разрешений ролям'),

            ('content', 'read', 'Просмотр контента'),
            ('content', 'create', 'Создание контента'),
            ('content', 'update', 'Редактирование контента'),
            ('content', 'delete', 'Удаление контента'),

            ('system', 'read', 'Просмотр системных настроек'),
            ('system', 'update', 'Изменение системных настроек'),
        ]

        permissions = {}
        for resource, action, desc in permissions_data:
            codename = f"{resource}.{action}"
            perm, created = Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    'name': f"{resource} - {action}",
                    'resource_type': resource,
                    'action': action,
                    'description': desc
                }
            )
            permissions[codename] = perm
            self.stdout.write(
                f'  {
                    "Создано" if created else "Существует"} разрешение: {codename}')

        for perm in permissions.values():
            RolePermission.objects.get_or_create(
                role=roles['super_admin'],
                permission=perm
            )
        self.stdout.write('  Назначены все разрешения роли super_admin')

        admin_perms = [
            'profile.read_any', 'profile.update_any',
            'user.read', 'user.create', 'user.update', 'user.deactivate',
            'role.read', 'role.assign',
            'permission.read',
            'content.read', 'content.create', 'content.update',
            'system.read',
        ]
        for codename in admin_perms:
            if codename in permissions:
                RolePermission.objects.get_or_create(
                    role=roles['admin'],
                    permission=permissions[codename]
                )
        self.stdout.write('  Назначены разрешения роли admin')

        manager_perms = [
            'profile.read_any',
            'user.read',
            'content.read', 'content.create', 'content.update',
        ]
        for codename in manager_perms:
            if codename in permissions:
                RolePermission.objects.get_or_create(
                    role=roles['manager'],
                    permission=permissions[codename]
                )
        self.stdout.write('  Назначены разрешения роли manager')

        user_perms = [
            'profile.read', 'profile.update',
            'content.read',
        ]
        for codename in user_perms:
            if codename in permissions:
                RolePermission.objects.get_or_create(
                    role=roles['user'],
                    permission=permissions[codename]
                )
        self.stdout.write('  Назначены разрешения роли user')

        test_users = [
            ('super_admin@example.com', 'superadmin123', 'Super', 'Admin', 'super_admin'),
            ('admin@example.com', 'admin123', 'Admin', 'User', 'admin'),
            ('manager@example.com', 'manager123', 'Manager', 'User', 'manager'),
            ('user@example.com', 'user123', 'Regular', 'User', 'user'),
        ]

        for email, password, first_name, last_name, role_name in test_users:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email.split('@')[0],
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True
                }
            )

            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(
                    f'  Создан пользователь: {email} (пароль: {password})')

            UserRole.objects.get_or_create(
                user=user,
                role=roles[role_name],
                defaults={'assigned_by': user if user.is_superuser else None}
            )

        self.stdout.write(self.style.SUCCESS(
            'Инициализация завершена успешно!'))

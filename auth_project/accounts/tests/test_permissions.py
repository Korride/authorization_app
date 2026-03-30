# accounts/tests/test_permissions.py

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from accounts.models import Role, UserRole, Permission, RolePermission

User = get_user_model()


class PermissionTests(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.create_roles()

        self.super_admin = User.objects.create_superuser(
            email='super@test.com',
            password='test123',
            first_name='Super',
            last_name='Admin'
        )

        self.admin = User.objects.create_user(
            email='admin@test.com',
            password='test123',
            first_name='Admin',
            last_name='User'
        )

        self.manager = User.objects.create_user(
            email='manager@test.com',
            password='test123',
            first_name='Manager',
            last_name='User'
        )

        self.user = User.objects.create_user(
            email='user@test.com',
            password='test123',
            first_name='Regular',
            last_name='User'
        )

        admin_role = Role.objects.get(name='admin')
        manager_role = Role.objects.get(name='manager')
        user_role = Role.objects.get(name='user')

        UserRole.objects.get_or_create(user=self.admin, role=admin_role)
        UserRole.objects.get_or_create(user=self.manager, role=manager_role)
        UserRole.objects.get_or_create(user=self.user, role=user_role)

        self.create_permissions()

    def create_roles(self):

        roles = [
            ('super_admin', 'Супер-администратор'),
            ('admin', 'Администратор'),
            ('manager', 'Менеджер'),
            ('user', 'Пользователь'),
        ]

        for name, desc in roles:
            Role.objects.get_or_create(
                name=name,
                defaults={'description': desc}
            )

    def create_permissions(self):

        permissions = [
            ('content.read', 'content', 'read', 'Чтение контента'),
            ('content.create', 'content', 'create', 'Создание контента'),
            ('content.update', 'content', 'update', 'Обновление контента'),
            ('content.delete', 'content', 'delete', 'Удаление контента'),
        ]

        for codename, resource, action, desc in permissions:
            Permission.objects.get_or_create(
                codename=codename,
                defaults={
                    'name': f'{resource} - {action}',
                    'resource_type': resource,
                    'action': action,
                    'description': desc
                }
            )

        admin_role = Role.objects.get(name='admin')
        manager_role = Role.objects.get(name='manager')
        user_role = Role.objects.get(name='user')

        for perm in Permission.objects.filter(resource_type='content'):
            RolePermission.objects.get_or_create(
                role=admin_role, permission=perm)

        for action in ['read', 'create', 'update']:
            try:
                perm = Permission.objects.get(codename=f'content.{action}')
                RolePermission.objects.get_or_create(
                    role=manager_role, permission=perm)
            except Permission.DoesNotExist:
                pass

        try:
            perm = Permission.objects.get(codename='content.read')
            RolePermission.objects.get_or_create(
                role=user_role, permission=perm)
        except Permission.DoesNotExist:
            pass

    def test_content_list_access_unauthenticated(self):

        url = reverse('mock_content_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_content_list_access_user(self):

        url = reverse('mock_content_list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.json())

    def test_content_create_access_user(self):

        url = reverse('mock_content_list')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            url, {'title': 'Test Content'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_content_create_access_manager(self):

        url = reverse('mock_content_list')
        self.client.force_authenticate(user=self.manager)
        response = self.client.post(
            url, {'title': 'Test Content'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

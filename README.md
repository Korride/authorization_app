# API Аутентификации с RBAC

## Система разграничения прав доступа

### Иерархия ролей

| Роль | Описание | Права |
|------|----------|-------|
| **Super Admin** | Полный доступ ко всему | Все разрешения |
| **Admin** | Управление пользователями | Просмотр/редактирование пользователей, назначение ролей |
| **Manager** | Управление контентом | CRUD контента, просмотр пользователей |
| **User** | Базовый доступ | Управление своим профилем, просмотр контента |

### Матрица доступа

| Ресурс | Действие | User | Manager | Admin | Super Admin |
|--------|----------|------|---------|-------|-------------|
| Свой профиль | CRUD | ✅ | ✅ | ✅ | ✅ |
| Чужой профиль | Просмотр | ❌ | ✅ | ✅ | ✅ |
| Чужой профиль | Редактирование | ❌ | ❌ | ✅ | ✅ |
| Пользователи | CRUD | ❌ | ❌ | ✅ | ✅ |
| Роли | Просмотр | ❌ | ❌ | ✅ | ✅ |
| Роли | CRUD | ❌ | ❌ | ❌ | ✅ |
| Разрешения | Управление | ❌ | ❌ | ❌ | ✅ |
| Контент | CRUD | ❌ | ✅ | ✅ | ✅ |

### API Эндпоинты

#### Аутентификация
- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/login/` - Вход
- `POST /api/auth/logout/` - Выход
- `GET /api/auth/profile/` - Профиль
- `GET /api/auth/my-permissions/` - Мои права

#### Управление пользователями (Admin+)
- `GET /api/auth/admin/users/` - Список пользователей
- `GET /api/auth/admin/users/<id>/` - Детали пользователя
- `PUT /api/auth/admin/users/<id>/` - Редактирование
- `DELETE /api/auth/admin/users/<id>/` - Деактивация

#### Управление ролями (Super Admin)
- `GET /api/auth/admin/roles/` - Список ролей
- `POST /api/auth/admin/roles/` - Создание роли
- `GET /api/auth/admin/roles/<id>/` - Детали роли
- `PUT /api/auth/admin/roles/<id>/` - Редактирование
- `DELETE /api/auth/admin/roles/<id>/` - Удаление

#### Назначение ролей (Admin+)
- `GET /api/auth/admin/user-roles/` - Список назначений
- `POST /api/auth/admin/user-roles/` - Назначить роль
- `DELETE /api/auth/admin/user-roles/<id>/` - Удалить назначение

### Тестовые учетные записи

| Роль | Email | Пароль |
|------|-------|--------|
| Super Admin | super_admin@example.com | superadmin123 |
| Admin | admin@example.com | admin123 |
| Manager | manager@example.com | manager123 |
| User | user@example.com | user123 |


## Mock-Views для тестирования

### Контент (требует content.* прав)
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/auth/mock/content/` | Список контента |
| POST | `/api/auth/mock/content/` | Создание контента |
| GET | `/api/auth/mock/content/{id}/` | Детали контента |
| PUT | `/api/auth/mock/content/{id}/` | Обновление контента |
| DELETE | `/api/auth/mock/content/{id}/` | Удаление контента |

### Отчеты (требует роль manager+)
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/auth/mock/reports/` | Получение отчетов |

**Параметры:** `?type=summary|user_activity|content_stats`

### Настройки (требует роль admin+)
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/auth/mock/settings/` | Просмотр настроек |
| PUT | `/api/auth/mock/settings/` | Изменение настроек (super_admin) |

### Тестирование ошибок
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/auth/mock/error/?type=401` | 401 Unauthorized |
| GET | `/api/auth/mock/error/?type=403` | 403 Forbidden |
| GET | `/api/auth/mock/error/?type=404` | 404 Not Found |
| GET | `/api/auth/mock/error/?type=400` | 400 Bad Request |
| GET | `/api/auth/mock/error/?type=500` | 500 Internal Error |
| GET | `/api/auth/mock/error/?type=validation` | Ошибка валидации |
| GET | `/api/auth/mock/error/?type=rate_limit` | Rate Limit |

### Тестирование прав доступа
| Метод | URL | Описание |
|-------|-----|----------|
| GET | `/api/auth/mock/permission-test/?level=user` | Тест прав user |
| GET | `/api/auth/mock/permission-test/?level=manager` | Тест прав manager |
| GET | `/api/auth/mock/permission-test/?level=admin` | Тест прав admin |
| GET | `/api/auth/mock/permission-test/?level=super_admin` | Тест прав super_admin |

### Инициализация

```bash
# Применить миграции
python manage.py migrate

# Заполнить тестовыми данными
python manage.py init_permissions

# Создать суперпользователя (если нужно)
python manage.py createsuperuser

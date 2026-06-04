# Handmade Marketplace Backend

Backend API для учебного pet-проекта маркетплейса товаров ручной работы.

Проект разработан на Django и Django REST Framework. Основная цель проекта — отработать backend-разработку на практике: проектирование моделей, работу с ролями пользователей, JWT-аутентификацию, права доступа, бизнес-логику заказов, PostgreSQL и автоматические API-тесты.

## Стек технологий

* Python
* Django
* Django REST Framework
* PostgreSQL
* Simple JWT
* Django Admin
* django-environ
* unittest / DRF APITestCase

## Основные возможности

* Регистрация пользователей.
* Роли пользователей:

  * buyer;
  * seller;
  * admin.
* JWT-аутентификация.
* Просмотр категорий.
* Просмотр списка товаров.
* Просмотр одного товара.
* Создание товара продавцом.
* Редактирование и удаление товара только владельцем или администратором.
* Создание заказа покупателем.
* Автоматический расчёт итоговой стоимости заказа.
* Автоматическое уменьшение количества товара после заказа.
* Автоматическое скрытие товара, если его количество стало равно нулю.
* Просмотр пользователем только своих заказов.
* Просмотр всех заказов администратором.
* Автоматические тесты API.

## Архитектура проекта

Основная логика приложения находится в приложении `marketplace`.

```text
marketplace/
├── admin.py
├── apps.py
├── models.py
├── permissions.py
├── serializers.py
├── services.py
├── urls.py
├── views.py
└── tests/
    ├── test_auth_api.py
    ├── test_products_api.py
    └── test_orders_api.py
```

### Основные слои

* `models.py` — описание структуры данных.
* `serializers.py` — преобразование данных в JSON и валидация входных данных.
* `permissions.py` — проверка прав доступа.
* `views.py` — обработка HTTP-запросов.
* `services.py` — бизнес-логика создания заказа.
* `tests/` — автоматические API-тесты.

## Модели

### UserProfile

Расширяет стандартную модель пользователя Django через связь один к одному.

Поля:

* `user`
* `role`

Доступные роли:

* `buyer`
* `seller`
* `admin`

### Category

Категория товара.

Поля:

* `name`
* `description`

### Product

Товар маркетплейса.

Поля:

* `title`
* `description`
* `price`
* `quantity`
* `image`
* `category`
* `seller`
* `created_at`
* `updated_at`
* `is_available`

### Order

Заказ пользователя.

Поля:

* `buyer`
* `product`
* `quantity`
* `total_price`
* `status`
* `created_at`

## Права доступа

| Действие                     | Аноним | Buyer | Seller | Admin |
| ---------------------------- | -----: | ----: | -----: | ----: |
| Просмотр категорий           |     Да |    Да |     Да |    Да |
| Просмотр товаров             |     Да |    Да |     Да |    Да |
| Создание товара              |    Нет |   Нет |     Да |    Да |
| Редактирование своего товара |    Нет |   Нет |     Да |    Да |
| Редактирование чужого товара |    Нет |   Нет |    Нет |    Да |
| Создание заказа              |    Нет |    Да |    Нет |   Нет |
| Просмотр своих заказов       |    Нет |    Да |     Да |    Да |
| Просмотр всех заказов        |    Нет |   Нет |    Нет |    Да |

## API endpoints

Базовый префикс API:

```text
/api/v1/
```

### Auth

```text
POST /api/v1/auth/register/
POST /api/v1/auth/token/
POST /api/v1/auth/token/refresh/
```

### Categories

```text
GET /api/v1/categories/
GET /api/v1/categories/{id}/
```

### Products

```text
GET    /api/v1/products/
POST   /api/v1/products/
GET    /api/v1/products/{id}/
PUT    /api/v1/products/{id}/
PATCH  /api/v1/products/{id}/
DELETE /api/v1/products/{id}/
```

### Orders

```text
GET  /api/v1/orders/
POST /api/v1/orders/
GET  /api/v1/orders/{id}/
```

## Переменные окружения

Проект использует `.env` для локальных настроек.

Пример находится в файле:

```text
.env.example
```

Пример содержимого:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DATABASE_URL=postgres://your_db_user:your_db_password@localhost:5432/your_db_name
```

Файл `.env` не должен попадать в Git.

## Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone <repository-url>
cd marketplace
```

### 2. Создать виртуальное окружение

```bash
python -m venv .venv
```

### 3. Активировать виртуальное окружение

Для Windows PowerShell:

```powershell
.\.venv\Scripts\activate
```

### 4. Установить зависимости

```bash
pip install -r requirements.txt
```

### 5. Создать `.env`

Создать файл `.env` в корне проекта и заполнить его по примеру `.env.example`.

### 6. Применить миграции

```bash
python manage.py migrate
```

### 7. Создать суперпользователя

```bash
python manage.py createsuperuser
```

### 8. Запустить сервер

```bash
python manage.py runserver
```

После запуска API будет доступно по адресу:

```text
http://127.0.0.1:8000/api/v1/
```

Админ-панель:

```text
http://127.0.0.1:8000/admin/
```

## Запуск тестов

```bash
python manage.py test
```

На текущем этапе проект содержит тесты для:

* регистрации пользователей;
* проверки ролей;
* создания товаров;
* проверки прав доступа к товарам;
* создания заказов;
* расчёта итоговой стоимости;
* уменьшения количества товара;
* ограничения доступа к чужим заказам;
* доступа администратора ко всем заказам.

## Примеры API-запросов

### Регистрация продавца

```json
{
  "username": "seller1",
  "email": "seller1@example.com",
  "password": "strongpass123",
  "role": "seller"
}
```

### Получение JWT-токена

```json
{
  "username": "seller1",
  "password": "strongpass123"
}
```

### Создание товара

```json
{
  "title": "Ceramic mug",
  "description": "Handmade white clay mug.",
  "price": "1200.00",
  "quantity": 5,
  "category": 1
}
```

### Создание заказа

```json
{
  "product": 1,
  "quantity": 2
}
```

## Особенности реализации

Бизнес-логика создания заказа вынесена в сервисный слой `services.py`.

При создании заказа backend:

1. Проверяет количество товара.
2. Проверяет доступность товара.
3. Блокирует товар на уровне базы данных через `select_for_update()`.
4. Рассчитывает `total_price`.
5. Создаёт заказ.
6. Уменьшает `quantity` товара.
7. Делает товар недоступным, если количество стало равно нулю.

Такой подход отделяет бизнес-логику от HTTP-слоя и делает код проще для тестирования и поддержки.

## Статус проекта

Проект находится в стадии активной разработки как учебный backend pet-project.

Планируемые улучшения:

* добавить фильтрацию и поиск товаров;
* добавить пагинацию;
* добавить документацию API через Swagger / drf-spectacular;
* улучшить README примерами curl-запросов;
* добавить Docker и docker-compose;
* добавить CI для запуска тестов.

# Сервис бронирования переговорных комнат

REST API на FastAPI для управления бронированием переговорных комнат в коворкинге.

## Стек технологий

- **Python 3.11+**, **FastAPI**, **SQLAlchemy 2.0** (async)
- **PostgreSQL** (через asyncpg), **JWT** аутентификация
- **Poetry** для управления зависимостями, **pytest** для тестов
- **Docker** + **docker-compose**

---

## Быстрый запуск через Docker Compose (рекомендуется)

```bash
# Клонировать репозиторий
git clone <repo-url> && cd booking-service

# Запустить сервис + базу данных
docker-compose up --build

# Сервис доступен на http://localhost:8000
# Swagger UI:          http://localhost:8000/docs
```

При первом запуске автоматически создаются таблицы и тестовые данные:

| Пользователь | Пароль   | Роль       |
|-------------|----------|------------|
| `admin`     | `admin123` | Администратор |
| `employee1` | `pass123`  | Сотрудник  |
| `employee2` | `pass123`  | Сотрудник  |

---

## Запуск только приложения через Docker (без docker-compose)

```bash
docker build -t booking-service .

docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@host:5432/dbname" \
  -e SECRET_KEY="your-secret-key" \
  booking-service
```

---

## Локальный запуск

### Требования
- Python 3.11+
- Poetry (`pip install poetry`)
- PostgreSQL (локально или через Docker)

```bash
# Установить зависимости
poetry install

# Создать .env из шаблона и настроить DATABASE_URL
cp .env.example .env

# Запустить только PostgreSQL
docker run -d --name pg -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=booking_db -p 5432:5432 postgres:16-alpine

# Запустить сервер
poetry run uvicorn app.main:app --reload --port 8000
```

---

## Запуск тестов

```bash
# Установить dev-зависимости (уже включены в poetry install)
poetry install

# Все тесты
poetry run pytest -v

# С отчётом покрытия
poetry run pytest --cov=app --cov-report=term-missing
```

Тесты используют SQLite in-memory и не требуют PostgreSQL.

---

## API Endpoints

### Аутентификация

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/v1/auth/register` | Регистрация нового пользователя |
| `POST` | `/api/v1/auth/login` | Получение JWT-токена |

### Комнаты *(требует авторизации)*

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/api/v1/rooms` | Список всех переговорных |
| `GET` | `/api/v1/rooms/{id}` | Информация о комнате |
| `GET` | `/api/v1/rooms/{id}/availability?date=YYYY-MM-DD` | Свободные/занятые слоты на дату |

### Бронирования *(требует авторизации)*

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| `POST` | `/api/v1/bookings` | Создать бронирование | Все пользователи |
| `GET` | `/api/v1/bookings/my` | Мои бронирования | Все пользователи |
| `GET` | `/api/v1/bookings` | Все бронирования | Только администратор |
| `DELETE` | `/api/v1/bookings/{id}` | Отменить бронирование | Своё — все; чужое — только admin |

---

## Примеры запросов

### 1. Получить токен

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "employee1", "password": "pass123"}'
```

```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

### 2. Посмотреть доступность комнаты на дату

```bash
curl http://localhost:8000/api/v1/rooms/1/availability?date=2025-12-15 \
  -H "Authorization: Bearer eyJ..."
```

```json
{
  "date": "2025-12-15",
  "room": {"id": 1, "name": "Переговорная «Альфа»", ...},
  "available_slots": [
    {"id": 1, "label": "09:00–11:00", "start_time": "09:00:00", "end_time": "11:00:00"},
    ...
  ],
  "booked_slots": []
}
```

### 3. Создать бронирование

```bash
curl -X POST http://localhost:8000/api/v1/bookings \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "time_slot_id": 1, "date": "2025-12-15"}'
```

```json
{
  "id": 1,
  "room_id": 1,
  "time_slot_id": 1,
  "date": "2025-12-15",
  "status": "active",
  "user_id": 2,
  "created_at": "2025-12-14T10:00:00"
}
```

### 4. Отменить бронирование

```bash
curl -X DELETE http://localhost:8000/api/v1/bookings/1 \
  -H "Authorization: Bearer eyJ..."
```

### 5. Список всех бронирований (администратор)

```bash
curl http://localhost:8000/api/v1/bookings \
  -H "Authorization: Bearer <admin-token>"
```

---

## Интерактивная документация

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

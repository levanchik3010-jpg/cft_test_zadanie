# Сервис бронирования переговорных комнат

Сервис для бронирования переговорных комнат в коворкинге. Сотрудники могут смотреть доступность комнат и создавать бронирования, администраторы управлять всеми бронированиями.

## Как запустить

### Через Docker Compose

Нужен только Docker.

```bash
git clone <ссылка на репозиторий>
cd cft_test_zadanie
docker-compose up --build
```

Сервис поднимется на http://localhost:8000 вместе с базой данных.

---

### Через docker run

Сначала запустить базу данных:

```bash
docker run -d --name booking-db ^
  -e POSTGRES_USER=postgres ^
  -e POSTGRES_PASSWORD=postgres ^
  -e POSTGRES_DB=booking_db ^
  -p 5432:5432 ^
  postgres:16-alpine
```

Затем собрать и запустить приложение:

```bash
docker build -t booking-service .

docker run -d --name booking-app ^
  -e DATABASE_URL=postgresql+psycopg://postgres:postgres@host.docker.internal:5432/booking_db ^
  -e SECRET_KEY=super-secret-key ^
  -e ACCESS_TOKEN_EXPIRE_MINUTES=30 ^
  -p 8000:8000 ^
  booking-service
```

Сервис поднимется на http://localhost:8000

---

### Локально

```bash
poetry install

cp .env.example .env

poetry run uvicorn app.main:app --reload --port 8000
```

---

### Тесты

```bash
poetry run pytest -v
```

---

## Тестовые пользователи

При первом запуске автоматически создаются:

| Логин | Пароль | Роль |
|-------|--------|------|
| admin | admin123 | Администратор |
| employee1 | pass123 | Сотрудник |
| employee2 | pass123 | Сотрудник |

---

## API

### Авторизация

| Метод | Путь | Описание |
|-------|------|----------|
| POST | /api/v1/auth/register | Регистрация |
| POST | /api/v1/auth/login | Получить JWT токен |

### Комнаты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | /api/v1/rooms | Список комнат |
| GET | /api/v1/rooms/{id} | Информация о комнате |
| GET | /api/v1/rooms/{id}/availability?date=YYYY-MM-DD | Свободные слоты на дату |

### Бронирования

| Метод | Путь | Описание | Доступ |
|-------|------|----------|--------|
| POST | /api/v1/bookings | Создать бронирование | Все |
| GET | /api/v1/bookings/my | Мои бронирования | Все |
| GET | /api/v1/bookings | Все бронирования | Только admin |
| DELETE | /api/v1/bookings/{id} | Отменить бронирование | Своё — все, чужое — только admin |

---

## Примеры

**Зарегистрировать пользователя:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register   -H "Content-Type: application/json"   -d '{"username": "ivan", "password": "pass123", "full_name": "Иван Иванов", "role": "employee"}'
```
```json
{"id": 4, "username": "ivan", "full_name": "Иван Иванов", "role": "employee"}
```

**Получить токен:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login   -H "Content-Type: application/json"   -d '{"username": "employee1", "password": "pass123"}'
```
```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

**Список всех комнат:**
```bash
curl http://localhost:8000/api/v1/rooms   -H "Authorization: Bearer eyJ..."
```
```json
[
  {"id": 1, "name": "Переговорная А", "capacity": 6, "time_slots": [...]},
  {"id": 2, "name": "Переговорная Б", "capacity": 10, "time_slots": [...]}
]
```

**Информация об одной комнате:**
```bash
curl http://localhost:8000/api/v1/rooms/1   -H "Authorization: Bearer eyJ..."
```
```json
{"id": 1, "name": "Переговорная А", "capacity": 6, "time_slots": [...]}
```

**Свободные слоты на дату:**
```bash
curl "http://localhost:8000/api/v1/rooms/1/availability?date=2026-12-20"   -H "Authorization: Bearer eyJ..."
```
```json
{
  "date": "2026-12-20",
  "available_slots": [{"id": 1, "label": "09:00-11:00"}, ...],
  "booked_slots": []
}
```

**Забронировать комнату:**
```bash
curl -X POST http://localhost:8000/api/v1/bookings   -H "Authorization: Bearer eyJ..."   -H "Content-Type: application/json"   -d '{"room_id": 1, "time_slot_id": 1, "date": "2026-12-20"}'
```
```json
{"id": 1, "status": "active", "date": "2026-12-20", "room_id": 1, "time_slot_id": 1, "user_id": 2}
```

**Мои бронирования:**
```bash
curl http://localhost:8000/api/v1/bookings/my   -H "Authorization: Bearer eyJ..."
```
```json
[{"id": 1, "status": "active", "date": "2026-12-20", "room_id": 1, "time_slot_id": 1, "user_id": 2}]
```

**Все бронирования (только админ):**
```bash
curl http://localhost:8000/api/v1/bookings   -H "Authorization: Bearer eyJ..."
```
```json
[
  {"id": 1, "status": "active", "date": "2026-12-20", "user": {...}, "room": {...}, "time_slot": {...}}
]
```

**Отменить бронирование:**
```bash
curl -X DELETE http://localhost:8000/api/v1/bookings/1   -H "Authorization: Bearer eyJ..."
```
```json
{"id": 1, "status": "cancelled", "date": "2026-12-20", "room_id": 1, "time_slot_id": 1, "user_id": 2}
```

---

Документация API доступна по адресу http://localhost:8000/docs

# Сервис бронирования переговорных комнат

Сервис для бронирования переговорных комнат в коворкинге. Сотрудники могут смотреть доступность комнат и создавать бронирования, администраторы — управлять всеми бронированиями.

## Технологии

- Python 3.11, FastAPI
- PostgreSQL + SQLAlchemy (async)
- JWT авторизация
- Poetry, Docker

---

## Как запустить

### Через Docker Compose (самый простой способ)

Нужен только Docker.

```bash
git clone <ссылка на репозиторий>
cd cft_test_zadanie
docker-compose up --build
```

Сервис поднимется на http://localhost:8000 вместе с базой данных.

---

### Локально

Нужен Python 3.11+, Poetry и PostgreSQL.

```bash
# Устанавливаем зависимости
poetry install

# Копируем .env и прописываем подключение к базе
cp .env.example .env

# Запускаем
poetry run uvicorn app.main:app --reload --port 8000
```

---

### Тесты

```bash
poetry run pytest -v
```

Тесты работают на SQLite, PostgreSQL не нужен.

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

**Получить токен:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "employee1", "password": "pass123"}'
```
```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

**Посмотреть свободные слоты:**
```bash
curl http://localhost:8000/api/v1/rooms/1/availability?date=2025-12-20 \
  -H "Authorization: Bearer eyJ..."
```
```json
{
  "date": "2025-12-20",
  "available_slots": [{"id": 1, "label": "09:00–11:00"}, ...],
  "booked_slots": []
}
```

**Забронировать комнату:**
```bash
curl -X POST http://localhost:8000/api/v1/bookings \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "time_slot_id": 1, "date": "2025-12-20"}'
```
```json
{"id": 1, "status": "active", "date": "2025-12-20", ...}
```

**Отменить бронирование:**
```bash
curl -X DELETE http://localhost:8000/api/v1/bookings/1 \
  -H "Authorization: Bearer eyJ..."
```

---

Swagger UI доступен по адресу http://localhost:8000/docs

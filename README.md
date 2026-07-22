# ChatApp — Мессенджер в реальном времени

Веб-приложение для обмена сообщениями с поддержкой групповых и личных чатов, отложенной отправки и индикации набора текста.

## Технологии

**Бэкенд:**
- Python / FastAPI
- PostgreSQL (через SQLAlchemy + asyncpg)
- Redis
- WebSocket для обмена сообщениями в реальном времени
- JWT-аутентификация

**Фронтенд:**
- Vanilla JavaScript, HTML, CSS
- Адаптивный интерфейс с тёмной и светлой темами

**Инфраструктура:**
- Docker Compose
- Nginx ( reverse proxy для фронтенда )

## Возможности

- Регистрация и авторизация пользователей
- Личные (прямые) сообщения между пользователями
- Групповые чаты (публичные и приватные)
- Создание и управление группами (добавление / удаление участников)
- Отправка сообщений в реальном времени через WebSocket
- Индикация набора текста ("печатает...")
- Отложенная отправка сообщений (планировщик с фоновой задачей)
- Редактирование и удаление сообщений с историей изменений
- Поиск по группам и пользователям
- Настройка оформления: тёмная / светлая тема, выбор акцентного цвета
- Адаптивный дизайн (мобильные и десктопные устройства)

## Структура проекта

```
Chat_app/
├── backend/
│   ├── main.py              # Точка входа FastAPI, lifespan, фоновый планировщик
│   ├── database.py          # Настройка подключения к PostgreSQL (async)
│   ├── settings/
│   │   └── settings.py      # Конфигурация (Pydantic Settings)
│   ├── models/
│   │   ├── user.py          # Модель пользователя
│   │   ├── groups.py        # Модели группы и участника
│   │   └── messages.py      # Модели сообщений, непрочитанных, истории изменений
│   ├── schemas/             # Pydantic-схемы запросов и ответов
│   ├── routers/
│   │   ├── auth.py          # Эндпоинты: регистрация, вход, текущий пользователь
│   │   ├── users.py         # Эндпоинты: список пользователей
│   │   ├── messages.py      # Эндпоинты: отправка, получение, редактирование, удаление, планирование
│   │   ├── groups.py        # Эндпоинты: CRUD групп, управление участниками
│   │   └── websocket.py     # WebSocket-эндпоинт для real-time обмена
│   ├── services/            # Бизнес-логика
│   ├── utils/               # Утилиты (менеджер соединений, безопасность, исключения)
│   ├── requirements.txt     # Зависимости Python
│   └── Dockerfile
├── frontend/
│   ├── index.html           # Главная страница приложения
│   ├── app.js               # Клиентская логика (авторизация, чат, WebSocket)
│   ├── style.css            # Стили (тёмная/светлая тема, адаптивность)
│   ├── nginx.conf           # Конфигурация Nginx
│   └── Dockerfile
├── docker-compose.yml       # Оркестрация: PostgreSQL, Redis, Backend, Frontend
├── .env                     # Переменные окружения (не коммитить)
└── .env.docker              # Переменные окружения для Docker
```

## Запуск

### Через Docker Compose (рекомендуется)

1. Убедитесь, что Docker и Docker Compose установлены.

2. Создайте файл `.env.docker` в корне проекта:

```env
SECRET_KEY=your-secret-key-min-32-characters-long
DATABASE_URL=postgresql+asyncpg://postgres:pass@postgres:5432/chat_db
REDIS_URL=redis://redis:6379
DEBUG=false
```

3. Запустите:

```bash
docker compose up --build
```

4. Приложение будет доступно:
- **Фронтенд:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API документация:** http://localhost:8000/docs

### Локальная разработка

1. Запустите PostgreSQL и Redis (например через Docker):

```bash
docker compose up -d postgres redis
```

2. Установите зависимости бэкенда:

```bash
cd backend
pip install -r requirements.txt
```

3. Создайте файл `.env` в корне проекта:

```env
SECRET_KEY=your-secret-key-min-32-characters-long
DATABASE_URL=postgresql+asyncpg://postgres:pass@localhost:5432/chat_db
REDIS_URL=redis://localhost:6379
DEBUG=true
```

4. Запустите бэкенд:

```bash
uvicorn backend.main:app --reload --port 8000
```

5. Откройте `frontend/index.html` в браузере или запустите любой локальный сервер на порту 3000.

## API Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/auth/register` | Регистрация пользователя |
| `POST` | `/api/auth/login` | Вход (возвращает JWT) |
| `GET` | `/api/auth/me` | Текущий пользователь |
| `GET` | `/api/users/` | Список пользователей |
| `POST` | `/api/messages/` | Отправить сообщение |
| `POST` | `/api/messages/schedule` | Отложить сообщение |
| `GET` | `/api/messages/group/{id}` | Сообщения группы |
| `GET` | `/api/messages/direct/{id}` | Личные сообщения |
| `PATCH` | `/api/messages/{id}` | Редактировать сообщение |
| `DELETE` | `/api/messages/{id}` | Удалить сообщение |
| `DELETE` | `/api/messages/scheduled/{id}` | Отменить отложенное |
| `POST` | `/api/groups/` | Создать группу |
| `GET` | `/api/groups/` | Мои группы |
| `GET` | `/api/groups/{id}` | Информация о группе |
| `GET` | `/api/groups/{id}/members` | Участники группы |
| `POST` | `/api/groups/{id}/members/{user_id}` | Добавить участника |
| `DELETE` | `/api/groups/{id}/members/{user_id}` | Удалить участника |
| `PATCH` | `/api/groups/{id}` | Обновить группу |
| `DELETE` | `/api/groups/{id}` | Удалить группу |

## WebSocket

Подключение: `ws://localhost:8000/ws/{jwt_token}`

Типы сообщений:
- `group_message` — отправка в группу
- `direct_message` — личное сообщение
- `typing` — индикация набора текста
- `read` — уведомление о прочтении

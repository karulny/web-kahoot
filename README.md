# web-kahoot (Проект для ЯЛа)
![Static Badge](https://img.shields.io/badge/python_3.14-project-green?logo=python)
![Static Badge](https://img.shields.io/badge/flask-project-aqua?logo=flask)
![Static Badge](https://img.shields.io/badge/github-repo-grey?logo=github)


## Архитектура:
```plain
backend/
├── app/
│   ├── db/
│   │   └── session.py    # Тут лежит db = SQLAlchemy()
│   ├── models.py         # Тут лежат классы (User и т.д.)
│   ├── handlers/         # Blueprint`ы
│   ├── middlwares/       # Проверяет авторизацию, но только пока что, служебная прослойка
│   └── services/         # бизнес-логика
└── main.py               # Точка запуска
└── frontend/           # красота
    ├── .html/
    ├── css/
    └── js/            
```

# КВИЗСТРОЙ

Веб-платформа для проведения интерактивных квизов в реальном времени — аналог Kahoot, без установки приложений.

## Быстрый старт

```bash
cp .env.example .env
docker compose up --build
```

Приложение доступно на `http://localhost:8080` (или порт из `.env`).

## Переменные окружения

| Переменная | По умолчанию | Описание |
|---|---|---|
| `POSTGRES_PASSWORD` | `1111` | Пароль PostgreSQL |
| `SECRET_KEY` | `dev-secret-key` | Ключ подписи JWT — **сменить в проде** |
| `FLASK_ENV` | `production` | Режим Flask |
| `PORT` | `80` | Порт на хосте |

## Стек

- **Backend** — Python 3.12, Flask, SQLAlchemy, Gunicorn
- **БД** — PostgreSQL 16
- **Инфраструктура** — Docker, Docker Compose, Nginx

## Хранение данных

Все данные хранятся в PostgreSQL. Docker volume `postgres_data` монтируется в `/var/lib/postgresql/data` — данные переживают перезапуск контейнеров.

**Медиафайлы** в текущей версии не загружаются на сервер — квизы принимают только `media_url` (внешняя ссылка на изображение). Загрузка файлов на сервер не реализована.

**Экспорт результатов** — файл `.xlsx` генерируется в памяти через `openpyxl` и отдаётся напрямую без сохранения на диск.

**QR-коды** — генерируются на лету, base64-строка возвращается в JSON, на диск не пишутся.

## API

| Метод | URL | Доступ | Описание |
|---|---|---|---|
| `POST` | `/auth/register` | — | Регистрация |
| `POST` | `/auth/login` | — | Вход, возвращает JWT |
| `GET` | `/quiz/` | Автор | Список своих квизов |
| `POST` | `/quiz/` | Автор | Создать квиз |
| `PUT` | `/quiz/<id>` | Автор | Обновить квиз |
| `DELETE` | `/quiz/<id>` | Автор | Удалить квиз |
| `POST` | `/game/start/<quiz_id>` | Автор | Создать игровую сессию |
| `POST` | `/game/join` | Участник | Войти по PIN |
| `GET` | `/game/status/<pin>` | Все | Polling: состояние игры |
| `POST` | `/game/next/<session_id>` | Автор | Следующий вопрос |
| `POST` | `/game/answer` | Участник | Отправить ответ |
| `GET` | `/game/leaderboard/<session_id>` | Все | Таблица лидеров |
| `GET` | `/game/export/<session_id>` | Автор | Скачать результаты `.xlsx` |
| `GET` | `/game/qr/<pin>` | Автор | QR-код для входа |

Защищённые маршруты требуют заголовок `Authorization: Bearer <token>`.

## Архитектура

```
Nginx → Gunicorn (Flask)
          ├── handlers/   — маршруты (Blueprint)
          ├── services/   — бизнес-логика
          ├── models.py   — User, Quiz, Question, AnswerOption
          └── models_game.py — GameSession, SessionParticipant, ParticipantAnswer
```

Клиент делает `GET /game/status/<pin>` каждые 2 секунды (polling) — без WebSocket.
## Как работает Polling
Каждые 2 секунды клиент (и ведущий и участник) делает GET /game/status/{pin}. Сервер возвращает полное состояние: статус (waiting/active/finished), текущий вопрос, количество участников. Клиент смотрит на статус и рендерит нужный экран.
#### By *@karulny*

# web-kahoot (Проект для ЯЛа)
![Static Badge](https://img.shields.io/badge/python_3.14-project-green?logo=python)
![Static Badge](https://img.shields.io/badge/flask-project-aqua?logo=flask)
![Static Badge](https://img.shields.io/badge/github-repo-grey?logo=github)


## Архитектура (на данный моеент) 04.04:
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

## Что есть и реализованно (backend)

- **Авторизация, Регистрация, Идентификация** ```auth.py, session.py```
- **БД (разметка)** - ```models.py```
- ```main.py```
## Roadmap (backend):

- ~~**Альфа-версия без фронта, только бэк (endpoint для 11 апреля):**~~
- ~~**Логика добавления и создания квизов**~~
- ~~**Возможность ответить на квиз.**~~
- Устранение ограничений бета-версии

## Ограничения бета:
- **Нет загрузки медиафайлов (только URL в поле media_url)**
- **Нет QR-кода (можно добавить библиотеку qrcode)**
- **PIN копируется в буфер, QR — заглушка**
- **Таймер обратного отсчёта на вопрос не реализован**

### API Эндпоинты:

| Метод | URL | Доступ | Описание |
| :--- | :--- | :--- | :--- |
| `POST` | `/game/start/{quiz_id}` | **Автор** | Создать новую игровую сессию |
| `POST` | `/game/join` | **Участник** | Присоединиться к игре по PIN-коду |
| `POST` | `/game/next/{session_id}` | **Автор** | Переключить на следующий вопрос |
| `GET` | `/game/status/{pin}` | **Все** | Polling: получение текущего состояния игры |
| `POST` | `/game/answer` | **Участник** | Отправить вариант ответа |
| `GET` | `/game/stats/{session_id}/{question_id}` | **Автор** | Статистика ответов по конкретному вопросу |
| `GET` | `/game/leaderboard/{session_id}` | **Все** | Текущая таблица лидеров |
| `GET` | `/game/export/{session_id}` | **Автор** | Выгрузка результатов в формате `.xlsx` |

## Как работает Polling
Каждые 2 секунды клиент (и ведущий и участник) делает GET /game/status/{pin}. Сервер возвращает полное состояние: статус (waiting/active/finished), текущий вопрос, количество участников. Клиент смотрит на статус и рендерит нужный экран.
#### By *@karulny*
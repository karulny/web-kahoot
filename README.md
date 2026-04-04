# web-kahoot (Проект для ЯЛа)
![Static Badge](https://img.shields.io/badge/python_3.14-project-green?logo=python)
![Static Badge](https://img.shields.io/badge/flask-project-aqua?logo=flask)
![Static Badge](https://img.shields.io/badge/github-repo-grey?logo=github)


### для удобства, потом уберу:
- │ 
- ├── 
- └──

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

- **Альфа-версия без фронта, только бэк (endpoint для 11 апреля):**
- **Логика добавления и создания квизов**
- **Возможность ответить на квиз.**


#### By *@karulny*
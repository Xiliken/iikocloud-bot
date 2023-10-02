# [Документация по работе с ботом]()

# Оглавление
___
1.  [Запуск бота](#запуск-бота)
2.  [Миграция БД](#миграция-бд)
3.  [Обновление языкового файла](#обновление-языкового-файла)
4.  [Как работать с конфигом](#как-работать-с-конфигом)
    + [Типы возвращаемых значений в Config](#типы-возвращаемых-значений-в-config)
5. [Пример файла .env](#пример-файла-env)
6. [Используемые библиотеки](#используемые-библиотеки)
7. [Todo](#todo)

## Запуск бота


1.  Запускаем Redis, если он не запустился: `sudo service redis-server start`

2.  Запускаем бота из под Linux: `sudo systemctl start bot`


## Миграция БД


`alembic revision --autogenerate -m "message"` - обновить миграцию в автоматическом режиме

`alembic upgrade head` - залить изменения

`alembic revision -m "message"` - обновить миграцию в ручном режиме **(не рекомендую)**


## Обновление языкового файла


1.   `pybabel extract --input-dirs=. -o bot/locales/messages.pot`  \- инициализировать файл локализации

2.   `pybabel update -d bot/locales -D messages -i bot/locales/messages.pot`  \- обновить файлы переводов

3.  Переводим файлы, если нужно ([PoEdit](https://poedit.net/)  в помощь)

4.  `pybabel compile -d bot/locales -D messages` \- Скомпилировать файлы переводов


## Как работать с конфигом

Конфиг сейчас реализован довольно кривовато, но работать с ним можно. Все настройки хранятся в `.env`. [Типы возвращаемых значений.](#типы-возвращаемых-значений-в-config)


1.  Импортируем конфиг в нужный файл<br>
    ```python
    from bot.mics.helpers.Config import Config
    ```

2.  Для получения значения используем метод `get`<br>
    ```python
    Config.get("переменная из файла .env", "тип возвращаемого значения")
    ```

3.  Для установки значения используем метод `set`
    ```python
    Config.set("переменная из файла .env", "новое значение")
    ```

## Типы возвращаемых значений в Config:


*   `str` - строка **(по умолчанию)**

*   `bool` - boolean тип

*   `list` - конвертация в list

*   `dict` - конвертация в dict

*   `int` - конвертация в int

*   `float` - конвертация в float



## Пример файла .env

<details>
  <summary>Пример файла .env.example</summary>

  ```python
  # Telegram settings
TELEGRAM_BOT_API_KEY=
NOTIFY_ADMIN_IDS=

# IikoCloud API settings
IIKOCLOUD_LOGIN=
IIKOCLOUD_ORGANIZATIONS_IDS=

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379

# SMS Center Settings
SMSC_LOGIN=
SMSC_PASSWORD=
SMSC_POST=False
SMSC_HTTPS=False
SMSC_CHARSET=utf-8
SMSC_DEBUG=False

# SMS Center SMTP Settings
SMSC_SMTP_FROM=
SMSC_SMTP_SERVER=
SMSC_SMTP_LOGIN=
SMSC_SMTP_PASSWORD=

# Database Settings
DATABASE_URL=sqlite+aiosqlite:///database.db
DATABASE_DEBUG=True

# Other settings
DEBUG=True
LOG_TYPE=file# File, Console
MAINTENANCE=False
  ```
</details>


## Используемые библиотеки:

[Aiogram 3.x](https://docs.aiogram.dev/en/dev-3.x/)

[SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)

[AioCron](https://pypi.org/project/aiocron/)

## TODO:

- [ ] Перенести FSM на [aiogram-dialog](https://aiogram-dialog.readthedocs.io/en/develop/quickstart/index.html)
- [ ] Сделать админку
  -[x] Сделать статистику в админке
  - [ ] Сделать ручное создание копии БД
- [ ] Настроить интеграцию с Webhooks IikoCloud API ???
- [ ] Перенести возможно с SQLite на PostgreSQL
- [ ] Сделать автоматическую резервную копию БД
- [ ] Вывести с IikoCloud API статистику дохода ???
- [ ] Сделать работу с Config более удобной

# [Документация по работе с ботом]()

# Оглавление

1.  [Запуск бота](#запуск-бота)
2.  [Миграция БД](#миграция-бд)
3.  [Обновление языкового файла](#обновление-языкового-файла)
4.  [Как работать с конфигом](#как-работать-с-конфигом)
    + [Типы возвращаемых значений в Config](#типы-возвращаемых-значений-в-config)
5. [Пример файла .env](#пример-файла-env)
6. [Работа с pre-commit](#работа-с-pre-commit)
7. [Используемые библиотеки](#используемые-библиотеки)
8. [Todo](#todo)

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

# IikoServer API settings
IIKOSERVER_LOGIN=
IIKOSERVER_PASSWORD=
IIKOSERVER_DOMAIN=
IIKOSERVER_DEPARTMENTS_IDS=

# Redis Settings
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_USER=
REDIS_PASSWORD=

# SMS Center Settings
SMSC_LOGIN=
SMSC_PASSWORD=
SMSC_POST=False
SMSC_HTTPS=False
SMSC_CHARSET=utf-8

# SMS Center SMTP Settings
SMSC_SMTP_FROM=
SMSC_SMTP_SERVER=
SMSC_SMTP_LOGIN=
SMSC_SMTP_PASSWORD=

# Database Settings
DATABASE_URL=sqlite+aiosqlite:///database.db

# Localization Settings
I18N_PATH=bot/locales
I18N_DEFAULT_LOCALE=ru
I18N_DOMAIN=messages

# Other settings
DEBUG=True
# File, Console
LOG_TYPE=file
MAINTENANCE=False

  ```
</details>


## Работа с pre-commit
Сейчас стоят различные Git-хуки на коммит изменений.
Как `commit`, так и `push` может делаться не сразу, в силу того, что
система несколько раз почему-то перепроверяет все файлы на
соответствие стандартам программирования на Python. Поэтому рекомендую
несколько раз коммитить изменения 😃 Перед тем, как делать коммит, рекомендую
в терминале пару раз запустить `pre-commit run --all-files` - команда просто проверит
все файлы на соответствие стандартам и исправит их. А в следующий раз
уже должна вывести на всех пунктах `Passed`.

Все хуки можно настроить в `.pre-commit-config.yaml`



## Используемые библиотеки:

[Aiogram 3.x](https://docs.aiogram.dev/en/dev-3.x/)

[SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)

[AioCron](https://pypi.org/project/aiocron/)

## TODO:

- [ ] Перенести FSM на [aiogram-dialog](https://aiogram-dialog.readthedocs.io/en/develop/quickstart/index.html)
- [ ] Сделать админку
  - [x] Сделать статистику в админке
  - [x] Сделать ручное создание копии БД
  - [ ] Сделать управление пользователями через админку
  - [ ] Поиск пользователей через админку
- [ ] Настроить интеграцию с Webhooks IikoCloud API ???
- [ ] Перенести возможно с SQLite на PostgreSQL
- [x] Вывести с IikoCloud API статистику дохода
- [ ] Сделать работу с Config более удобной
- [ ] Выводить среднюю оценку по отзывам за текущий месяц (с 1 по n)
- [x] Автоматический бэкап БД
- [ ] Сделать профиль пользователя
  -  [ ] Просмотр истории заказов
  -  [ ] Редактирование учетной записи
- [ ] Перенести работу с Telegram с polling на Webhooks
- [x] Если пользователь удалил аккаунт, то не взаимодействовать с ним

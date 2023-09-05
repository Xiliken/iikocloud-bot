from __future__ import annotations

import sqlite3


class DBManager:
    __instance = None

    def __init__(self):
        self.connection = sqlite3.connect('data.db')
        self.cursor = self.connection.cursor()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users
            (
                user_id VARCHAR(255),
                nickname VARCHAR(255) UNIQUE
            );
        ''')

    def __del__(self):
        self.cursor.close()
        self.connection.close()

    @classmethod
    def singleton(cls):
        if not cls.__instance:
            cls.__instance = cls()

        return cls.__instance

    def user_exists(self, user_id):
        """Проверка пользователя в БД"""
        result = self.cursor.execute(f"SELECT `user_id` FROM `users` WHERE `user_id` = ?", ( str(user_id),) )
        return bool(result.fetchone())

    def add_user(self, user_id: str | int, nickname: None | str = None):
        """Добавление пользователя в БД"""
        try:
            self.cursor.execute("INSERT INTO `users` (`user_id`, `nickname`) VALUES (?, ?)", (str(user_id), str(nickname)))
            self.connection.commit()
        except sqlite3.Error as error:
            print(error)
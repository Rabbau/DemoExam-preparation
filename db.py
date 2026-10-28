"""Подключение к базе данных PostgreSQL и выполнение запросов."""
import configparser
from contextlib import contextmanager

import psycopg2
import psycopg2.extras

from app_paths import CONFIG_PATH


def load_db_settings():
    parser = configparser.ConfigParser()
    parser.read(CONFIG_PATH, encoding="utf-8")
    if not parser.has_section("database"):
        raise FileNotFoundError(f"Не найден раздел [database] в файле настроек {CONFIG_PATH}")
    section = parser["database"]
    return {
        "host": section.get("host", "127.0.0.1"),
        "port": section.getint("port", 5432),
        "dbname": section.get("dbname", "shoe_shop"),
        "user": section.get("user", "postgres"),
        "password": section.get("password", ""),
        "connect_timeout": 5,
    }


@contextmanager
def open_connection():
    """Соединение-транзакция: commit при успехе, rollback при любой ошибке."""
    connection = psycopg2.connect(**load_db_settings())
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def dict_cursor(connection):
    return connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


def fetch_all(sql, params=None):
    with open_connection() as connection:
        with dict_cursor(connection) as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()


def fetch_one(sql, params=None):
    with open_connection() as connection:
        with dict_cursor(connection) as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()


def check_connection():
    fetch_one("SELECT 1 AS ok")

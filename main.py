"""Точка входа приложения оформления заказов обуви."""
import sys
import traceback

import psycopg2
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication

from db import check_connection
from main_window import MainWindow
from messages import show_error
from style import APP_NAME, FONT_FAMILY, FONT_SIZE, STYLE_SHEET

DB_ERROR_TEXT = (
    "Нет связи с базой данных.\n"
    "Проверьте, что сервер PostgreSQL запущен, а настройки подключения в файле config.ini верны."
)


def handle_unexpected_error(exc_type, exc_value, exc_traceback):
    """Не даёт приложению аварийно закрыться: любая необработанная ошибка показывается сообщением."""
    traceback.print_exception(exc_type, exc_value, exc_traceback)
    if issubclass(exc_type, psycopg2.OperationalError):
        show_error(None, DB_ERROR_TEXT, "Ошибка базы данных")
        return
    show_error(None, f"Произошла непредвиденная ошибка:\n{exc_value}\n\n"
                     "Повторите действие. Если ошибка повторяется, перезапустите приложение.")


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    # Fusion одинаково выглядит на любой Windows и корректно принимает таблицу стилей.
    app.setStyle("Fusion")
    app.setFont(QFont(FONT_FAMILY, FONT_SIZE))
    app.setStyleSheet(STYLE_SHEET)
    sys.excepthook = handle_unexpected_error

    try:
        check_connection()
    except Exception as error:
        show_error(None, f"{DB_ERROR_TEXT}\n\nПодробности: {error}", "Ошибка базы данных")
        return 1

    window = MainWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())

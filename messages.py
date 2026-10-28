"""Окна сообщений с правильными заголовками, пиктограммами и русскими кнопками."""
from PyQt5.QtWidgets import QMessageBox


def _show(parent, icon, title, text):
    box = QMessageBox(icon, title, text, parent=parent)
    box.addButton("ОК", QMessageBox.AcceptRole)
    box.exec_()


def show_info(parent, text, title="Информация"):
    _show(parent, QMessageBox.Information, title, text)


def show_warning(parent, text, title="Предупреждение"):
    _show(parent, QMessageBox.Warning, title, text)


def show_error(parent, text, title="Ошибка"):
    _show(parent, QMessageBox.Critical, title, text)


def ask_confirm(parent, text, title="Подтверждение"):
    """Вопрос перед необратимым действием. По умолчанию выбрано «Нет»."""
    box = QMessageBox(QMessageBox.Question, title, text, parent=parent)
    yes_button = box.addButton("Да", QMessageBox.YesRole)
    no_button = box.addButton("Нет", QMessageBox.NoRole)
    box.setDefaultButton(no_button)
    box.exec_()
    return box.clickedButton() is yes_button

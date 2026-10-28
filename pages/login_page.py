from PyQt5.QtCore import QRegularExpression, Qt
from PyQt5.QtGui import QPixmap, QRegularExpressionValidator
from PyQt5.QtWidgets import QFrame, QLabel, QLineEdit, QVBoxLayout

from app_paths import resource_path
from messages import show_error, show_warning
from pages.base_page import BasePage
from pages.catalog_page import CatalogPage
from repository import find_user_by_login
from session import session
from style import COMPANY_NAME
from widgets import make_button, muted_label


class LoginPage(BasePage):
    page_key = "login"
    title = "Вход в систему"

    def __init__(self, main_window):
        super().__init__(main_window)
        self.setObjectName("loginPage")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.addStretch()

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(420)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 32, 36, 32)
        card_layout.setSpacing(12)

        logo_label = QLabel()
        logo_label.setPixmap(QPixmap(resource_path("logo.png")).scaledToHeight(90, Qt.SmoothTransformation))
        card_layout.addWidget(logo_label, alignment=Qt.AlignCenter)

        title_label = QLabel(COMPANY_NAME)
        title_label.setObjectName("loginTitle")
        card_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        card_layout.addWidget(muted_label("Войдите, чтобы оформить заказ"), alignment=Qt.AlignCenter)
        card_layout.addSpacing(8)

        card_layout.addWidget(QLabel("Логин"))
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Логин из списка пользователей")
        self.login_edit.setToolTip("Пароль не требуется. Пробелы в логине недопустимы.")
        self.login_edit.setMaxLength(100)
        self.login_edit.setValidator(QRegularExpressionValidator(QRegularExpression(r"\S*")))
        self.login_edit.returnPressed.connect(self.login)
        card_layout.addWidget(self.login_edit)
        card_layout.addSpacing(4)

        login_button = make_button("Войти")
        login_button.clicked.connect(self.login)
        card_layout.addWidget(login_button)

        guest_button = make_button("Продолжить как гость", "secondary")
        guest_button.clicked.connect(self.login_as_guest)
        card_layout.addWidget(guest_button)

        layout.addWidget(card, alignment=Qt.AlignCenter)
        layout.addStretch()

    def on_shown(self):
        # Возврат на эту страницу кнопкой «Назад» означает выход из учётной записи.
        session.logout()
        self.login_edit.setFocus()

    def login(self):
        login = self.login_edit.text().strip()
        if not login:
            show_warning(self, "Введите логин. Логины пользователей указаны в списке пользователей системы.")
            return
        user = find_user_by_login(login)
        if user is None:
            show_error(
                self,
                f"Пользователь с логином «{login}» не найден.\n"
                "Проверьте раскладку клавиатуры и правильность ввода или войдите как гость.",
                "Ошибка входа",
            )
            return
        session.login(user)
        self.login_edit.clear()
        self.main_window.open_page(CatalogPage(self.main_window))

    def login_as_guest(self):
        session.logout()
        self.main_window.open_page(CatalogPage(self.main_window))

"""Главное окно: шапка (логотип, заголовок, ФИО, «Назад») и стек страниц с историей переходов."""
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from app_paths import resource_path
from pages.login_page import LoginPage
from session import session
from style import APP_NAME
from widgets import make_button


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(resource_path("icon.ico")))
        self.resize(1100, 760)
        self.setMinimumSize(900, 600)
        self.history = []

        central = QWidget()
        central_layout = QVBoxLayout(central)
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)

        self.header = QFrame()
        self.header.setObjectName("header")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(14)

        logo_label = QLabel()
        logo_label.setPixmap(QPixmap(resource_path("logo.png")).scaledToHeight(44, Qt.SmoothTransformation))
        header_layout.addWidget(logo_label)

        self.back_button = make_button("← Назад", "secondary")
        self.back_button.clicked.connect(self.go_back)
        header_layout.addWidget(self.back_button)

        self.title_label = QLabel()
        self.title_label.setObjectName("pageTitle")
        header_layout.addWidget(self.title_label, stretch=1)

        user_layout = QVBoxLayout()
        user_layout.setSpacing(0)
        self.user_name_label = QLabel()
        self.user_name_label.setObjectName("userName")
        self.user_role_label = QLabel()
        self.user_role_label.setObjectName("userRole")
        user_layout.addWidget(self.user_name_label, alignment=Qt.AlignRight)
        user_layout.addWidget(self.user_role_label, alignment=Qt.AlignRight)
        header_layout.addLayout(user_layout)

        central_layout.addWidget(self.header)

        self.stack = QStackedWidget()
        central_layout.addWidget(self.stack, stretch=1)
        self.setCentralWidget(central)

        self.open_page(LoginPage(self))

    def open_page(self, page):
        self.history.append(page)
        self.stack.addWidget(page)
        self._show_current()

    def go_back(self):
        if len(self.history) < 2:
            return
        self._pop_page()
        self._show_current()

    def go_back_to(self, page_key):
        """Возврат к ближайшей странице с указанным page_key (например, после оформления заказа)."""
        if not any(page.page_key == page_key for page in self.history):
            page_key = "catalog"
        while len(self.history) > 1 and self.history[-1].page_key != page_key:
            self._pop_page()
        self._show_current()

    def _pop_page(self):
        page = self.history.pop()
        self.stack.removeWidget(page)
        page.deleteLater()

    def _show_current(self):
        page = self.history[-1]
        self.stack.setCurrentWidget(page)
        self.title_label.setText(page.title)
        self.setWindowTitle(f"{APP_NAME}: {page.title}")
        self.back_button.setVisible(len(self.history) > 1)
        page.on_shown()
        if session.is_authorized:
            self.user_name_label.setText(session.full_name)
            self.user_role_label.setText(session.role)
        elif page.page_key != "login":
            self.user_name_label.setText("Гость")
            self.user_role_label.setText("просмотр каталога")
        else:
            self.user_name_label.setText("")
            self.user_role_label.setText("")

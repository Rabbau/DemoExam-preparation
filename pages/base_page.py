from PyQt5.QtWidgets import QWidget


class BasePage(QWidget):
    """Страница в стеке главного окна. title попадает в шапку и заголовок окна."""

    page_key = ""
    title = ""

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def on_shown(self):
        """Вызывается при каждом показе страницы, в том числе после возврата «Назад»."""

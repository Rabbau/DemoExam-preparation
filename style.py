"""Оформление по руководству по стилю (Приложение 3).

На экзамене меняются только константы из первого блока: название, шрифт и три цвета руководства.
Остальные цвета нейтральные и подходят к любой палитре.
"""

from app_paths import resource_path

COMPANY_NAME = "ООО «Обувь»"
APP_NAME = f"{COMPANY_NAME} — оформление заказов"

FONT_FAMILY = "Segoe UI"
FONT_SIZE = 14

COLOR_MAIN_BG = "#FFFFFF"
COLOR_SECONDARY_BG = "#E8F3EE"
COLOR_ACCENT = "#1F8A5B"

# Нейтральные цвета, не зависящие от руководства.
COLOR_TEXT = "#1F2933"
COLOR_MUTED = "#6B7280"
COLOR_BORDER = "#D9DEE3"
COLOR_LOW_STOCK = "#FFCCCC"
COLOR_DISCOUNT = "#D93025"
COLOR_OLD_PRICE = COLOR_DISCOUNT


def _hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[index:index + 2], 16) for index in (0, 2, 4))


def _shade(color, factor):
    """Затемняет цвет (factor < 1) для состояний hover/pressed."""
    red, green, blue = (max(0, min(255, int(channel * factor))) for channel in _hex_to_rgb(color))
    return f"#{red:02X}{green:02X}{blue:02X}"


def _text_on(color):
    """Чёрный или белый текст в зависимости от яркости фона, чтобы надпись читалась на любом акценте."""
    red, green, blue = _hex_to_rgb(color)
    brightness = 0.299 * red + 0.587 * green + 0.114 * blue
    return COLOR_TEXT if brightness > 150 else "#FFFFFF"


COLOR_ON_ACCENT = _text_on(COLOR_ACCENT)

# В url() таблицы стилей нужны прямые слэши.
ARROW_DOWN = resource_path("ui", "arrow_down.png").replace("\\", "/")
ARROW_UP = resource_path("ui", "arrow_up.png").replace("\\", "/")

STYLE_SHEET = f"""
QWidget {{
    font-family: "{FONT_FAMILY}";
    font-size: {FONT_SIZE}px;
    color: {COLOR_TEXT};
}}
QMainWindow, QDialog, QMessageBox {{
    background-color: {COLOR_MAIN_BG};
}}
QLabel {{
    background: transparent;
}}
QLabel[muted="true"] {{
    color: {COLOR_MUTED};
}}

QFrame#header {{
    background-color: {COLOR_SECONDARY_BG};
    border-bottom: 1px solid {COLOR_BORDER};
}}
QLabel#pageTitle {{
    font-size: {FONT_SIZE + 8}px;
    font-weight: bold;
}}
QLabel#userName {{
    font-weight: bold;
}}
QLabel#userRole {{
    color: {COLOR_MUTED};
    font-size: {FONT_SIZE - 1}px;
}}

QWidget#loginPage {{
    background-color: {COLOR_SECONDARY_BG};
}}
QFrame#loginCard, QFrame#panel {{
    background-color: {COLOR_MAIN_BG};
    border: 1px solid {COLOR_BORDER};
    border-radius: 14px;
}}
QLabel#loginTitle {{
    font-size: {FONT_SIZE + 10}px;
    font-weight: bold;
}}

QPushButton {{
    background-color: {COLOR_ACCENT};
    color: {COLOR_ON_ACCENT};
    border: 1px solid {COLOR_ACCENT};
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {_shade(COLOR_ACCENT, 0.9)};
    border-color: {_shade(COLOR_ACCENT, 0.9)};
}}
QPushButton:pressed {{
    background-color: {_shade(COLOR_ACCENT, 0.8)};
}}
QPushButton:disabled {{
    background-color: #E5E7EB;
    border-color: #E5E7EB;
    color: #9CA3AF;
}}
QPushButton[kind="secondary"] {{
    background-color: {COLOR_MAIN_BG};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_BORDER};
}}
QPushButton[kind="secondary"]:hover {{
    border-color: {COLOR_ACCENT};
    color: {COLOR_ACCENT};
}}
QPushButton[kind="danger"] {{
    background-color: {COLOR_MAIN_BG};
    color: {COLOR_DISCOUNT};
    border: 1px solid #F1B5B0;
}}
QPushButton[kind="danger"]:hover {{
    background-color: #FDECEA;
}}

QLineEdit, QComboBox, QSpinBox, QDateEdit {{
    background-color: {COLOR_MAIN_BG};
    border: 1px solid {COLOR_BORDER};
    border-radius: 8px;
    padding: 6px 10px;
    min-height: 22px;
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus {{
    border: 1px solid {COLOR_ACCENT};
}}
QComboBox, QDateEdit {{
    padding-right: 32px;
}}
QComboBox::drop-down, QDateEdit::drop-down {{
    subcontrol-origin: padding;
    subcontrol-position: center right;
    width: 30px;
    border: none;
}}
QComboBox::down-arrow, QDateEdit::down-arrow {{
    image: url("{ARROW_DOWN}");
    width: 14px;
    height: 14px;
}}
QSpinBox {{
    padding-right: 28px;
}}
QSpinBox::up-button, QSpinBox::down-button {{
    subcontrol-origin: border;
    width: 26px;
    border: none;
    background: transparent;
}}
QSpinBox::up-button {{
    subcontrol-position: top right;
}}
QSpinBox::down-button {{
    subcontrol-position: bottom right;
}}
QSpinBox::up-arrow {{
    image: url("{ARROW_UP}");
    width: 12px;
    height: 12px;
}}
QSpinBox::down-arrow {{
    image: url("{ARROW_DOWN}");
    width: 12px;
    height: 12px;
}}
QSpinBox::up-arrow:disabled, QSpinBox::down-arrow:disabled, QSpinBox::up-arrow:off, QSpinBox::down-arrow:off {{
    image: none;
}}
QComboBox QAbstractItemView {{
    background-color: {COLOR_MAIN_BG};
    border: 1px solid {COLOR_BORDER};
    selection-background-color: {COLOR_SECONDARY_BG};
    selection-color: {COLOR_TEXT};
    outline: 0;
}}

QListWidget {{
    background: transparent;
    border: none;
    outline: 0;
}}
QListWidget::item, QListWidget::item:selected, QListWidget::item:hover {{
    background: transparent;
    border: none;
}}
QFrame#productRow {{
    background-color: {COLOR_MAIN_BG};
    border: 1px solid {COLOR_BORDER};
    border-radius: 12px;
}}
QFrame#productRow:hover {{
    border: 1px solid {COLOR_ACCENT};
}}
QFrame#productRow[lowStock="true"] {{
    background-color: {COLOR_LOW_STOCK};
    border-color: #F2A7A7;
}}
QLabel#productImage {{
    background-color: #F5F6F7;
    border-radius: 8px;
}}
QLabel#productName {{
    font-size: {FONT_SIZE + 3}px;
    font-weight: bold;
}}
QLabel#price {{
    font-size: {FONT_SIZE + 6}px;
    font-weight: bold;
}}
QLabel#oldPrice {{
    color: {COLOR_OLD_PRICE};
}}
QLabel#discountBadge {{
    background-color: {COLOR_DISCOUNT};
    color: #FFFFFF;
    border-radius: 10px;
    padding: 2px 8px;
    font-weight: bold;
}}
QLabel#stockBadge {{
    border-radius: 10px;
    padding: 3px 10px;
    font-weight: bold;
}}
QLabel#stockBadge[level="many"] {{
    background-color: #E3F4EA;
    color: #1B6B43;
}}
QLabel#stockBadge[level="few"] {{
    background-color: #FFF1DB;
    color: #8A5300;
}}
QLabel#emptyState {{
    color: {COLOR_MUTED};
    font-size: {FONT_SIZE + 2}px;
    padding: 40px;
}}

QTableWidget {{
    background-color: {COLOR_MAIN_BG};
    alternate-background-color: #F8FAF9;
    border: 1px solid {COLOR_BORDER};
    border-radius: 10px;
    gridline-color: transparent;
    selection-background-color: {COLOR_SECONDARY_BG};
    selection-color: {COLOR_TEXT};
    outline: 0;
}}
QTableWidget::item {{
    padding: 4px 8px;
}}
QHeaderView::section {{
    background-color: {COLOR_SECONDARY_BG};
    color: {COLOR_TEXT};
    font-weight: bold;
    padding: 8px;
    border: none;
    border-bottom: 1px solid {COLOR_BORDER};
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px;
}}
QScrollBar::handle:vertical {{
    background: #C9CED4;
    border-radius: 4px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
    background: none;
}}
"""

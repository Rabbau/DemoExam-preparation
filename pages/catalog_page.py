from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from messages import show_info
from pages.base_page import BasePage
from pages.cart_page import CartPage
from pages.product_card_page import ProductCardPage
from repository import load_categories, load_products
from session import session
from widgets import ProductRow, make_button, muted_label

ALL_CATEGORIES = "Все категории"
SORT_NONE = "none"
SORT_ASC = "asc"
SORT_DESC = "desc"


class CatalogPage(BasePage):
    page_key = "catalog"
    title = "Каталог товаров"

    def __init__(self, main_window, title=None):
        super().__init__(main_window)
        if title:
            self.title = title
        self.products = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Панель поиска/фильтра/сортировки доступна только авторизованным пользователям.
        self.tools_panel = QWidget()
        tools_layout = QHBoxLayout(self.tools_panel)
        tools_layout.setContentsMargins(0, 0, 0, 0)
        tools_layout.setSpacing(10)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Поиск по наименованию и описанию")
        self.search_edit.setMaxLength(100)
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(self.apply_filters)
        tools_layout.addWidget(self.search_edit, stretch=1)

        self.category_combo = QComboBox()
        self.category_combo.setMinimumWidth(180)
        self.category_combo.currentIndexChanged.connect(self.apply_filters)
        tools_layout.addWidget(self.category_combo)

        self.sort_combo = QComboBox()
        self.sort_combo.setMinimumWidth(200)
        self.sort_combo.addItem("Без сортировки", SORT_NONE)
        self.sort_combo.addItem("Цена по возрастанию", SORT_ASC)
        self.sort_combo.addItem("Цена по убыванию", SORT_DESC)
        self.sort_combo.currentIndexChanged.connect(self.apply_filters)
        tools_layout.addWidget(self.sort_combo)

        layout.addWidget(self.tools_panel)

        buttons_layout = QHBoxLayout()
        self.count_label = muted_label()
        buttons_layout.addWidget(self.count_label, stretch=1)
        self.orders_button = make_button("Заказы", "secondary")
        self.orders_button.clicked.connect(self.open_orders)
        buttons_layout.addWidget(self.orders_button)
        self.cart_button = make_button("")
        self.cart_button.clicked.connect(self.open_cart)
        buttons_layout.addWidget(self.cart_button)
        layout.addLayout(buttons_layout)

        self.product_list = QListWidget()
        self.product_list.setSpacing(5)
        self.product_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.product_list.itemClicked.connect(self.open_product)
        layout.addWidget(self.product_list, stretch=1)

        self.empty_label = QLabel("Ничего не найдено. Измените строку поиска или выберите другую категорию.")
        self.empty_label.setObjectName("emptyState")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setWordWrap(True)
        layout.addWidget(self.empty_label, stretch=1)

        self.tools_panel.setVisible(session.is_authorized)
        self.cart_button.setVisible(session.is_authorized)
        # Из списка заказов эта страница открывается для выбора товара — второй переход в заказы не нужен.
        self.orders_button.setVisible(session.is_staff and session.order_origin != "orders")
        self.load_category_items()

    def load_category_items(self):
        self.category_combo.blockSignals(True)
        self.category_combo.clear()
        self.category_combo.addItem(ALL_CATEGORIES, None)
        for category in load_categories():
            self.category_combo.addItem(category, category)
        self.category_combo.blockSignals(False)

    def on_shown(self):
        # Данные перечитываются при каждом показе: после заказа меняются остатки и скидки.
        self.products = load_products()
        self.cart_button.setText(f"Корзина · {session.cart.positions_count()}")
        self.apply_filters()

    def apply_filters(self):
        search_text = self.search_edit.text().strip().lower()
        category = self.category_combo.currentData()
        sort_mode = self.sort_combo.currentData()

        visible = []
        for product in self.products:
            if category is not None and product.category != category:
                continue
            if search_text and search_text not in product.name.lower() and search_text not in product.description.lower():
                continue
            visible.append(product)

        if sort_mode == SORT_ASC:
            visible.sort(key=lambda item: item.final_price)
        elif sort_mode == SORT_DESC:
            visible.sort(key=lambda item: item.final_price, reverse=True)

        self.show_products(visible)

    def show_products(self, products):
        self.product_list.clear()
        for product in products:
            row_widget = ProductRow(product)
            list_item = QListWidgetItem()
            list_item.setData(Qt.UserRole, product)
            list_item.setSizeHint(row_widget.sizeHint())
            self.product_list.addItem(list_item)
            self.product_list.setItemWidget(list_item, row_widget)
        self.count_label.setText(f"Показано товаров: {len(products)} из {len(self.products)}")
        self.product_list.setVisible(bool(products))
        self.empty_label.setVisible(not products)

    def open_product(self, list_item):
        if not session.is_authorized:
            show_info(self, "Чтобы оформить заказ, войдите в систему: нажмите «Назад» и введите логин.")
            return
        product = list_item.data(Qt.UserRole)
        self.main_window.open_page(ProductCardPage(self.main_window, product))

    def open_cart(self):
        self.main_window.open_page(CartPage(self.main_window))

    def open_orders(self):
        # Локальный импорт: orders_page сам открывает каталог для нового заказа.
        from pages.orders_page import OrdersPage
        self.main_window.open_page(OrdersPage(self.main_window))

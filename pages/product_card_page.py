from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QFormLayout, QFrame, QHBoxLayout, QLabel, QSpinBox, QVBoxLayout

from messages import ask_confirm, show_warning
from pages.base_page import BasePage
from pages.cart_page import CartPage
from pricing import format_size
from repository import load_product_sizes
from session import CartItem, session
from widgets import load_product_pixmap, make_button, make_price_block, make_stock_badge, muted_label


class ProductCardPage(BasePage):
    page_key = "product"
    title = "Просмотр товара"

    def __init__(self, main_window, product):
        super().__init__(main_window)
        self.product = product
        self.sizes = []

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(20)

        image_panel = QFrame()
        image_panel.setObjectName("panel")
        image_layout = QVBoxLayout(image_panel)
        image_layout.setContentsMargins(16, 16, 16, 16)
        image_label = QLabel()
        image_label.setObjectName("productImage")
        image_label.setFixedSize(320, 320)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setPixmap(load_product_pixmap(product.photo, 300, 300))
        image_layout.addWidget(image_label)
        image_layout.addStretch()
        layout.addWidget(image_panel, alignment=Qt.AlignTop)

        info_panel = QFrame()
        info_panel.setObjectName("panel")
        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(24, 20, 24, 20)
        info_layout.setSpacing(10)

        info_layout.addWidget(muted_label(product.category))
        name_label = QLabel(product.name)
        name_label.setObjectName("productName")
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)
        info_layout.addLayout(make_price_block(product))
        info_layout.addWidget(make_stock_badge(product.total_quantity), alignment=Qt.AlignLeft)

        form = QFormLayout()
        form.setHorizontalSpacing(16)
        form.setVerticalSpacing(8)
        form.addRow(muted_label("Производство"), QLabel(product.manufacturer))
        composition_label = QLabel(product.composition)
        composition_label.setWordWrap(True)
        form.addRow(muted_label("Состав"), composition_label)
        description_label = QLabel(product.description)
        description_label.setWordWrap(True)
        form.addRow(muted_label("Описание"), description_label)
        self.size_range_label = QLabel()
        self.size_range_label.setWordWrap(True)
        form.addRow(muted_label("Размерный ряд"), self.size_range_label)

        self.size_combo = QComboBox()
        self.size_combo.currentIndexChanged.connect(self.update_quantity_limit)
        form.addRow(muted_label("Размер"), self.size_combo)

        self.quantity_spin = QSpinBox()
        self.quantity_spin.setSuffix(" пар.")
        self.quantity_spin.setFixedWidth(140)
        form.addRow(muted_label("Количество"), self.quantity_spin)
        info_layout.addLayout(form)
        info_layout.addSpacing(8)

        buttons_layout = QHBoxLayout()
        self.add_button = make_button("Добавить в заказ")
        self.add_button.clicked.connect(self.add_to_cart)
        buttons_layout.addWidget(self.add_button)
        cart_button = make_button("Перейти к оформлению", "secondary")
        cart_button.clicked.connect(self.open_cart)
        buttons_layout.addWidget(cart_button)
        buttons_layout.addStretch()
        info_layout.addLayout(buttons_layout)
        info_layout.addStretch()

        layout.addWidget(info_panel, stretch=1, alignment=Qt.AlignTop)

    def on_shown(self):
        self.sizes = load_product_sizes(self.product.product_id)
        self.size_range_label.setText(", ".join(format_size(row["size_value"]) for row in self.sizes) or "—")

        self.size_combo.blockSignals(True)
        self.size_combo.clear()
        for row in self.sizes:
            # Учитываем пары, уже положенные в корзину, иначе можно заказать больше остатка.
            available = row["quantity"] - session.cart.reserved_quantity(row["product_size_id"])
            if available > 0:
                text = f"{format_size(row['size_value'])} (в наличии: {available})"
                self.size_combo.addItem(text, (row, available))
        self.size_combo.blockSignals(False)

        has_sizes = self.size_combo.count() > 0
        if not has_sizes:
            self.size_combo.addItem("Нет в наличии", None)
        self.size_combo.setEnabled(has_sizes)
        self.add_button.setEnabled(has_sizes)
        self.update_quantity_limit()

    def update_quantity_limit(self):
        data = self.size_combo.currentData()
        if data is None:
            self.quantity_spin.setRange(0, 0)
            self.quantity_spin.setEnabled(False)
            return
        available = data[1]
        self.quantity_spin.setEnabled(True)
        self.quantity_spin.setRange(1, available)
        self.quantity_spin.setToolTip(f"От 1 до {available} пар")

    def add_to_cart(self):
        data = self.size_combo.currentData()
        if data is None:
            show_warning(self, "Выберите размер из списка доступных.")
            return
        size_row = data[0]
        session.cart.add(CartItem(
            product_size_id=size_row["product_size_id"],
            product_name=self.product.name,
            manufacturer_name=self.product.manufacturer,
            size_value=format_size(size_row["size_value"]),
            quantity=self.quantity_spin.value(),
            unit_price=self.product.final_price,
        ))
        if ask_confirm(self, "Товар добавлен в заказ.\nПерейти к оформлению заказа?", "Товар добавлен"):
            self.open_cart()
        else:
            self.main_window.go_back()

    def open_cart(self):
        self.main_window.open_page(CartPage(self.main_window))

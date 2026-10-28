from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QComboBox, QHBoxLayout, QLabel, QTableWidget, QVBoxLayout

from messages import ask_confirm, show_error, show_info, show_warning
from pages.base_page import BasePage
from pricing import format_money
from repository import NotEnoughStockError, create_order, load_clients
from session import session
from widgets import configure_table, fit_table_columns, make_button, muted_label, table_item

COLUMNS = ["Товар", "Производство", "Размер", "Количество", "Цена за пару", "Сумма"]
NUMERIC_COLUMNS = {3, 4, 5}


class CartPage(BasePage):
    page_key = "cart"
    title = "Оформление заказа"

    def __init__(self, main_window):
        super().__init__(main_window)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # Менеджер и Администратор оформляют заказ на клиента, клиент — на себя.
        self.client_combo = QComboBox()
        if session.is_staff:
            client_layout = QHBoxLayout()
            client_layout.addWidget(muted_label("Клиент"))
            for client in load_clients():
                self.client_combo.addItem(client["full_name"], client["user_id"])
            client_layout.addWidget(self.client_combo, stretch=1)
            layout.addLayout(client_layout)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        configure_table(self.table, stretch_column=0)
        layout.addWidget(self.table, stretch=1)

        self.total_label = QLabel()
        self.total_label.setObjectName("price")
        layout.addWidget(self.total_label)

        buttons_layout = QHBoxLayout()
        self.remove_button = make_button("Удалить позицию", "danger")
        self.remove_button.clicked.connect(self.remove_item)
        buttons_layout.addWidget(self.remove_button)
        buttons_layout.addStretch()
        self.cancel_button = make_button("Отказаться от заказа", "secondary")
        self.cancel_button.clicked.connect(self.cancel_order)
        buttons_layout.addWidget(self.cancel_button)
        self.confirm_button = make_button("Подтвердить заказ")
        self.confirm_button.clicked.connect(self.confirm_order)
        buttons_layout.addWidget(self.confirm_button)
        layout.addLayout(buttons_layout)

    def on_shown(self):
        self.fill_table()

    def fill_table(self):
        items = list(session.cart.items.values())
        self.table.setRowCount(len(items))
        for row_index, item in enumerate(items):
            values = [
                item.product_name,
                item.manufacturer_name,
                item.size_value,
                str(item.quantity),
                format_money(item.unit_price),
                format_money(item.line_total),
            ]
            for column, value in enumerate(values):
                self.table.setItem(row_index, column, table_item(value, column in NUMERIC_COLUMNS))
            self.table.item(row_index, 0).setData(Qt.UserRole, item.product_size_id)
        fit_table_columns(self.table)

        is_empty = session.cart.is_empty()
        self.total_label.setText(f"Итого: {format_money(session.cart.total())}" if not is_empty
                                 else "Заказ пуст. Выберите товары в каталоге.")
        self.remove_button.setEnabled(not is_empty)
        self.cancel_button.setEnabled(not is_empty)
        self.confirm_button.setEnabled(not is_empty)

    def remove_item(self):
        row = self.table.currentRow()
        if row < 0:
            show_warning(self, "Выберите позицию в таблице, которую нужно удалить.")
            return
        product_size_id = self.table.item(row, 0).data(Qt.UserRole)
        session.cart.remove(product_size_id)
        self.fill_table()

    def cancel_order(self):
        if not ask_confirm(self, "Отказаться от заказа? Все выбранные позиции будут удалены."):
            return
        session.cart.clear()
        self.return_to_origin()

    def confirm_order(self):
        if session.is_staff:
            user_id = self.client_combo.currentData()
            if user_id is None:
                show_warning(self, "Выберите клиента, на которого оформляется заказ.")
                return
        else:
            user_id = session.user["user_id"]

        if not ask_confirm(self, f"Подтвердить заказ на сумму {format_money(session.cart.total())}?"):
            return
        try:
            order_id = create_order(user_id, list(session.cart.items.values()))
        except NotEnoughStockError as error:
            show_error(self, f"Не удалось оформить заказ: {error}\n"
                             "Удалите эту позицию или уменьшите количество и повторите.")
            return
        session.cart.clear()
        show_info(self, f"Заказ № {order_id} оформлен.", "Заказ оформлен")
        self.return_to_origin()

    def return_to_origin(self):
        origin = session.order_origin
        session.order_origin = "catalog"
        self.main_window.go_back_to(origin)

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QTableWidget, QVBoxLayout

from messages import ask_confirm, show_info, show_warning
from pages.base_page import BasePage
from pages.catalog_page import CatalogPage
from pages.order_details_page import OrderDetailsPage
from pricing import format_money
from repository import delete_order, load_orders
from session import session
from widgets import configure_table, fit_table_columns, make_button, table_item

COLUMNS = ["№ заказа", "Дата заказа", "ФИО клиента", "Позиций", "Сумма"]
NUMERIC_COLUMNS = {3, 4}


class OrdersPage(BasePage):
    page_key = "orders"
    title = "Список заказов"

    def __init__(self, main_window):
        super().__init__(main_window)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        configure_table(self.table, stretch_column=2)
        self.table.doubleClicked.connect(self.open_details)
        layout.addWidget(self.table, stretch=1)

        buttons_layout = QHBoxLayout()
        new_button = make_button("Новый заказ")
        new_button.clicked.connect(self.new_order)
        buttons_layout.addWidget(new_button)
        details_text = "Состав / редактирование" if session.is_admin else "Состав заказа"
        details_button = make_button(details_text, "secondary")
        details_button.clicked.connect(self.open_details)
        buttons_layout.addWidget(details_button)
        buttons_layout.addStretch()
        delete_button = make_button("Удалить заказ", "danger")
        delete_button.clicked.connect(self.delete_selected)
        buttons_layout.addWidget(delete_button)
        layout.addLayout(buttons_layout)

    def on_shown(self):
        session.order_origin = "catalog"
        orders = load_orders()
        self.table.setRowCount(len(orders))
        for row_index, order in enumerate(orders):
            values = [
                str(order["order_id"]),
                order["order_date"].strftime("%d.%m.%Y"),
                order["client_name"],
                str(order["positions_count"]),
                format_money(order["total"]),
            ]
            for column, value in enumerate(values):
                self.table.setItem(row_index, column, table_item(value, column in NUMERIC_COLUMNS))
            self.table.item(row_index, 0).setData(Qt.UserRole, order["order_id"])
        fit_table_columns(self.table)

    def selected_order_id(self):
        row = self.table.currentRow()
        if row < 0:
            show_warning(self, "Выберите заказ в списке.")
            return None
        return self.table.item(row, 0).data(Qt.UserRole)

    def new_order(self):
        if not session.cart.is_empty() and not ask_confirm(
                self, "В корзине уже есть товары. Начать новый заказ с этими товарами?"):
            session.cart.clear()
        session.order_origin = "orders"
        self.main_window.open_page(CatalogPage(self.main_window, "Новый заказ: выбор товара"))

    def open_details(self):
        order_id = self.selected_order_id()
        if order_id is None:
            return
        self.main_window.open_page(OrderDetailsPage(self.main_window, order_id))

    def delete_selected(self):
        order_id = self.selected_order_id()
        if order_id is None:
            return
        if not ask_confirm(self, f"Удалить заказ № {order_id}?\n"
                                 "Товары вернутся на склад. Действие нельзя отменить.", "Удаление заказа"):
            return
        delete_order(order_id)
        show_info(self, f"Заказ № {order_id} удалён.")
        self.on_shown()

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import QDateEdit, QFormLayout, QHBoxLayout, QLabel, QTableWidget, QVBoxLayout

from messages import ask_confirm, show_info, show_warning
from pages.base_page import BasePage
from pricing import format_money, format_size
from repository import load_order, load_order_items, update_order
from session import session
from widgets import configure_table, fit_table_columns, make_button, muted_label, table_item

COLUMNS = ["Модель", "Производство", "Размер", "Количество", "Цена за единицу", "Сумма"]
NUMERIC_COLUMNS = {3, 4, 5}


class OrderDetailsPage(BasePage):
    page_key = "order_details"

    def __init__(self, main_window, order_id):
        super().__init__(main_window)
        self.order_id = order_id
        self.editable = session.is_admin
        self.title = f"Заказ № {order_id}: редактирование" if self.editable else f"Заказ № {order_id}: состав"
        self.items = []
        self.removed_item_ids = set()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)
        form = QFormLayout()
        self.client_label = QLabel()
        form.addRow(muted_label("Клиент"), self.client_label)
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd.MM.yyyy")
        self.date_edit.setFixedWidth(160)
        self.date_edit.setMaximumDate(QDate.currentDate())
        self.date_edit.setToolTip("Дата заказа не может быть позже сегодняшней")
        self.date_edit.setEnabled(self.editable)
        form.addRow(muted_label("Дата заказа"), self.date_edit)
        layout.addLayout(form)

        self.table = QTableWidget(0, len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        configure_table(self.table, stretch_column=0)
        layout.addWidget(self.table, stretch=1)

        self.total_label = QLabel()
        self.total_label.setObjectName("price")
        layout.addWidget(self.total_label)

        if self.editable:
            buttons_layout = QHBoxLayout()
            remove_button = make_button("Удалить позицию", "danger")
            remove_button.clicked.connect(self.remove_item)
            buttons_layout.addWidget(remove_button)
            buttons_layout.addStretch()
            save_button = make_button("Сохранить изменения")
            save_button.clicked.connect(self.save)
            buttons_layout.addWidget(save_button)
            layout.addLayout(buttons_layout)

        self.load()

    def load(self):
        order = load_order(self.order_id)
        self.client_label.setText(order["client_name"])
        order_date = order["order_date"]
        self.date_edit.setDate(QDate(order_date.year, order_date.month, order_date.day))
        self.items = load_order_items(self.order_id)
        self.removed_item_ids.clear()
        self.fill_table()

    def visible_items(self):
        return [item for item in self.items if item["order_item_id"] not in self.removed_item_ids]

    def fill_table(self):
        items = self.visible_items()
        self.table.setRowCount(len(items))
        for row_index, item in enumerate(items):
            values = [
                item["product_name"],
                item["manufacturer_name"],
                format_size(item["size_value"]),
                str(item["quantity"]),
                format_money(item["unit_price"]),
                format_money(item["line_total"]),
            ]
            for column, value in enumerate(values):
                self.table.setItem(row_index, column, table_item(value, column in NUMERIC_COLUMNS))
            self.table.item(row_index, 0).setData(Qt.UserRole, item["order_item_id"])
        fit_table_columns(self.table)
        total = sum((item["line_total"] for item in items), 0)
        self.total_label.setText(f"Итоговая сумма заказа: {format_money(total)}")

    def remove_item(self):
        row = self.table.currentRow()
        if row < 0:
            show_warning(self, "Выберите позицию, которую нужно удалить из заказа.")
            return
        if len(self.visible_items()) == 1:
            show_warning(self, "В заказе должна остаться хотя бы одна позиция.\n"
                               "Чтобы удалить заказ целиком, используйте «Удалить заказ» в списке заказов.")
            return
        self.removed_item_ids.add(self.table.item(row, 0).data(Qt.UserRole))
        self.fill_table()

    def save(self):
        question = "Сохранить изменения заказа?"
        if self.removed_item_ids:
            question += f"\nУдаляемых позиций: {len(self.removed_item_ids)}. Товары вернутся на склад."
        if not ask_confirm(self, question):
            return
        update_order(self.order_id, self.date_edit.date().toPyDate(), self.removed_item_ids)
        show_info(self, f"Изменения заказа № {self.order_id} сохранены.")
        self.main_window.go_back()

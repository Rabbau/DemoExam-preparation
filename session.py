"""Текущий пользователь и формируемый заказ (корзина)."""
from dataclasses import dataclass

ROLE_ADMIN = "Администратор"
ROLE_MANAGER = "Менеджер"
ROLE_CLIENT = "Авторизированный клиент"


@dataclass
class CartItem:
    product_size_id: int
    product_name: str
    manufacturer_name: str
    size_value: object
    quantity: int
    unit_price: object

    @property
    def line_total(self):
        return self.unit_price * self.quantity


class Cart:
    def __init__(self):
        self.items = {}

    def add(self, item):
        existing = self.items.get(item.product_size_id)
        if existing:
            existing.quantity += item.quantity
        else:
            self.items[item.product_size_id] = item

    def remove(self, product_size_id):
        self.items.pop(product_size_id, None)

    def reserved_quantity(self, product_size_id):
        item = self.items.get(product_size_id)
        if item:
            return item.quantity
        return 0

    def clear(self):
        self.items.clear()

    def is_empty(self):
        return not self.items

    def positions_count(self):
        return len(self.items)

    def total(self):
        return sum((item.line_total for item in self.items.values()), 0)


class Session:
    def __init__(self):
        self.user = None
        self.cart = Cart()
        # "orders" — заказ начат из списка заказов (Менеджер/Администратор), иначе из каталога.
        self.order_origin = "catalog"

    def login(self, user):
        self.user = user
        self.cart.clear()
        self.order_origin = "catalog"

    def logout(self):
        self.user = None
        self.cart.clear()

    @property
    def is_authorized(self):
        return self.user is not None

    @property
    def role(self):
        if self.user:
            return self.user["role_name"]
        return None

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN

    @property
    def is_staff(self):
        return self.role in (ROLE_ADMIN, ROLE_MANAGER)

    @property
    def full_name(self):
        if self.user:
            return self.user["full_name"]
        return "Гость"


session = Session()

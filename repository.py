"""Запросы к БД, которые нужны интерфейсу."""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from db import fetch_all, fetch_one, open_connection
from pricing import calc_discount_percent, calc_discounted_price, previous_month_range
from session import ROLE_CLIENT


class NotEnoughStockError(Exception):
    pass


@dataclass
class Product:
    product_id: int
    article: str
    name: str
    category: str
    manufacturer: str
    price: Decimal
    composition: str
    description: str
    photo: str
    total_quantity: int
    discount_percent: int
    final_price: Decimal


def find_user_by_login(login):
    return fetch_one(
        """
        SELECT u.user_id, u.login, r.role_name,
               concat_ws(' ', u.last_name, u.first_name, u.patronymic) AS full_name
        FROM app_user u
        JOIN role r ON r.role_id = u.role_id
        WHERE u.login = %s
        """,
        (login,),
    )


def load_clients():
    return fetch_all(
        """
        SELECT u.user_id, concat_ws(' ', u.last_name, u.first_name, u.patronymic) AS full_name
        FROM app_user u
        JOIN role r ON r.role_id = u.role_id
        WHERE r.role_name = %s
        ORDER BY full_name
        """,
        (ROLE_CLIENT,),
    )


def load_categories():
    rows = fetch_all("SELECT category_name FROM category ORDER BY category_name")
    return [row["category_name"] for row in rows]


def load_products(calc_date=None):
    calc_date = calc_date or date.today()
    period_start, period_end = previous_month_range(calc_date)
    rows = fetch_all(
        """
        SELECT p.product_id, p.article, p.product_name, p.price, p.composition, p.description, p.photo,
               c.category_name, m.manufacturer_name,
               COALESCE((SELECT SUM(ps.quantity) FROM product_size ps
                         WHERE ps.product_id = p.product_id), 0) AS total_quantity,
               EXISTS (SELECT 1
                       FROM order_item oi
                       JOIN product_size ps ON ps.product_size_id = oi.product_size_id
                       JOIN customer_order o ON o.order_id = oi.order_id
                       WHERE ps.product_id = p.product_id
                         AND o.order_date >= %(period_start)s
                         AND o.order_date < %(period_end)s) AS has_previous_month_orders
        FROM product p
        JOIN category c ON c.category_id = p.category_id
        JOIN manufacturer m ON m.manufacturer_id = p.manufacturer_id
        ORDER BY p.product_name
        """,
        {"period_start": period_start, "period_end": period_end},
    )
    products = []
    for row in rows:
        discount_percent = calc_discount_percent(row["has_previous_month_orders"])
        products.append(Product(
            product_id=row["product_id"],
            article=row["article"],
            name=row["product_name"],
            category=row["category_name"],
            manufacturer=row["manufacturer_name"],
            price=row["price"],
            composition=row["composition"] or "",
            description=row["description"] or "",
            photo=row["photo"],
            total_quantity=int(row["total_quantity"]),
            discount_percent=discount_percent,
            final_price=calc_discounted_price(row["price"], discount_percent),
        ))
    return products


def load_product_sizes(product_id):
    return fetch_all(
        """
        SELECT ps.product_size_id, s.size_value, ps.quantity
        FROM product_size ps
        JOIN shoe_size s ON s.size_id = ps.size_id
        WHERE ps.product_id = %s
        ORDER BY s.size_value
        """,
        (product_id,),
    )


def create_order(user_id, cart_items):
    """Списывает остатки и сохраняет заказ одной транзакцией. Возвращает номер заказа."""
    with open_connection() as connection:
        with connection.cursor() as cursor:
            for item in cart_items:
                # Условие quantity >= %s не даёт уйти в минус, если товар успели купить с другого места.
                cursor.execute(
                    """
                    UPDATE product_size SET quantity = quantity - %s
                    WHERE product_size_id = %s AND quantity >= %s
                    """,
                    (item.quantity, item.product_size_id, item.quantity),
                )
                if cursor.rowcount == 0:
                    raise NotEnoughStockError(
                        f"«{item.product_name}», размер {item.size_value}: "
                        f"на складе уже нет {item.quantity} пар."
                    )
            cursor.execute(
                "INSERT INTO customer_order (user_id, order_date) VALUES (%s, CURRENT_DATE) RETURNING order_id",
                (user_id,),
            )
            order_id = cursor.fetchone()[0]
            for item in cart_items:
                cursor.execute(
                    """
                    INSERT INTO order_item (order_id, product_size_id, quantity, unit_price)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (order_id, item.product_size_id, item.quantity, item.unit_price),
                )
    return order_id


def load_orders():
    return fetch_all(
        """
        SELECT o.order_id, o.order_date,
               concat_ws(' ', u.last_name, u.first_name, u.patronymic) AS client_name,
               COUNT(oi.order_item_id) AS positions_count,
               COALESCE(SUM(oi.quantity * oi.unit_price), 0) AS total
        FROM customer_order o
        JOIN app_user u ON u.user_id = o.user_id
        LEFT JOIN order_item oi ON oi.order_id = o.order_id
        GROUP BY o.order_id, u.user_id
        ORDER BY o.order_date DESC, o.order_id DESC
        """
    )


def load_order(order_id):
    return fetch_one(
        """
        SELECT o.order_id, o.order_date,
               concat_ws(' ', u.last_name, u.first_name, u.patronymic) AS client_name
        FROM customer_order o
        JOIN app_user u ON u.user_id = o.user_id
        WHERE o.order_id = %s
        """,
        (order_id,),
    )


def load_order_items(order_id):
    return fetch_all(
        """
        SELECT oi.order_item_id, p.product_name, m.manufacturer_name, s.size_value,
               oi.quantity, oi.unit_price, oi.quantity * oi.unit_price AS line_total
        FROM order_item oi
        JOIN product_size ps ON ps.product_size_id = oi.product_size_id
        JOIN product p ON p.product_id = ps.product_id
        JOIN manufacturer m ON m.manufacturer_id = p.manufacturer_id
        JOIN shoe_size s ON s.size_id = ps.size_id
        WHERE oi.order_id = %s
        ORDER BY p.product_name, s.size_value
        """,
        (order_id,),
    )


def _return_items_to_stock(cursor, order_id, order_item_ids=None):
    sql = """
        UPDATE product_size ps SET quantity = ps.quantity + oi.quantity
        FROM order_item oi
        WHERE oi.product_size_id = ps.product_size_id AND oi.order_id = %s
    """
    params = [order_id]
    if order_item_ids is not None:
        sql += " AND oi.order_item_id = ANY(%s)"
        params.append(list(order_item_ids))
    cursor.execute(sql, params)


def delete_order(order_id):
    with open_connection() as connection:
        with connection.cursor() as cursor:
            _return_items_to_stock(cursor, order_id)
            cursor.execute("DELETE FROM customer_order WHERE order_id = %s", (order_id,))


def update_order(order_id, order_date, removed_item_ids):
    with open_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE customer_order SET order_date = %s WHERE order_id = %s",
                (order_date, order_id),
            )
            if removed_item_ids:
                _return_items_to_stock(cursor, order_id, removed_item_ids)
                cursor.execute(
                    "DELETE FROM order_item WHERE order_id = %s AND order_item_id = ANY(%s)",
                    (order_id, list(removed_item_ids)),
                )

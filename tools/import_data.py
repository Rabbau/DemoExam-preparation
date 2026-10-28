"""Импорт товаров из CSV заказчика (пример, который подгоняется под реальный файл на экзамене).

Excel-файл заранее сохраняется как «CSV UTF-8 (разделитель — точка с запятой)».
Ожидаемые столбцы: Артикул;Наименование;Категория;Производитель;Цена;Состав;Описание;Фото;Остатки
Остатки — пары «размер:количество» через запятую, например «38:2, 39:4».

Запуск: python tools/import_data.py database/import_sample/products.csv
"""
import csv
import os
import sys
from datetime import datetime
from decimal import Decimal

# Скрипт лежит в tools/, а db.py — в корне проекта.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import open_connection

DATE_FORMATS = ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%d.%m.%y")


def clean_text(value):
    return " ".join((value or "").split())


def parse_price(value):
    return Decimal(clean_text(value).replace(" ", "").replace(",", ".").replace("₽", "").replace("руб.", ""))


def parse_date(value):
    text = clean_text(value)
    for date_format in DATE_FORMATS:
        try:
            return datetime.strptime(text, date_format).date()
        except ValueError:
            continue
    raise ValueError(f"Неизвестный формат даты: «{value}»")


def split_full_name(full_name):
    """«Иванов Иван Иванович» → ("Иванов", "Иван", "Иванович"); отчества может не быть."""
    parts = clean_text(full_name).split(" ")
    last_name = parts[0]
    first_name = parts[1] if len(parts) > 1 else ""
    patronymic = " ".join(parts[2:]) or None
    return last_name, first_name, patronymic


def parse_stock(value):
    stock = []
    for pair in clean_text(value).split(","):
        if not pair.strip():
            continue
        size_text, quantity_text = pair.split(":")
        stock.append((Decimal(size_text.strip().replace(",", ".")), int(quantity_text)))
    return stock


def get_or_create(cursor, table, id_column, name_column, value):
    cursor.execute(f"SELECT {id_column} FROM {table} WHERE {name_column} = %s", (value,))
    row = cursor.fetchone()
    if row:
        return row[0]
    cursor.execute(f"INSERT INTO {table} ({name_column}) VALUES (%s) RETURNING {id_column}", (value,))
    return cursor.fetchone()[0]


def import_products(csv_path):
    with open(csv_path, encoding="utf-8-sig", newline="") as csv_file:
        rows = list(csv.DictReader(csv_file, delimiter=";"))

    with open_connection() as connection:
        with connection.cursor() as cursor:
            for row in rows:
                category_id = get_or_create(cursor, "category", "category_id", "category_name",
                                            clean_text(row["Категория"]))
                manufacturer_id = get_or_create(cursor, "manufacturer", "manufacturer_id", "manufacturer_name",
                                                clean_text(row["Производитель"]))
                cursor.execute(
                    """
                    INSERT INTO product (article, product_name, category_id, manufacturer_id, price,
                                         composition, description, photo)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (article) DO UPDATE SET
                        product_name = EXCLUDED.product_name, category_id = EXCLUDED.category_id,
                        manufacturer_id = EXCLUDED.manufacturer_id, price = EXCLUDED.price,
                        composition = EXCLUDED.composition, description = EXCLUDED.description,
                        photo = EXCLUDED.photo
                    RETURNING product_id
                    """,
                    (
                        clean_text(row["Артикул"]),
                        clean_text(row["Наименование"]),
                        category_id,
                        manufacturer_id,
                        parse_price(row["Цена"]),
                        clean_text(row["Состав"]) or None,
                        clean_text(row["Описание"]) or None,
                        clean_text(row["Фото"]) or None,
                    ),
                )
                product_id = cursor.fetchone()[0]
                for size_value, quantity in parse_stock(row["Остатки"]):
                    size_id = get_or_create(cursor, "shoe_size", "size_id", "size_value", size_value)
                    cursor.execute(
                        """
                        INSERT INTO product_size (product_id, size_id, quantity) VALUES (%s, %s, %s)
                        ON CONFLICT (product_id, size_id) DO UPDATE SET quantity = EXCLUDED.quantity
                        """,
                        (product_id, size_id, quantity),
                    )
    print(f"Импортировано товаров: {len(rows)}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python tools/import_data.py путь/к/файлу.csv")
        sys.exit(1)
    import_products(sys.argv[1])

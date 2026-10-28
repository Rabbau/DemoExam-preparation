"""Алгоритм расчёта цены со скидкой и правила отображения остатков."""
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal

DISCOUNT_PERCENT = 25
MANY_STOCK_THRESHOLD = 5
LOW_STOCK_THRESHOLD = 3


def previous_month_range(calc_date):
    """Границы предыдущего календарного месяца: [начало, конец), конец не включается."""
    current_month_start = calc_date.replace(day=1)
    previous_month_start = (current_month_start - timedelta(days=1)).replace(day=1)
    return previous_month_start, current_month_start


def calc_discount_percent(has_orders_in_previous_month):
    if has_orders_in_previous_month:
        return 0
    return DISCOUNT_PERCENT


def calc_discounted_price(price, discount_percent):
    price = Decimal(price)
    discounted = price * (100 - discount_percent) / 100
    return discounted.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def stock_label(total_quantity):
    if total_quantity > MANY_STOCK_THRESHOLD:
        return "много"
    return "мало"


def is_low_stock(total_quantity):
    return total_quantity <= LOW_STOCK_THRESHOLD


def format_money(value):
    return f"{Decimal(value):,.2f}".replace(",", " ") + " ₽"


def format_size(size_value):
    return f"{float(size_value):g}"

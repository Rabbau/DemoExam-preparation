"""Модульные тесты алгоритма скидки и правил остатков. Запуск: python -m pytest"""
import os
import sys
from datetime import date
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pricing import (calc_discount_percent, calc_discounted_price, format_money, format_size, is_low_stock,
                     previous_month_range, stock_label)


def test_previous_month_range_middle_of_year():
    assert previous_month_range(date(2027, 6, 15)) == (date(2027, 5, 1), date(2027, 6, 1))


def test_previous_month_range_january_goes_to_previous_year():
    assert previous_month_range(date(2027, 1, 10)) == (date(2026, 12, 1), date(2027, 1, 1))


def test_previous_month_range_on_first_and_last_day():
    assert previous_month_range(date(2027, 3, 1)) == (date(2027, 2, 1), date(2027, 3, 1))
    assert previous_month_range(date(2027, 3, 31)) == (date(2027, 2, 1), date(2027, 3, 1))


def test_discount_only_without_previous_month_orders():
    assert calc_discount_percent(has_orders_in_previous_month=False) == 25
    assert calc_discount_percent(has_orders_in_previous_month=True) == 0


def test_discounted_price_is_rounded_to_kopecks():
    assert calc_discounted_price(Decimal("5490.00"), 25) == Decimal("4117.50")
    assert calc_discounted_price(Decimal("999.99"), 25) == Decimal("749.99")
    assert calc_discounted_price(Decimal("1000"), 0) == Decimal("1000.00")


def test_stock_label_threshold_is_five():
    assert stock_label(6) == "много"
    assert stock_label(5) == "мало"
    assert stock_label(0) == "мало"


def test_low_stock_threshold_is_three():
    assert is_low_stock(3)
    assert is_low_stock(0)
    assert not is_low_stock(4)


def test_formatting():
    assert format_money(Decimal("4117.5")) == "4 117.50 ₽"
    assert format_size(Decimal("40.0")) == "40"
    assert format_size(Decimal("40.5")) == "40.5"

import os
import sys
from datetime import date
from decimal import Decimal

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tools"))

from import_data import clean_text, parse_date, parse_price, parse_stock, split_full_name


def test_clean_text_collapses_spaces():
    assert clean_text("  Слипоны   «Лето» ") == "Слипоны «Лето»"


def test_parse_price_accepts_spaces_commas_and_currency():
    assert parse_price("1 890,00") == Decimal("1890.00")
    assert parse_price("7 450,00 ₽") == Decimal("7450.00")


def test_parse_date_supports_several_formats():
    assert parse_date("05.03.2027") == date(2027, 3, 5)
    assert parse_date("2027-03-05") == date(2027, 3, 5)


def test_split_full_name_without_patronymic():
    assert split_full_name("Широкова Елена") == ("Широкова", "Елена", None)
    assert split_full_name("Орлов  Денис Игоревич") == ("Орлов", "Денис", "Игоревич")


def test_parse_stock():
    assert parse_stock("37:2, 38:3") == [(Decimal("37"), 2), (Decimal("38"), 3)]

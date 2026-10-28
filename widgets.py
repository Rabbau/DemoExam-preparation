"""Общие виджеты: кнопки, таблицы, загрузка картинок с заглушкой и карточка товара в каталоге."""
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import (QAbstractItemView, QFrame, QHBoxLayout, QHeaderView, QLabel, QPushButton,
                             QTableWidgetItem, QVBoxLayout)

from app_paths import resource_path
from pricing import format_money, is_low_stock, stock_label

PLACEHOLDER_IMAGE = "picture.png"


def make_button(text, kind="primary"):
    """kind: primary — основное действие, secondary — второстепенное, danger — удаление."""
    button = QPushButton(text)
    button.setProperty("kind", kind)
    button.setCursor(Qt.PointingHandCursor)
    return button


def muted_label(text=""):
    label = QLabel(text)
    label.setProperty("muted", True)
    return label


def configure_table(table, stretch_column):
    table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    table.setSelectionBehavior(QAbstractItemView.SelectRows)
    table.setSelectionMode(QAbstractItemView.SingleSelection)
    table.setAlternatingRowColors(True)
    table.setShowGrid(False)
    table.setFocusPolicy(Qt.NoFocus)
    table.verticalHeader().setVisible(False)
    table.verticalHeader().setDefaultSectionSize(38)
    table.horizontalHeader().setHighlightSections(False)
    table.horizontalHeader().setDefaultAlignment(Qt.AlignLeft | Qt.AlignVCenter)
    table.stretch_column = stretch_column


def table_item(text, numeric=False):
    item = QTableWidgetItem(text)
    if numeric:
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    return item


def fit_table_columns(table):
    table.resizeColumnsToContents()
    table.horizontalHeader().setSectionResizeMode(table.stretch_column, QHeaderView.Stretch)


def load_product_pixmap(photo, width, height):
    path = resource_path("products", photo) if photo else ""
    pixmap = QPixmap(path) if path and os.path.isfile(path) else QPixmap()
    if pixmap.isNull():
        pixmap = QPixmap(resource_path(PLACEHOLDER_IMAGE))
    return pixmap.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)


def make_price_block(product, alignment=Qt.AlignLeft):
    """Цена со скидкой; при скидке — зачёркнутая старая цена и плашка «−25%»."""
    layout = QVBoxLayout()
    layout.setSpacing(2)
    if product.discount_percent:
        old_layout = QHBoxLayout()
        old_layout.setSpacing(6)
        old_price_label = QLabel(format_money(product.price))
        old_price_label.setObjectName("oldPrice")
        font = old_price_label.font()
        font.setStrikeOut(True)
        old_price_label.setFont(font)
        badge = QLabel(f"−{product.discount_percent}%")
        badge.setObjectName("discountBadge")
        if alignment == Qt.AlignRight:
            old_layout.addStretch()
        old_layout.addWidget(old_price_label)
        old_layout.addWidget(badge)
        if alignment != Qt.AlignRight:
            old_layout.addStretch()
        layout.addLayout(old_layout)
    price_label = QLabel(format_money(product.final_price))
    price_label.setObjectName("price")
    price_label.setAlignment(alignment)
    layout.addWidget(price_label)
    return layout


def make_stock_badge(total_quantity):
    label = stock_label(total_quantity)
    badge = QLabel(f"В наличии: {label}")
    badge.setObjectName("stockBadge")
    badge.setProperty("level", "many" if label == "много" else "few")
    return badge


class ProductRow(QFrame):
    def __init__(self, product, parent=None):
        super().__init__(parent)
        self.setObjectName("productRow")
        self.setAttribute(Qt.WA_Hover, True)
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("lowStock", is_low_stock(product.total_quantity))

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 16, 12)
        layout.setSpacing(16)

        image_label = QLabel()
        image_label.setObjectName("productImage")
        image_label.setFixedSize(120, 120)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setPixmap(load_product_pixmap(product.photo, 110, 110))
        layout.addWidget(image_label)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        info_layout.addWidget(muted_label(product.category))
        name_label = QLabel(product.name)
        name_label.setObjectName("productName")
        info_layout.addWidget(name_label)
        info_layout.addWidget(QLabel(f"Производство: {product.manufacturer}"))
        composition_label = muted_label(f"Состав: {product.composition}")
        composition_label.setWordWrap(True)
        info_layout.addWidget(composition_label)
        info_layout.addStretch()
        layout.addLayout(info_layout, stretch=1)

        right_layout = QVBoxLayout()
        right_layout.setSpacing(8)
        right_layout.addLayout(make_price_block(product, Qt.AlignRight))
        right_layout.addStretch()
        right_layout.addWidget(make_stock_badge(product.total_quantity), alignment=Qt.AlignRight)
        layout.addLayout(right_layout)

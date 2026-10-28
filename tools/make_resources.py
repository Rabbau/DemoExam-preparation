"""Рисует заглушки ресурсов для тренировки (логотип, иконку, picture.png, фото товаров).

На экзамене ресурсы выдаются в Приложении 2 — просто положите их в папку resources.
Запуск: python tools/make_resources.py
"""
import os
import sys

from PyQt5.QtCore import QPointF, QRect, Qt
from PyQt5.QtGui import QColor, QFont, QGuiApplication, QImage, QPainter, QPen, QPolygonF

RESOURCES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources")


def draw_image(path, width, height, background, text, text_color="#000000", font_size=28):
    image = QImage(width, height, QImage.Format_ARGB32)
    image.fill(QColor(background))
    painter = QPainter(image)
    painter.setPen(QColor(text_color))
    painter.setRenderHint(QPainter.TextAntialiasing)
    painter.setFont(QFont("Segoe UI", font_size, QFont.Bold))
    painter.drawText(QRect(0, 0, width, height), Qt.AlignCenter | Qt.TextWordWrap, text)
    painter.end()
    image.save(path)


def draw_logo(path):
    image = QImage(240, 120, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setPen(Qt.NoPen)
    painter.setBrush(QColor("#1F8A5B"))
    painter.drawRoundedRect(QRect(8, 20, 80, 80), 18, 18)
    painter.setPen(QColor("#FFFFFF"))
    painter.setFont(QFont("Segoe UI", 34, QFont.Bold))
    painter.drawText(QRect(8, 20, 80, 80), Qt.AlignCenter, "О")
    painter.setPen(QColor("#1F2933"))
    painter.setFont(QFont("Segoe UI", 24, QFont.Bold))
    painter.drawText(QRect(100, 20, 140, 80), Qt.AlignVCenter | Qt.AlignLeft, "ОБУВЬ")
    painter.end()
    image.save(path)


def draw_chevron(path, pointing_down):
    """Стрелки для выпадающих списков и счётчиков (используются в style.py)."""
    image = QImage(24, 24, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    painter.setRenderHint(QPainter.Antialiasing)
    pen = QPen(QColor("#6B7280"), 2.6)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    painter.setPen(pen)
    if pointing_down:
        painter.drawPolyline(QPolygonF([QPointF(6, 9), QPointF(12, 15), QPointF(18, 9)]))
    else:
        painter.drawPolyline(QPolygonF([QPointF(6, 15), QPointF(12, 9), QPointF(18, 15)]))
    painter.end()
    image.save(path)


def main():
    app = QGuiApplication(sys.argv)
    products_dir = os.path.join(RESOURCES_DIR, "products")
    ui_dir = os.path.join(RESOURCES_DIR, "ui")
    os.makedirs(products_dir, exist_ok=True)
    os.makedirs(ui_dir, exist_ok=True)

    draw_chevron(os.path.join(ui_dir, "arrow_down.png"), pointing_down=True)
    draw_chevron(os.path.join(ui_dir, "arrow_up.png"), pointing_down=False)

    draw_logo(os.path.join(RESOURCES_DIR, "logo.png"))
    draw_image(os.path.join(RESOURCES_DIR, "icon.ico"), 64, 64, "#1F8A5B", "О", "#FFFFFF", font_size=36)
    draw_image(os.path.join(RESOURCES_DIR, "picture.png"), 300, 300, "#F5F6F7", "Нет фото", "#9AA3AD", font_size=20)
    draw_image(os.path.join(products_dir, "sh001.png"), 300, 300, "#CFE3F7", "Спринт", "#2D5B87")
    draw_image(os.path.join(products_dir, "sh002.png"), 300, 300, "#FBEBC4", "Метро", "#8A6416")
    draw_image(os.path.join(products_dir, "sh003.png"), 300, 300, "#E6DCD6", "Тайга", "#6B4F3F")
    app.quit()


if __name__ == "__main__":
    main()

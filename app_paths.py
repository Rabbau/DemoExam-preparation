"""Пути к файлам приложения: работают и при запуске из исходников, и из exe (PyInstaller)."""
import os
import sys

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
    BUNDLE_DIR = getattr(sys, "_MEIPASS", APP_DIR)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = APP_DIR

# config.ini лежит рядом с exe, чтобы строку подключения можно было поправить без пересборки.
CONFIG_PATH = os.path.join(APP_DIR, "config.ini")


def resource_path(*parts):
    return os.path.join(BUNDLE_DIR, "resources", *parts)

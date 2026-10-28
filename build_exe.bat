@echo off
rem Builds dist\ShoeShop\ShoeShop.exe and puts config.ini next to it.
.venv\Scripts\pyinstaller --noconfirm --windowed --name ShoeShop --icon resources\icon.ico --add-data "resources;resources" main.py
copy /Y config.ini dist\ShoeShop\config.ini

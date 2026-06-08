"""Скрипт для сборки exe из Python приложения через PyInstaller."""

import PyInstaller.__main__
import os
import sys

# Параметры сборки
output_name = "SteamAutoLauncher"
main_file = "main.py"

# Команда PyInstaller
PyInstaller.__main__.run([
    main_file,
    '--name', output_name,
    '--onefile',  # Один exe файл
    '--windowed',  # Без консоли
    '--icon=NONE',  # Иконка (опционально)
    '--add-data', 'config.json:.',
    '--collect-all', 'pywinauto',
    '--collect-all', 'keyboard',
    '--collect-all', 'pyperclip',
    '--collect-all', 'cryptography',
    '-y',  # Перезаписать без вопроса
])

print("\n✅ Сборка завершена!")
print(f"Exe находится в папке: dist/{output_name}.exe")

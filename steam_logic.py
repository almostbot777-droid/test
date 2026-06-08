"""Логика запуска Steam и игр с правильной работой UI."""

import os
import subprocess
import time
from pathlib import Path

from dialog_bypass import bypass_account_selector


def find_steam_exe(custom_path="") -> str:
    """Найти steam.exe в системе."""
    if custom_path and Path(custom_path).exists():
        return custom_path
    
    common_paths = [
        "C:/Program Files (x86)/Steam/steam.exe",
        "C:/Program Files/Steam/steam.exe",
        "D:/Steam/steam.exe",
        "E:/Steam/steam.exe",
    ]
    
    for path in common_paths:
        if Path(path).exists():
            return path
    
    # Попробовать через реестр (Windows)
    try:
        import winreg
        reg = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(reg, r"Software\Valve\Steam")
        steam_path, _ = winreg.QueryValueEx(key, "SteamPath")
        steam_exe = Path(steam_path) / "steam.exe"
        if steam_exe.exists():
            return str(steam_exe)
    except:
        pass
    
    raise FileNotFoundError("❌ steam.exe не найден. Укажите путь вручную.")


def kill_steam_processes():
    """Убить все процессы Steam."""
    try:
        subprocess.run(
            ["taskkill", "/F", "/IM", "steam.exe"],
            capture_output=True,
            timeout=5,
        )
        subprocess.run(
            ["taskkill", "/F", "/IM", "steamwebhelper.exe"],
            capture_output=True,
            timeout=5,
        )
    except:
        pass


def input_credentials(login: str, password: str, status_callback=None):
    """Вводит логин и пароль в Steam через буфер обмена и клавиатуру."""
    def log(msg):
        if status_callback:
            status_callback(msg)
        print(msg)
    
    try:
        import keyboard
        import pyperclip
        
        log(f"Фокусируем Steam окно и вводим логин...")
        time.sleep(1)
        
        # Копируем логин в буфер и вставляем
        pyperclip.copy(login)
        keyboard.send('ctrl+a')  # Выбрать всё
        time.sleep(0.3)
        keyboard.send('ctrl+v')  # Вставить логин
        time.sleep(0.5)
        keyboard.send('tab')     # Перейти на пароль
        time.sleep(0.3)
        
        # Копируем пароль и вставляем
        pyperclip.copy(password)
        keyboard.send('ctrl+v')  # Вставить пароль
        time.sleep(0.5)
        keyboard.send('tab')     # Перейти на Enter или код
        time.sleep(0.3)
        keyboard.send('enter')   # Нажимаем Enter
        
        log("✓ Учётные данные введены")
        return True
    except ImportError as e:
        log(f"❌ Библиотека не установлена: {e}")
        return False
    except Exception as e:
        log(f"❌ Ошибка ввода: {e}")
        return False


def launch_steam_only(
    login: str,
    password: str,
    steam_exe: str,
    delay_startup: int = 45,
    delay_hold: int = 15,
    delay_dialog: int = 3,
    status_callback=None,
) -> bool:
    """Запустить только Steam с автоматическим вводом уч��тных данных."""
    def log(msg):
        if status_callback:
            status_callback(msg)
        print(msg)
    
    try:
        log(f"\n[{login}] ===== ТОЛЬКО STEAM =====")
        
        # Закрыть старые процессы
        log(f"[{login}] Закрытие старых процессов...")
        kill_steam_processes()
        time.sleep(2)
        
        # Запустить Steam
        log(f"[{login}] 🚀 Запуск Steam...")
        subprocess.Popen(f'"{steam_exe}"')
        
        # Ждём загрузки
        log(f"[{login}] ⏳ Загрузка Steam ({delay_startup}с)...")
        time.sleep(delay_startup)
        
        # Пытаемся обойти диалог выбора аккаунта
        log(f"[{login}] Проверка диалога выбора аккаунта...")
        time.sleep(delay_dialog)
        bypass_account_selector(login, timeout=5, status_callback=log)
        
        # Вводим учётные данные
        log(f"[{login}] Ввод учётных данных...")
        time.sleep(1)
        input_credentials(login, password, status_callback=log)
        
        # Ждём авторизации
        log(f"[{login}] ⏳ Авторизация ({delay_hold}с)...")
        time.sleep(delay_hold)
        
        # Закрыть Steam
        log(f"[{login}] Закрытие Steam...")
        kill_steam_processes()
        time.sleep(1)
        
        log(f"[{login}] ✓ Завершено успешно")
        return True
    
    except Exception as e:
        log(f"[{login}] ❌ Ошибка: {e}")
        kill_steam_processes()
        return False


def launch_steam_with_game(
    login: str,
    password: str,
    steam_exe: str,
    app_id: str = "",
    game_exe: str = "",
    delay_startup: int = 45,
    delay_auth: int = 50,
    delay_game: int = 15,
    delay_dialog: int = 3,
    status_callback=None,
) -> bool:
    """Запустить Steam и игру с автоматическим вводом учётных данных."""
    def log(msg):
        if status_callback:
            status_callback(msg)
        print(msg)
    
    try:
        log(f"\n[{login}] ===== STEAM + ИГРА =====")
        
        # Закрыть старые процессы
        log(f"[{login}] Закрытие старых процессов...")
        kill_steam_processes()
        time.sleep(2)
        
        # Запустить Steam
        log(f"[{login}] 🚀 Запуск Steam...")
        subprocess.Popen(f'"{steam_exe}"')
        
        # Ждём загрузки
        log(f"[{login}] ⏳ Загрузка Steam ({delay_startup}с)...")
        time.sleep(delay_startup)
        
        # Пытаемся обойти диалог выбора аккаунта
        log(f"[{login}] Проверка диалога выбора аккаунта...")
        time.sleep(delay_dialog)
        bypass_account_selector(login, timeout=5, status_callback=log)
        
        # Вводим учётные данные
        log(f"[{login}] Ввод учётных данных...")
        time.sleep(1)
        input_credentials(login, password, status_callback=log)
        
        # Ждём авторизации
        log(f"[{login}] ⏳ Авторизация Steam ({delay_auth}с)...")
        time.sleep(delay_auth)
        
        # Запускаем игру
        if game_exe and Path(game_exe).exists():
            log(f"[{login}] 🎮 Запуск игры (exe): {Path(game_exe).name}")
            subprocess.Popen(f'"{game_exe}"')
        elif app_id:
            log(f"[{login}] 🎮 Запуск игры (App ID): {app_id}")
            subprocess.Popen(f"steam://run/{app_id}")
        else:
            log(f"[{login}] ⚠️  App ID и путь к игре не указаны")
        
        # Ждём в игре
        log(f"[{login}] ⏳ Время в игре ({delay_game}с)...")
        time.sleep(delay_game)
        
        # Закрыть Steam
        log(f"[{login}] Закрытие Steam...")
        kill_steam_processes()
        time.sleep(1)
        
        log(f"[{login}] ✓ Завершено успешно")
        return True
    
    except Exception as e:
        log(f"[{login}] ❌ Ошибка: {e}")
        kill_steam_processes()
        return False

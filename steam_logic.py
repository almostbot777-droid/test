"""Логика запуска Steam и игр."""

import os
import subprocess
import time
from pathlib import Path

from config import get_account_password
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


def launch_steam_only(
    login: str,
    password: str,
    steam_exe: str,
    delay_startup: int = 15,
    delay_hold: int = 10,
    delay_dialog: int = 3,
    status_callback=None,
) -> bool:
    """Запустить только Steam.
    
    Args:
        login: Steam логин
        password: Steam пароль (не зашифрованный)
        steam_exe: путь к steam.exe
        delay_startup: задержка после запуска Steam (для загрузки)
        delay_hold: как долго держать Steam открытым
        delay_dialog: задержка перед попыткой обхода диалога
        status_callback: функция для вывода статуса
    """
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
        
        # Пробуем обойти диалог
        log(f"[{login}] Попытка обхода диалога...")
        time.sleep(delay_dialog)
        bypass_account_selector(login, timeout=5, status_callback=log)
        
        # Вводим логин/пароль
        log(f"[{login}] Ввод учётных данных...")
        time.sleep(1)
        subprocess.Popen(f'"{steam_exe}" -login {login} {password}', shell=True)
        
        # Держим Steam открытым
        log(f"[{login}] ✓ Steam запущен, держим {delay_hold}с...")
        time.sleep(delay_hold)
        
        # Закрываем
        log(f"[{login}] Закрытие Steam...")
        kill_steam_processes()
        time.sleep(1)
        
        log(f"[{login}] ✓ Завершено успешно")
        return True
    
    except Exception as e:
        log(f"[{login}] ❌ Ошибка: {e}")
        return False


def launch_steam_with_game(
    login: str,
    password: str,
    steam_exe: str,
    app_id: str = "",
    game_exe: str = "",
    delay_startup: int = 15,
    delay_auth: int = 40,
    delay_game: int = 10,
    delay_dialog: int = 3,
    status_callback=None,
) -> bool:
    """Запустить Steam и игру.
    
    Args:
        login: Steam логин
        password: Steam пароль
        steam_exe: путь к steam.exe
        app_id: App ID игры (если нет game_exe)
        game_exe: путь к exe файлу игры
        delay_startup: задержка после запуска Steam
        delay_auth: задержка авторизации
        delay_game: как долго держать игру открытой
        delay_dialog: задержка перед обходом диалога
        status_callback: функция для вывода статуса
    """
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
        
        # Пробуем обойти диалог
        log(f"[{login}] Попытка обхода диалога...")
        time.sleep(delay_dialog)
        bypass_account_selector(login, timeout=5, status_callback=log)
        
        # Вводим логин/пароль
        log(f"[{login}] Ввод учётных данных...")
        time.sleep(1)
        subprocess.Popen(f'"{steam_exe}" -login {login} {password}', shell=True)
        
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
            log(f"[{login}] ⚠ App ID и путь к игре не указаны")
        
        # Держим игру открытой
        log(f"[{login}] ✓ Игра запущена, ждём {delay_game}с...")
        time.sleep(delay_game)
        
        # Закрываем
        log(f"[{login}] Закрытие Steam...")
        kill_steam_processes()
        time.sleep(1)
        
        log(f"[{login}] ✓ Завершено успешно")
        return True
    
    except Exception as e:
        log(f"[{login}] ❌ Ошибка: {e}")
        return False

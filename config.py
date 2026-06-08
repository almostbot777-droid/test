"""Управление конфигом и шифрованием паролей."""

import json
from pathlib import Path
from cryptography.fernet import Fernet

CONFIG_FILE = Path("config.json")
KEY_FILE = Path(".steam_key")


def get_or_create_key():
    """Получить или создать ключ шифрования."""
    if KEY_FILE.exists():
        return KEY_FILE.read_bytes()
    
    key = Fernet.generate_key()
    KEY_FILE.write_bytes(key)
    # На Windows это не работает, но хотя бы выглядит красиво
    try:
        KEY_FILE.chmod(0o600)
    except:
        pass
    
    return key


def get_cipher():
    """Получить Fernet cipher для шифрования."""
    key = get_or_create_key()
    return Fernet(key)


def encrypt_password(password: str) -> str:
    """Зашифровать пароль."""
    cipher = get_cipher()
    return cipher.encrypt(password.encode()).decode()


def decrypt_password(encrypted: str) -> str:
    """Расшифровать пароль."""
    cipher = get_cipher()
    try:
        return cipher.decrypt(encrypted.encode()).decode()
    except:
        return ""


def load_config():
    """Загрузить конфиг из файла."""
    if not CONFIG_FILE.exists():
        return {"accounts": [], "settings": {}}
    
    try:
        return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except:
        return {"accounts": [], "settings": {}}


def save_config(config: dict):
    """Сохранить конфиг в файл."""
    CONFIG_FILE.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def add_account(label: str, login: str, password: str) -> dict:
    """Добавить новый аккаунт."""
    encrypted_pwd = encrypt_password(password)
    return {
        "label": label,
        "login": login,
        "password": encrypted_pwd
    }


def get_account_password(account: dict) -> str:
    """Получить расшифрованный пароль аккаунта."""
    return decrypt_password(account.get("password", ""))

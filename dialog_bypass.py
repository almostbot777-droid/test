"""Обход диалога 'Кто играет?' с надёжной логикой."""

import time


def bypass_account_selector(login: str, timeout: int = 10, status_callback=None) -> bool:
    """Обойти диалог 'Кто играет?' через pywinauto.
    
    Args:
        login: Steam логин (для логирования)
        timeout: максимальное время ожидания диалога
        status_callback: функция для вывода статуса
    
    Returns:
        True если диалог обойден, False если не найден
    """
    def log(msg):
        if status_callback:
            status_callback(msg)
        print(msg)
    
    try:
        from pywinauto import Desktop
        from pywinauto.timings import Timings
        
        log(f"[{login}] 🔍 Поиск диалога 'Кто играет?'...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                desktop = Desktop()
                
                # Ищем все окна Steam
                for window in desktop.windows():
                    try:
                        title = window.window_text()
                        
                        # Проверяем название окна
                        if any(x in title.lower() for x in ['who is playing', 'кто играет', 'steam', 'select account']):
                            log(f"[{login}] ✓ Найдено окно: {title}")
                            
                            # Пытаемся найти и нажать кнопку
                            try:
                                buttons = window.descendants(control_type="Button")
                                
                                if buttons:
                                    log(f"[{login}] Found {len(buttons)} button(s), clicking first visible...")
                                    
                                    clicked = False
                                    for btn in buttons:
                                        try:
                                            is_visible = True
                                            try:
                                                is_visible = btn.is_visible()
                                            except:
                                                pass
                                            
                                            if is_visible:
                                                btn_text = ""
                                                try:
                                                    btn_text = btn.window_text()
                                                except:
                                                    pass
                                                
                                                log(f"[{login}] Clicking button: {btn_text}")
                                                btn.click()
                                                time.sleep(0.5)
                                                clicked = True
                                                break
                                        except Exception as e:
                                            continue
                                    
                                    if clicked:
                                        log(f"[{login}] ✓ Диалог успешно обойден")
                                        return True
                                else:
                                    # Если нет кнопок, пробуем Enter
                                    log(f"[{login}] Buttons not found, trying ENTER...")
                                    try:
                                        window.send_keys('{ENTER}')
                                        time.sleep(0.5)
                                        log(f"[{login}] ✓ Диалог закрыт (Enter)")
                                        return True
                                    except:
                                        pass
                            except Exception as e:
                                log(f"[{login}] Button search error: {e}")
                                try:
                                    window.send_keys('{ENTER}')
                                    time.sleep(0.5)
                                    return True
                                except:
                                    pass
                    except:
                        continue
                
                time.sleep(0.5)
            except Exception as e:
                log(f"[{login}] Desktop scan error: {e}")
                time.sleep(0.5)
        
        log(f"[{login}] ⚠ Диалог не найден за {timeout}с")
        return False
    
    except ImportError:
        log(f"[{login}] ❌ pywinauto не установлен. Pip install -r requirements.txt")
        return False
    except Exception as e:
        log(f"[{login}] ❌ Ошибка при обходе диалога: {e}")
        return False

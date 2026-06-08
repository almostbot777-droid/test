"""GUI приложение для запуска Steam и игр."""

import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk, scrolledtext

from config import load_config, save_config, add_account, get_account_password
from steam_logic import find_steam_exe, launch_steam_only, launch_steam_with_game, kill_steam_processes


class SteamLauncherApp:
    def __init__(self, root):
        self.root = root
        root.title("🎮 Steam Auto Launcher")
        root.geometry("1000x700")
        root.resizable(True, True)
        
        self.config = load_config()
        self.running = False
        self.account_vars = {}
        
        self._build_ui()
        self._load_accounts()
    
    def _build_ui(self):
        """Построить интерфейс."""
        # Ноутбук (вкладки)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Вкладка 1: Аккаунты
        accounts_frame = ttk.Frame(notebook)
        notebook.add(accounts_frame, text="📋 Аккаунты")
        self._build_accounts_tab(accounts_frame)
        
        # Вкладка 2: Настройки
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="⚙️ Настройки")
        self._build_settings_tab(settings_frame)
        
        # Вкладка 3: Логи
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="📝 Логи")
        self._build_logs_tab(logs_frame)
    
    def _build_accounts_tab(self, parent):
        """Вкладка с аккаунтами."""
        main = ttk.Frame(parent, padding=10)
        main.pack(fill="both", expand=True)
        
        # Кнопки
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(btn_frame, text="✅ Выбрать все", command=self._select_all).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="❌ Снять все", command=self._deselect_all).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="➕ Добавить", command=self._add_account).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑️ Удалить", command=self._delete_account).pack(side="left", padx=5)
        
        # Список аккаунтов
        scroll_frame = ttk.Frame(main)
        scroll_frame.pack(fill="both", expand=True)
        
        scrollbar = ttk.Scrollbar(scroll_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.accounts_canvas = tk.Canvas(scroll_frame, yscrollcommand=scrollbar.set, bg="white", highlightthickness=0)
        scrollbar.config(command=self.accounts_canvas.yview)
        self.accounts_canvas.pack(side="left", fill="both", expand=True)
        
        self.accounts_inner = ttk.Frame(self.accounts_canvas)
        self.canvas_window = self.accounts_canvas.create_window(0, 0, window=self.accounts_inner, anchor="nw")
        self.accounts_canvas.bind(
            "<Configure>",
            lambda e: self.accounts_canvas.itemconfig(self.canvas_window, width=e.width)
        )
    
    def _build_settings_tab(self, parent):
        """Вкладка с настройками."""
        main = ttk.Frame(parent, padding=20)
        main.pack(fill="both", expand=True)
        
        # Путь к Steam
        ttk.Label(main, text="Путь к steam.exe:").grid(row=0, column=0, sticky="w", pady=10)
        self.steam_path_var = tk.StringVar(value=self.config.get("settings", {}).get("steam_exe_path", ""))
        ttk.Entry(main, textvariable=self.steam_path_var, width=50).grid(row=0, column=1, sticky="ew", padx=10)
        ttk.Button(main, text="...", command=self._browse_steam, width=3).grid(row=0, column=2)
        
        # App ID игры
        ttk.Label(main, text="App ID игры:").grid(row=1, column=0, sticky="w", pady=10)
        self.app_id_var = tk.StringVar(value=self.config.get("settings", {}).get("game_app_id", "420980"))
        ttk.Entry(main, textvariable=self.app_id_var, width=50).grid(row=1, column=1, sticky="ew", padx=10)
        
        # Путь к exe игры
        ttk.Label(main, text="Путь к exe игры:").grid(row=2, column=0, sticky="w", pady=10)
        self.game_exe_var = tk.StringVar(value=self.config.get("settings", {}).get("game_exe_path", ""))
        ttk.Entry(main, textvariable=self.game_exe_var, width=50).grid(row=2, column=1, sticky="ew", padx=10)
        ttk.Button(main, text="...", command=self._browse_game, width=3).grid(row=2, column=2)
        
        # Задержки
        ttk.Label(main, text="Загрузка Steam (сек):").grid(row=3, column=0, sticky="w", pady=10)
        self.delay_startup_var = tk.StringVar(value=str(self.config.get("settings", {}).get("delay_startup", 15)))
        ttk.Entry(main, textvariable=self.delay_startup_var, width=50).grid(row=3, column=1, sticky="ew", padx=10)
        
        ttk.Label(main, text="Авторизация (сек):").grid(row=4, column=0, sticky="w", pady=10)
        self.delay_auth_var = tk.StringVar(value=str(self.config.get("settings", {}).get("delay_auth", 40)))
        ttk.Entry(main, textvariable=self.delay_auth_var, width=50).grid(row=4, column=1, sticky="ew", padx=10)
        
        ttk.Label(main, text="Время в игре (сек):").grid(row=5, column=0, sticky="w", pady=10)
        self.delay_game_var = tk.StringVar(value=str(self.config.get("settings", {}).get("delay_game", 10)))
        ttk.Entry(main, textvariable=self.delay_game_var, width=50).grid(row=5, column=1, sticky="ew", padx=10)
        
        ttk.Label(main, text="Обход диалога (сек):").grid(row=6, column=0, sticky="w", pady=10)
        self.delay_dialog_var = tk.StringVar(value=str(self.config.get("settings", {}).get("delay_dialog", 3)))
        ttk.Entry(main, textvariable=self.delay_dialog_var, width=50).grid(row=6, column=1, sticky="ew", padx=10)
        
        # Кнопка сохранения
        ttk.Button(main, text="💾 Сохранить настройки", command=self._save_settings).grid(row=7, column=0, columnspan=3, pady=20)
        
        main.columnconfigure(1, weight=1)
    
    def _build_logs_tab(self, parent):
        """Вкладка с логами."""
        main = ttk.Frame(parent, padding=10)
        main.pack(fill="both", expand=True)
        
        # Кнопки управления
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x", pady=(0, 10))
        
        self.start_btn = ttk.Button(btn_frame, text="▶ Только Steam", command=self._start_steam_only)
        self.start_btn.pack(side="left", padx=5)
        
        self.start_game_btn = ttk.Button(btn_frame, text="▶ Steam + Игра", command=self._start_steam_with_game)
        self.start_game_btn.pack(side="left", padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="⏹ Стоп", command=self._stop, state="disabled")
        self.stop_btn.pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="🗑️ Очистить логи", command=self._clear_logs).pack(side="left", padx=5)
        
        # Логи
        self.log_text = scrolledtext.ScrolledText(main, height=25, width=80, state="disabled")
        self.log_text.pack(fill="both", expand=True)
    
    def _load_accounts(self):
        """Загрузить аккаунты в список."""
        for widget in self.accounts_inner.winfo_children():
            widget.destroy()
        
        self.account_vars = {}
        for acc in self.config.get("accounts", []):
            var = tk.BooleanVar(value=False)
            self.account_vars[acc["login"]] = var
            
            frame = ttk.Frame(self.accounts_inner, relief="solid", borderwidth=1)
            frame.pack(fill="x", padx=5, pady=3)
            
            ttk.Checkbutton(frame, text=f"{acc['label']}", variable=var).pack(side="left", padx=5, pady=5)
            ttk.Label(frame, text=f"({acc['login']})", foreground="gray").pack(side="left", padx=5)
        
        self.accounts_canvas.configure(scrollregion=self.accounts_canvas.bbox("all"))
    
    def _log(self, msg):
        """Вывести сообщение в логи."""
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
        print(msg)
    
    def _select_all(self):
        for var in self.account_vars.values():
            var.set(True)
    
    def _deselect_all(self):
        for var in self.account_vars.values():
            var.set(False)
    
    def _browse_steam(self):
        path = filedialog.askopenfilename(title="Выбери steam.exe", filetypes=[("Exe", "*.exe")])
        if path:
            self.steam_path_var.set(path)
    
    def _browse_game(self):
        path = filedialog.askopenfilename(title="Выбери exe игры", filetypes=[("Exe", "*.exe")])
        if path:
            self.game_exe_var.set(path)
    
    def _add_account(self):
        dialog = AccountDialog(self.root, on_save=self._on_account_added)
    
    def _delete_account(self):
        selected = [login for login, var in self.account_vars.items() if var.get()]
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Выбери аккаунт для удаления")
            return
        
        if messagebox.askyesno("🗑️ Удалить", f"Удалить {len(selected)} аккаунт(о)в?"):
            self.config["accounts"] = [
                acc for acc in self.config["accounts"]
                if acc["login"] not in selected
            ]
            save_config(self.config)
            self._load_accounts()
            self._log(f"✓ Удалено {len(selected)} аккаунт(о)в")
    
    def _on_account_added(self, account_data):
        self.config.setdefault("accounts", []).append(account_data)
        save_config(self.config)
        self._load_accounts()
        self._log(f"✓ Добавлен аккаунт: {account_data['label']}")
    
    def _save_settings(self):
        try:
            delay_startup = int(self.delay_startup_var.get())
            delay_auth = int(self.delay_auth_var.get())
            delay_game = int(self.delay_game_var.get())
            delay_dialog = int(self.delay_dialog_var.get())
            
            if any(x < 1 for x in [delay_startup, delay_auth, delay_game, delay_dialog]):
                raise ValueError("Задержки должны быть >= 1")
        except ValueError as e:
            messagebox.showerror("❌ Ошибка", f"Неверные задержки: {e}")
            return
        
        self.config["settings"] = {
            "steam_exe_path": self.steam_path_var.get(),
            "game_app_id": self.app_id_var.get(),
            "game_exe_path": self.game_exe_var.get(),
            "delay_startup": delay_startup,
            "delay_auth": delay_auth,
            "delay_game": delay_game,
            "delay_dialog": delay_dialog,
        }
        save_config(self.config)
        messagebox.showinfo("✓ Успех", "Настройки сохранены")
        self._log("✓ Настройки сохранены")
    
    def _start_steam_only(self):
        selected = [login for login, var in self.account_vars.items() if var.get()]
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Выбери аккаунт")
            return
        
        self.running = True
        self.start_btn.config(state="disabled")
        self.start_game_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        thread = threading.Thread(
            target=self._run_sequence,
            args=(selected, False),
            daemon=True
        )
        thread.start()
    
    def _start_steam_with_game(self):
        selected = [login for login, var in self.account_vars.items() if var.get()]
        if not selected:
            messagebox.showwarning("⚠️ Внимание", "Выбери аккаунт")
            return
        
        self.running = True
        self.start_btn.config(state="disabled")
        self.start_game_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        
        thread = threading.Thread(
            target=self._run_sequence,
            args=(selected, True),
            daemon=True
        )
        thread.start()
    
    def _run_sequence(self, logins, with_game=False):
        try:
            steam_exe = find_steam_exe(self.config.get("settings", {}).get("steam_exe_path", ""))
            app_id = self.config.get("settings", {}).get("game_app_id", "420980")
            game_exe = self.config.get("settings", {}).get("game_exe_path", "")
            delay_startup = self.config.get("settings", {}).get("delay_startup", 15)
            delay_auth = self.config.get("settings", {}).get("delay_auth", 40)
            delay_game = self.config.get("settings", {}).get("delay_game", 10)
            delay_dialog = self.config.get("settings", {}).get("delay_dialog", 3)
            
            self._log(f"\n{'='*60}")
            self._log(f"🚀 Запуск {'с игрой' if with_game else 'только Steam'} для {len(logins)} аккаунт(о)в")
            self._log(f"{'='*60}")
            
            for login in logins:
                if not self.running:
                    break
                
                acc = next((a for a in self.config["accounts"] if a["login"] == login), None)
                if not acc:
                    continue
                
                password = get_account_password(acc)
                
                try:
                    if with_game:
                        launch_steam_with_game(
                            login, password, steam_exe,
                            app_id=app_id, game_exe=game_exe,
                            delay_startup=delay_startup,
                            delay_auth=delay_auth,
                            delay_game=delay_game,
                            delay_dialog=delay_dialog,
                            status_callback=self._log
                        )
                    else:
                        launch_steam_only(
                            login, password, steam_exe,
                            delay_startup=delay_startup,
                            delay_hold=delay_game,
                            delay_dialog=delay_dialog,
                            status_callback=self._log
                        )
                except Exception as e:
                    self._log(f"❌ Ошибка для {login}: {e}")
                
                if self.running and login != logins[-1]:
                    self._log("⏳ Пауза 2 секунды перед следующим...")
                    time.sleep(2)
            
            self._log(f"{'='*60}")
            self._log("✓ Последовательность завершена")
            self._log(f"{'='*60}\n")
        
        except Exception as e:
            self._log(f"❌ Критическая ошибка: {e}")
            messagebox.showerror("❌ Ошибка", str(e))
        
        finally:
            self.start_btn.config(state="normal")
            self.start_game_btn.config(state="normal")
            self.stop_btn.config(state="disabled")
            self.running = False
    
    def _stop(self):
        self._log("\n⏹ Остановка...")
        self.running = False
        kill_steam_processes()
    
    def _clear_logs(self):
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")


class AccountDialog:
    def __init__(self, parent, on_save):
        self.on_save = on_save
        
        win = tk.Toplevel(parent)
        win.title("➕ Добавить аккаунт")
        win.geometry("400x200")
        win.transient(parent)
        win.grab_set()
        
        win.columnconfigure(1, weight=1)
        
        ttk.Label(win, text="Название:").grid(row=0, column=0, sticky="w", padx=10, pady=10)
        self.label_var = tk.StringVar()
        ttk.Entry(win, textvariable=self.label_var).grid(row=0, column=1, sticky="ew", padx=10)
        
        ttk.Label(win, text="Steam логин:").grid(row=1, column=0, sticky="w", padx=10, pady=10)
        self.login_var = tk.StringVar()
        ttk.Entry(win, textvariable=self.login_var).grid(row=1, column=1, sticky="ew", padx=10)
        
        ttk.Label(win, text="Пароль:").grid(row=2, column=0, sticky="w", padx=10, pady=10)
        self.password_var = tk.StringVar()
        ttk.Entry(win, textvariable=self.password_var, show="*").grid(row=2, column=1, sticky="ew", padx=10)
        
        btn_frame = ttk.Frame(win)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        ttk.Button(btn_frame, text="✓ Сохранить", command=self._save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✗ Отмена", command=win.destroy).pack(side="left", padx=5)
    
    def _save(self):
        if not self.label_var.get().strip():
            messagebox.showwarning("⚠️ Внимание", "Введи название")
            return
        if not self.login_var.get().strip():
            messagebox.showwarning("⚠️ Внимание", "Введи логин Steam")
            return
        if not self.password_var.get():
            messagebox.showwarning("⚠️ Внимание", "Введи пароль")
            return
        
        account_data = add_account(
            self.label_var.get().strip(),
            self.login_var.get().strip(),
            self.password_var.get()
        )
        self.on_save(account_data)
        messagebox.showinfo("✓ Успех", "Аккаунт добавлен")


if __name__ == "__main__":
    root = tk.Tk()
    app = SteamLauncherApp(root)
    root.mainloop()

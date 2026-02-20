"""
Currency Arbitrage Calculator - Standalone Version
Универсальный калькулятор для сравнения способов обмена валют в разных странах

Работает на стандартном tkinter без дополнительных зависимостей!

Author: Created with Antigravity AI
Version: 1.1
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import ctypes
from typing import Dict, Optional

# Включаем DPI awareness для Windows (четкие шрифты)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI aware
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()  # Fallback
    except Exception:
        pass

# Попробуем импортировать matplotlib, если есть
# ОТКЛЮЧЕНО - используем Apple-style текстовые карточки
HAS_MATPLOTLIB = False
# try:
#     import matplotlib
#     matplotlib.use('TkAgg')
#     from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#     from matplotlib.figure import Figure
#     HAS_MATPLOTLIB = True
# except ImportError:
#     HAS_MATPLOTLIB = False
#     print("⚠️ matplotlib не установлен - график будет в текстовом виде")

# Больше не требуем requests хуками, используем urllib.request внутри RateFetcher

# ==============================================================================
# CONSTANTS & DEFAULTS
# ==============================================================================

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

# ==============================================================================
# COUNTRY PROFILES
# ==============================================================================

COUNTRY_PROFILES = {
    # ===== КАВКАЗ И ЗАКАВКАЗЬЕ =====
    "georgia": {
        "name": "Грузия", "flag": "🇬🇪", "city": "Батуми",
        "local_currency": "GEL", "local_symbol": "₾", "local_name": "Лари",
        "central_bank": "НБГ", "central_bank_full": "Центробанк Грузии",
        "central_bank_api": "https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies",
        "street_exchange": "Valuto/Rico",
        "default_rates": {"nbg_rate": 3.16, "street_rate": 3.14, "direct_rate": 3.02, "eur_usd_rate": 1.08, "usd_gel_rate": 2.9}
    },
    "armenia": {
        "name": "Армения", "flag": "🇦🇲", "city": "Ереван",
        "local_currency": "AMD", "local_symbol": "֏", "local_name": "Драм",
        "central_bank": "ЦБА", "central_bank_full": "ЦБ Армении",
        "central_bank_api": "", "street_exchange": "Обменник",
        "default_rates": {"nbg_rate": 430.0, "street_rate": 428.0, "direct_rate": 420.0, "eur_usd_rate": 1.08, "usd_gel_rate": 400.0}
    },
    "azerbaijan": {
        "name": "Азербайджан", "flag": "🇦🇿", "city": "Баку",
        "local_currency": "AZN", "local_symbol": "₼", "local_name": "Манат",
        "central_bank": "ЦБА", "central_bank_full": "ЦБ Азербайджана",
        "central_bank_api": "", "street_exchange": "Обменник",
        "default_rates": {"nbg_rate": 1.84, "street_rate": 1.82, "direct_rate": 1.78, "eur_usd_rate": 1.08, "usd_gel_rate": 1.7}
    },
    
    # ===== БАЛКАНЫ =====
    "serbia": {
        "name": "Сербия", "flag": "🇷🇸", "city": "Белград",
        "local_currency": "RSD", "local_symbol": "дин", "local_name": "Динар",
        "central_bank": "НБС", "central_bank_full": "Народный Банк Сербии",
        "central_bank_api": "https://nbs.rs/", "street_exchange": "Menjačnica",
        "default_rates": {"nbg_rate": 117.0, "street_rate": 116.5, "direct_rate": 115.0, "eur_usd_rate": 1.08, "usd_gel_rate": 108.0}
    },
    "albania": {
        "name": "Албания", "flag": "🇦🇱", "city": "Тирана",
        "local_currency": "ALL", "local_symbol": "L", "local_name": "Лек",
        "central_bank": "БА", "central_bank_full": "Банк Албании",
        "central_bank_api": "", "street_exchange": "Këmbim Valutor",
        "default_rates": {"nbg_rate": 100.0, "street_rate": 99.0, "direct_rate": 97.0, "eur_usd_rate": 1.08, "usd_gel_rate": 93.0}
    },
    "north_macedonia": {
        "name": "Сев. Македония", "flag": "🇲🇰", "city": "Скопье",
        "local_currency": "MKD", "local_symbol": "ден", "local_name": "Денар",
        "central_bank": "НБМ", "central_bank_full": "НБ Македонии",
        "central_bank_api": "", "street_exchange": "Менувачница",
        "default_rates": {"nbg_rate": 61.5, "street_rate": 61.0, "direct_rate": 60.0, "eur_usd_rate": 1.08, "usd_gel_rate": 57.0}
    },
    "bosnia": {
        "name": "Босния", "flag": "🇧🇦", "city": "Сараево",
        "local_currency": "BAM", "local_symbol": "KM", "local_name": "Марка",
        "central_bank": "ЦББиГ", "central_bank_full": "ЦБ Боснии",
        "central_bank_api": "", "street_exchange": "Mjenjačnica",
        "default_rates": {"nbg_rate": 1.96, "street_rate": 1.95, "direct_rate": 1.92, "eur_usd_rate": 1.08, "usd_gel_rate": 1.81}
    },
    
    # ===== ВОСТОЧНАЯ ЕВРОПА =====
    "ukraine": {
        "name": "Украина", "flag": "🇺🇦", "city": "Киев",
        "local_currency": "UAH", "local_symbol": "₴", "local_name": "Гривна",
        "central_bank": "НБУ", "central_bank_full": "НБ Украины",
        "central_bank_api": "", "street_exchange": "Обмін валют",
        "default_rates": {"nbg_rate": 44.0, "street_rate": 43.5, "direct_rate": 42.0, "eur_usd_rate": 1.08, "usd_gel_rate": 41.0}
    },
    "moldova": {
        "name": "Молдова", "flag": "🇲🇩", "city": "Кишинёв",
        "local_currency": "MDL", "local_symbol": "L", "local_name": "Лей",
        "central_bank": "НБМ", "central_bank_full": "НБ Молдовы",
        "central_bank_api": "", "street_exchange": "Schimb Valutar",
        "default_rates": {"nbg_rate": 19.5, "street_rate": 19.3, "direct_rate": 19.0, "eur_usd_rate": 1.08, "usd_gel_rate": 18.0}
    },
    "belarus": {
        "name": "Беларусь", "flag": "🇧🇾", "city": "Минск",
        "local_currency": "BYN", "local_symbol": "Br", "local_name": "Рубль",
        "central_bank": "НББ", "central_bank_full": "НБ Беларуси",
        "central_bank_api": "", "street_exchange": "Обменник",
        "default_rates": {"nbg_rate": 3.5, "street_rate": 3.45, "direct_rate": 3.4, "eur_usd_rate": 1.08, "usd_gel_rate": 3.2}
    },
    "russia": {
        "name": "Россия", "flag": "🇷🇺", "city": "Москва",
        "local_currency": "RUB", "local_symbol": "₽", "local_name": "Рубль",
        "central_bank": "ЦБР", "central_bank_full": "ЦБ России",
        "central_bank_api": "https://cbr.ru/", "street_exchange": "Обменник",
        "default_rates": {"nbg_rate": 105.0, "street_rate": 103.0, "direct_rate": 100.0, "eur_usd_rate": 1.08, "usd_gel_rate": 97.0}
    },
    
    # ===== ЦЕНТРАЛЬНАЯ ЕВРОПА =====
    "poland": {
        "name": "Польша", "flag": "🇵🇱", "city": "Варшава",
        "local_currency": "PLN", "local_symbol": "zł", "local_name": "Злотый",
        "central_bank": "НБП", "central_bank_full": "НБ Польши",
        "central_bank_api": "https://nbp.pl/", "street_exchange": "Kantor",
        "default_rates": {"nbg_rate": 4.3, "street_rate": 4.25, "direct_rate": 4.15, "eur_usd_rate": 1.08, "usd_gel_rate": 4.0}
    },
    "czechia": {
        "name": "Чехия", "flag": "🇨🇿", "city": "Прага",
        "local_currency": "CZK", "local_symbol": "Kč", "local_name": "Крона",
        "central_bank": "ЧНБ", "central_bank_full": "ЧНБ",
        "central_bank_api": "https://cnb.cz/", "street_exchange": "Směnárna",
        "default_rates": {"nbg_rate": 25.3, "street_rate": 25.0, "direct_rate": 24.5, "eur_usd_rate": 1.08, "usd_gel_rate": 23.5}
    },
    "hungary": {
        "name": "Венгрия", "flag": "🇭🇺", "city": "Будапешт",
        "local_currency": "HUF", "local_symbol": "Ft", "local_name": "Форинт",
        "central_bank": "МНБ", "central_bank_full": "НБ Венгрии",
        "central_bank_api": "https://mnb.hu/", "street_exchange": "Pénzváltó",
        "default_rates": {"nbg_rate": 395.0, "street_rate": 390.0, "direct_rate": 380.0, "eur_usd_rate": 1.08, "usd_gel_rate": 365.0}
    },
    "romania": {
        "name": "Румыния", "flag": "🇷🇴", "city": "Бухарест",
        "local_currency": "RON", "local_symbol": "lei", "local_name": "Лей",
        "central_bank": "НБР", "central_bank_full": "НБ Румынии",
        "central_bank_api": "https://bnr.ro/", "street_exchange": "Casa de Schimb",
        "default_rates": {"nbg_rate": 4.97, "street_rate": 4.92, "direct_rate": 4.85, "eur_usd_rate": 1.08, "usd_gel_rate": 4.6}
    },
    "bulgaria": {
        "name": "Болгария", "flag": "🇧🇬", "city": "София",
        "local_currency": "BGN", "local_symbol": "лв", "local_name": "Лев",
        "central_bank": "БНБ", "central_bank_full": "БНБ",
        "central_bank_api": "https://bnb.bg/", "street_exchange": "Обменно бюро",
        "default_rates": {"nbg_rate": 1.96, "street_rate": 1.94, "direct_rate": 1.90, "eur_usd_rate": 1.08, "usd_gel_rate": 1.81}
    },
    
    # ===== СКАНДИНАВИЯ =====
    "sweden": {
        "name": "Швеция", "flag": "🇸🇪", "city": "Стокгольм",
        "local_currency": "SEK", "local_symbol": "kr", "local_name": "Крона",
        "central_bank": "Риксбанк", "central_bank_full": "Riksbank",
        "central_bank_api": "https://riksbank.se/", "street_exchange": "Forex",
        "default_rates": {"nbg_rate": 11.5, "street_rate": 11.3, "direct_rate": 11.0, "eur_usd_rate": 1.08, "usd_gel_rate": 10.6}
    },
    "norway": {
        "name": "Норвегия", "flag": "🇳🇴", "city": "Осло",
        "local_currency": "NOK", "local_symbol": "kr", "local_name": "Крона",
        "central_bank": "Norges Bank", "central_bank_full": "Norges Bank",
        "central_bank_api": "https://norges-bank.no/", "street_exchange": "Forex",
        "default_rates": {"nbg_rate": 11.8, "street_rate": 11.6, "direct_rate": 11.3, "eur_usd_rate": 1.08, "usd_gel_rate": 10.9}
    },
    "denmark": {
        "name": "Дания", "flag": "🇩🇰", "city": "Копенгаген",
        "local_currency": "DKK", "local_symbol": "kr", "local_name": "Крона",
        "central_bank": "Danmarks NB", "central_bank_full": "Danmarks Nationalbank",
        "central_bank_api": "https://nationalbanken.dk/", "street_exchange": "Forex",
        "default_rates": {"nbg_rate": 7.46, "street_rate": 7.4, "direct_rate": 7.3, "eur_usd_rate": 1.08, "usd_gel_rate": 6.9}
    },
    "iceland": {
        "name": "Исландия", "flag": "🇮🇸", "city": "Рейкьявик",
        "local_currency": "ISK", "local_symbol": "kr", "local_name": "Крона",
        "central_bank": "Seðlabanki", "central_bank_full": "ЦБ Исландии",
        "central_bank_api": "", "street_exchange": "Gjaldeyrisskipti",
        "default_rates": {"nbg_rate": 150.0, "street_rate": 148.0, "direct_rate": 145.0, "eur_usd_rate": 1.08, "usd_gel_rate": 139.0}
    },
    
    # ===== ЗАПАДНАЯ ЕВРОПА (не EUR) =====
    "uk": {
        "name": "Великобритания", "flag": "🇬🇧", "city": "Лондон",
        "local_currency": "GBP", "local_symbol": "£", "local_name": "Фунт",
        "central_bank": "BoE", "central_bank_full": "Bank of England",
        "central_bank_api": "https://bankofengland.co.uk/", "street_exchange": "Bureau de Change",
        "default_rates": {"nbg_rate": 0.84, "street_rate": 0.83, "direct_rate": 0.82, "eur_usd_rate": 1.08, "usd_gel_rate": 0.78}
    },
    "switzerland": {
        "name": "Швейцария", "flag": "🇨🇭", "city": "Цюрих",
        "local_currency": "CHF", "local_symbol": "Fr", "local_name": "Франк",
        "central_bank": "SNB", "central_bank_full": "Swiss National Bank",
        "central_bank_api": "https://snb.ch/", "street_exchange": "Wechselstube",
        "default_rates": {"nbg_rate": 0.94, "street_rate": 0.93, "direct_rate": 0.91, "eur_usd_rate": 1.08, "usd_gel_rate": 0.87}
    },
    
    # ===== ТУРЦИЯ =====
    "turkey": {
        "name": "Турция", "flag": "🇹🇷", "city": "Стамбул",
        "local_currency": "TRY", "local_symbol": "₺", "local_name": "Лира",
        "central_bank": "TCMB", "central_bank_full": "ЦБ Турции",
        "central_bank_api": "https://tcmb.gov.tr/", "street_exchange": "Döviz Bürosu",
        "default_rates": {"nbg_rate": 35.0, "street_rate": 34.8, "direct_rate": 34.0, "eur_usd_rate": 1.08, "usd_gel_rate": 32.5}
    }
}

DEFAULT_SETTINGS = {
    "country": "georgia",             # Выбранная страна
    "nbg_rate": 3.1595,               # Курс ЦБ EUR -> Local
    "eur_usd_rate": 1.16,             # IBT cross-rate EUR -> USD
    "usd_gel_rate": 2.69,             # Credo USD -> Local
    "street_rate": 3.143,             # Обменник
    "direct_implied_rate": 3.02,      # Эффективный курс карты IBT
    "ibt_transfer_fee": 1.5,          # Комиссия перевода IBT %
    "atm_fee_pct": 1.5,               # Комиссия банкомата %
    "atm_fee_fix": 1.0,               # Фикс комиссия банкомата EUR
    "last_amount": 100.0,             # Последняя введенная сумма
    "theme": "dark"                   # Тема: dark или light
}

# ==============================================================================
# THEME COLORS
# ==============================================================================

THEMES = {
    "dark": {
        # Apple-inspired dark mode
        "bg": "#000000",
        "bg_secondary": "#1c1c1e",
        "bg_card": "#2c2c2e",
        "bg_elevated": "#3a3a3c",
        "fg": "#ffffff",
        "fg_secondary": "#98989d",
        "accent": "#0a84ff",
        "profit": "#30d158",
        "loss": "#ff453a",
        "warning": "#ff9f0a",
        "border": "#38383a",
        "entry_bg": "#1c1c1e",
        "button_bg": "#30d158",
        "button_fg": "#000000",
        # Chart colors
        "chart_bar_1": "#ff453a",  # Red - worst
        "chart_bar_2": "#ff9f0a",  # Orange - middle
        "chart_bar_3": "#30d158",  # Green - best
        "chart_ref": "#0a84ff",    # Blue - reference
    },
    "light": {
        # Apple-inspired light mode
        "bg": "#f2f2f7",
        "bg_secondary": "#ffffff",
        "bg_card": "#ffffff",
        "bg_elevated": "#ffffff",
        "fg": "#000000",
        "fg_secondary": "#6e6e73",
        "accent": "#007aff",
        "profit": "#34c759",
        "loss": "#ff3b30",
        "warning": "#ff9500",
        "border": "#d1d1d6",
        "entry_bg": "#ffffff",
        "button_bg": "#34c759",
        "button_fg": "#ffffff",
        # Chart colors
        "chart_bar_1": "#ff3b30",
        "chart_bar_2": "#ff9500",
        "chart_bar_3": "#34c759",
        "chart_ref": "#007aff",
    }
}

# ==============================================================================
# CALENDAR POPUP
# ==============================================================================

class CalendarPopup:
    """Simple calendar popup for date selection"""
    
    def __init__(self, parent, date_var, colors, on_select=None):
        self.parent = parent
        self.date_var = date_var
        self.colors = colors
        self.on_select = on_select
        
        # Parse current date
        import calendar
        self.calendar = calendar
        
        try:
            parts = date_var.get().split(".")
            self.day = int(parts[0])
            self.month = int(parts[1])
            self.year = int(parts[2])
        except:
            from datetime import datetime
            now = datetime.now()
            self.day = now.day
            self.month = now.month
            self.year = now.year
        
        self._create_popup()
    
    def _create_popup(self):
        """Create the calendar popup window"""
        self.popup = tk.Toplevel(self.parent)
        self.popup.overrideredirect(True)  # No window decorations
        self.popup.configure(bg=self.colors["bg_card"])
        
        # Position near parent
        x = self.parent.winfo_rootx()
        y = self.parent.winfo_rooty() + self.parent.winfo_height()
        self.popup.geometry(f"+{x}+{y}")
        
        # Main frame with border
        main = tk.Frame(self.popup, bg=self.colors["bg_card"],
                       highlightthickness=1,
                       highlightbackground=self.colors["accent"])
        main.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Header with month/year and navigation
        header = tk.Frame(main, bg=self.colors["bg_card"])
        header.pack(fill="x", padx=5, pady=5)
        
        tk.Button(header, text="◀", font=("Segoe UI", 10),
                 bg=self.colors["bg_card"], fg=self.colors["fg"],
                 bd=0, command=self._prev_month).pack(side="left")
        
        self.header_label = tk.Label(header, 
                                    text=self._get_month_year(),
                                    font=("Segoe UI", 11, "bold"),
                                    bg=self.colors["bg_card"],
                                    fg=self.colors["fg"])
        self.header_label.pack(side="left", expand=True)
        
        tk.Button(header, text="▶", font=("Segoe UI", 10),
                 bg=self.colors["bg_card"], fg=self.colors["fg"],
                 bd=0, command=self._next_month).pack(side="right")
        
        # Days of week header
        days_frame = tk.Frame(main, bg=self.colors["bg_card"])
        days_frame.pack(fill="x", padx=5)
        
        for day in ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]:
            tk.Label(days_frame, text=day, width=3,
                    font=("Segoe UI", 9),
                    bg=self.colors["bg_card"],
                    fg=self.colors["fg_secondary"]).pack(side="left", padx=1)
        
        # Calendar grid
        self.grid_frame = tk.Frame(main, bg=self.colors["bg_card"])
        self.grid_frame.pack(padx=5, pady=5)
        
        self._draw_calendar()
        
        # Close button
        tk.Button(main, text="Закрыть", font=("Segoe UI", 9),
                 bg=self.colors["border"], fg=self.colors["fg"],
                 bd=0, padx=10, pady=3,
                 command=self.popup.destroy).pack(pady=(0, 5))
        
        # Close on click outside
        self.popup.bind("<FocusOut>", lambda e: self.popup.destroy())
        self.popup.focus_set()
    
    def _get_month_year(self):
        months = ["", "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
                 "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"]
        return f"{months[self.month]} {self.year}"
    
    def _prev_month(self):
        self.month -= 1
        if self.month < 1:
            self.month = 12
            self.year -= 1
        self._refresh()
    
    def _next_month(self):
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
        self._refresh()
    
    def _refresh(self):
        self.header_label.configure(text=self._get_month_year())
        self._draw_calendar()
    
    def _draw_calendar(self):
        # Clear grid
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        
        # Get calendar for month
        cal = self.calendar.Calendar(firstweekday=0)  # Monday first
        weeks = cal.monthdayscalendar(self.year, self.month)
        
        from datetime import datetime
        today = datetime.now()
        
        for week in weeks:
            week_frame = tk.Frame(self.grid_frame, bg=self.colors["bg_card"])
            week_frame.pack()
            
            for day in week:
                if day == 0:
                    lbl = tk.Label(week_frame, text="", width=3,
                                  bg=self.colors["bg_card"])
                else:
                    is_today = (day == today.day and 
                               self.month == today.month and 
                               self.year == today.year)
                    is_selected = (day == self.day and 
                                  self.month == int(self.date_var.get().split(".")[1]) if "." in self.date_var.get() else False)
                    
                    bg = self.colors["accent"] if is_today else self.colors["bg_card"]
                    fg = "#ffffff" if is_today else self.colors["fg"]
                    
                    lbl = tk.Button(week_frame, text=str(day), width=3,
                                   font=("Segoe UI", 9, "bold" if is_today else "normal"),
                                   bg=bg, fg=fg, bd=0,
                                   command=lambda d=day: self._select_day(d))
                lbl.pack(side="left", padx=1, pady=1)
    
    def _select_day(self, day):
        date_str = f"{day:02d}.{self.month:02d}.{self.year}"
        self.date_var.set(date_str)
        if self.on_select:
            self.on_select()
        self.popup.destroy()

# ==============================================================================
# SETTINGS MANAGER
# ==============================================================================

class SettingsManager:
    def __init__(self, filepath: str = SETTINGS_FILE):
        self.filepath = filepath
        self.settings = self.load()
        self.countries = self._load_countries()
    
    def load(self) -> dict:
        try:
            if os.path.exists(self.filepath):
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    return {**DEFAULT_SETTINGS, **loaded}
        except Exception as e:
            print(f"Settings load error: {e}")
        return DEFAULT_SETTINGS.copy()
    
    def _load_countries(self) -> dict:
        """Load countries: built-in + custom from settings.json"""
        # Start with built-in countries
        countries = COUNTRY_PROFILES.copy()
        
        # Add custom countries from settings if present
        custom = self.settings.get("custom_countries", {})
        if custom and isinstance(custom, dict):
            for key, profile in custom.items():
                # Validate minimum required fields
                required = ["name", "flag", "local_currency", "local_symbol"]
                if all(field in profile for field in required):
                    # Fill in defaults for missing fields
                    defaults = {
                        "city": profile.get("name", ""),
                        "local_name": profile.get("local_currency", ""),
                        "central_bank": "ЦБ",
                        "central_bank_full": "Центробанк",
                        "central_bank_api": "",
                        "street_exchange": "Обменник",
                        "default_rates": {
                            "nbg_rate": 1.0,
                            "street_rate": 1.0,
                            "direct_rate": 1.0,
                            "eur_usd_rate": 1.0,
                            "usd_gel_rate": 1.0,
                        }
                    }
                    countries[key] = {**defaults, **profile}
        
        return countries
    
    def get_countries(self) -> dict:
        """Return all countries (built-in + custom)"""
        return self.countries
    
    def add_country(self, key: str, profile: dict):
        """Add a custom country"""
        custom = self.settings.get("custom_countries", {})
        custom[key] = profile
        self.settings["custom_countries"] = custom
        self.countries[key] = profile
        self.save()
    
    def save(self):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Settings save error: {e}")
    
    def get(self, key: str, default=None):
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        self.settings[key] = value

import urllib.request
import re

class RateFetcher:
    """Universal rate fetcher using urllib (no third-party dependencies)"""
    
    @staticmethod
    def get_headers():
        return {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
    @staticmethod
    def fetch_georgia_rates() -> Optional[Dict[str, float]]:
        rates = {}
        
        # 1. NBG (Central Bank EUR and USD)
        try:
            req = urllib.request.Request("https://nbg.gov.ge/gw/api/ct/monetarypolicy/currencies/en/json", headers=RateFetcher.get_headers())
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data and isinstance(data, list):
                    currencies = data[0].get("currencies", [])
                    for curr in currencies:
                        code = curr.get("code")
                        if code in ["EUR", "USD"]:
                            rates[code] = curr.get("rate", 0) / curr.get("quantity", 1)
        except Exception as e:
            print(f"NBG API Error: {e}")
            
        # 2. Rico (Street Exchange & Credo Approximation)
        try:
            req = urllib.request.Request("https://rico.ge/?lang=en", headers=RateFetcher.get_headers())
            with urllib.request.urlopen(req, timeout=10) as response:
                html = response.read().decode('utf-8')
                eur_match = re.search(r'EUR.*?(\d+\.\d+)', html, re.IGNORECASE | re.DOTALL)
                usd_match = re.search(r'USD.*?(\d+\.\d+)', html, re.IGNORECASE | re.DOTALL)
                if eur_match:
                    rates["street_eur"] = float(eur_match.group(1))
                if usd_match:
                    rates["credo_usd"] = float(usd_match.group(1))
        except Exception as e:
            print(f"Rico Scrape Error: {e}")
            
        # 3. Frankfurter (M/C cross-rate EUR->USD proxy)
        try:
            req = urllib.request.Request("https://api.frankfurter.dev/v1/latest?base=EUR&symbols=USD", headers=RateFetcher.get_headers())
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                rates["eur_usd"] = data["rates"]["USD"]
        except Exception as e:
            print(f"Frankfurter API Error: {e}")
            
        return rates if rates else None

# ==============================================================================
# CALCULATOR LOGIC
# ==============================================================================

class Calculator:
    @staticmethod
    def calc_direct(spend_eur: float, implied_rate: float) -> float:
        return spend_eur * implied_rate
    
    @staticmethod
    def calc_transfer(spend_eur: float, fee_pct: float, 
                      eur_usd: float, usd_gel: float) -> float:
        net_eur = spend_eur / (1 + fee_pct / 100)
        amount_usd = net_eur * eur_usd
        return amount_usd * usd_gel
    
    @staticmethod
    def calc_cash(spend_eur: float, fee_pct: float, 
                  fix_fee: float, street_rate: float) -> float:
        if spend_eur <= fix_fee:
            return 0.0
        net_eur = (spend_eur - fix_fee) / (1 + fee_pct / 100)
        return net_eur * street_rate
    
    @staticmethod
    def calc_nbg_reference(spend_eur: float, nbg_rate: float) -> float:
        return spend_eur * nbg_rate
    
    @staticmethod
    def calc_loss_percent(actual: float, reference: float) -> float:
        if reference <= 0:
            return 0.0
        return ((reference - actual) / reference) * 100

# ==============================================================================
# MAIN APPLICATION
# ==============================================================================

class CurrencyCalculatorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.settings = SettingsManager()
        self.current_theme = self.settings.get("theme", "dark")
        self.colors = THEMES[self.current_theme]
        # Country setup (supports custom countries from settings.json)
        self.all_countries = self.settings.get_countries()
        self.country_key = self.settings.get("country", "georgia")
        self.country = self.all_countries.get(self.country_key, self.all_countries.get("georgia", list(self.all_countries.values())[0]))
        
        # Window setup (dynamic based on country)
        self._update_window_title()
        self.root.geometry("1600x900")
        self.root.minsize(1100, 700)
        
        # Variables
        self.amount_var = tk.StringVar(value=str(self.settings.get("last_amount", 100.0)))
        self.nbg_var = tk.StringVar(value=str(self.settings.get("nbg_rate")))
        self.eur_usd_var = tk.StringVar(value=str(self.settings.get("eur_usd_rate")))
        self.usd_gel_var = tk.StringVar(value=str(self.settings.get("usd_gel_rate")))
        self.street_var = tk.StringVar(value=str(self.settings.get("street_rate")))
        self.direct_var = tk.StringVar(value=str(self.settings.get("direct_implied_rate")))
        self.ibt_fee_var = tk.StringVar(value=str(self.settings.get("ibt_transfer_fee")))
        self.atm_fee_pct_var = tk.StringVar(value=str(self.settings.get("atm_fee_pct")))
        self.atm_fee_fix_var = tk.StringVar(value=str(self.settings.get("atm_fee_fix")))
        
        # Date variables for rate tracking
        from datetime import datetime
        today = datetime.now().strftime("%d.%m.%Y")
        self.nbg_date_var = tk.StringVar(value=self.settings.get("nbg_date", today))
        self.direct_date_var = tk.StringVar(value=self.settings.get("direct_date", today))
        self.transfer_date_var = tk.StringVar(value=self.settings.get("transfer_date", today))
        self.cash_date_var = tk.StringVar(value=self.settings.get("cash_date", today))
        
        # Transaction calculator variables (for Method 1)
        self.trans_gel_var = tk.StringVar(value="19.00")
        self.trans_eur_var = tk.StringVar(value="6.29")
        self.trans_rate_var = tk.StringVar(value="3.02")
        
        self.results = {}
        
        self._apply_theme()
        self._create_ui()
        self.calculate()
        
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _apply_theme(self):
        """Apply theme colors"""
        self.colors = THEMES[self.current_theme]
        self.root.configure(bg=self.colors["bg"])
        
        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')
        
        style.configure(".", 
                       background=self.colors["bg"],
                       foreground=self.colors["fg"],
                       fieldbackground=self.colors["entry_bg"])
        
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("Card.TFrame", background=self.colors["bg_card"])
        style.configure("Secondary.TFrame", background=self.colors["bg_secondary"])
        
        style.configure("TLabel", 
                       background=self.colors["bg"],
                       foreground=self.colors["fg"],
                       font=("Segoe UI", 10))
        
        style.configure("Title.TLabel",
                       font=("Segoe UI", 20, "bold"),
                       foreground=self.colors["accent"])
        
        style.configure("Header.TLabel",
                       font=("Segoe UI", 14, "bold"),
                       foreground=self.colors["fg"])
        
        style.configure("Secondary.TLabel",
                       foreground=self.colors["fg_secondary"])
        
        style.configure("Profit.TLabel",
                       foreground=self.colors["profit"],
                       font=("Segoe UI", 12, "bold"))
        
        style.configure("Loss.TLabel",
                       foreground=self.colors["loss"])
        
        style.configure("Big.TLabel",
                       font=("Segoe UI", 24, "bold"))
        
        style.configure("TEntry",
                       fieldbackground=self.colors["entry_bg"],
                       foreground=self.colors["fg"],
                       insertcolor=self.colors["fg"])
        
        style.configure("TButton",
                       background=self.colors["button_bg"],
                       foreground=self.colors["button_fg"],
                       font=("Segoe UI", 11, "bold"),
                       padding=(15, 10))
        
        style.map("TButton",
                 background=[("active", self.colors["profit"])])
        
        style.configure("Accent.TButton",
                       background=self.colors["accent"])
        
        style.map("Accent.TButton",
                 background=[("active", self.colors["accent"])])
    
    def _create_ui(self):
        """Create the main UI with resizable panels"""
        # Main container (stored for refresh)
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self._create_header(self.main_frame)
        
        # Content area with resizable panes (PanedWindow)
        self.paned = tk.PanedWindow(
            self.main_frame, 
            orient="horizontal",
            bg=self.colors["border"],
            sashwidth=6,
            sashrelief="raised",
            opaqueresize=True
        )
        self.paned.pack(fill="both", expand=True, pady=10)
        
        # Left panel - Inputs (+30% wider)
        left_container = tk.Frame(self.paned, bg=self.colors["bg_secondary"])
        self._create_input_panel(left_container)
        self.paned.add(left_container, minsize=400, width=550)
        
        # Center - Results 
        center_container = tk.Frame(self.paned, bg=self.colors["bg_secondary"])
        self._create_results_panel(center_container)
        self.paned.add(center_container, minsize=380, width=500)
        
        # Right - Chart (increased to fit text)
        right_container = tk.Frame(self.paned, bg=self.colors["bg_secondary"])
        self._create_chart_panel(right_container)
        self.paned.add(right_container, minsize=350, width=420)
        
        # Bottom - Recommendation
        self._create_recommendation_banner(self.main_frame)
    
    def _create_header(self, parent):
        """Create header section with country selector"""
        header = tk.Frame(parent, bg=self.colors["bg_secondary"], height=60)
        header.pack(fill="x", pady=(0, 10))
        header.pack_propagate(False)
        
        # Title
        title = tk.Label(header, 
                        text="💱 CURRENCY ARBITRAGE CALCULATOR",
                        font=("Segoe UI", 18, "bold"),
                        bg=self.colors["bg_secondary"],
                        fg=self.colors["accent"])
        title.pack(side="left", padx=20, pady=15)
        
        # Dynamic subtitle based on country
        c = self.country
        subtitle_text = f"{c['city']} | IBT Card (EUR) → {c['local_currency']}"
        self.subtitle_label = tk.Label(header,
                           text=subtitle_text,
                           font=("Segoe UI", 11),
                           bg=self.colors["bg_secondary"],
                           fg=self.colors["fg_secondary"])
        self.subtitle_label.pack(side="left", padx=10, pady=15)
        
        # Country selector (dropdown)
        country_frame = tk.Frame(header, bg=self.colors["bg_secondary"])
        country_frame.pack(side="right", padx=10, pady=10)
        
        # Country dropdown button
        country_display = f"{self.country['flag']} {self.country['name']}"
        self.country_btn = tk.Menubutton(country_frame,
                                        text=country_display,
                                        font=("Segoe UI", 10, "bold"),
                                        bg=self.colors["bg_card"],
                                        fg=self.colors["fg"],
                                        activebackground=self.colors["accent"],
                                        activeforeground="#ffffff",
                                        relief="flat",
                                        padx=10, pady=5,
                                        cursor="hand2")
        self.country_btn.pack(side="left")
        
        # Dropdown menu
        self.country_menu = tk.Menu(self.country_btn, tearoff=0,
                                   bg=self.colors["bg_card"],
                                   fg=self.colors["fg"],
                                   activebackground=self.colors["accent"],
                                   activeforeground="#ffffff",
                                   font=("Segoe UI", 10))
        
        self._rebuild_country_menu()
        
        self.country_btn["menu"] = self.country_menu
        
        # Add country button (+)
        add_country_btn = tk.Button(country_frame,
                                   text="⚙",
                                   font=("Segoe UI", 10),
                                   bg=self.colors["bg_card"],
                                   fg=self.colors["fg_secondary"],
                                   bd=0,
                                   width=2,
                                   cursor="hand2",
                                   command=self._show_country_manager)
        add_country_btn.pack(side="left", padx=(5, 0))
        
        # Theme toggle
        theme_btn = tk.Button(header,
                             text="🌙" if self.current_theme == "dark" else "☀️",
                             font=("Segoe UI", 14),
                             bg=self.colors["bg_card"],
                             fg=self.colors["fg"],
                             bd=0,
                             width=3,
                             cursor="hand2",
                             command=self._toggle_theme)
        theme_btn.pack(side="right", padx=10, pady=10)
        
        # Refresh button
        refresh_text = f"🔄 Авто-Курсы"
        self.refresh_btn = tk.Button(header,
                               text=refresh_text,
                               font=("Segoe UI", 10, "bold"),
                               bg=self.colors["accent"],
                               fg="#ffffff",
                               bd=0,
                               padx=15,
                               pady=8,
                               cursor="hand2",
                               command=self._fetch_nbg_rates)
        self.refresh_btn.pack(side="right", padx=10, pady=10)
    
    def _update_window_title(self):
        """Update window title based on current country"""
        c = self.country
        self.root.title(f"💱 Currency Arbitrage Calculator | {c['flag']} {c['city']}")
    
    def _change_country(self, country_key: str):
        """Change country and refresh entire UI"""
        self.country_key = country_key
        self.country = self.all_countries[country_key]
        
        # Apply default rates for new country
        defaults = self.country.get("default_rates", {})
        if defaults:
            self.nbg_var.set(str(defaults.get("nbg_rate", 1.0)))
            self.street_var.set(str(defaults.get("street_rate", 1.0)))
            self.direct_var.set(str(defaults.get("direct_rate", 1.0)))
            self.eur_usd_var.set(str(defaults.get("eur_usd_rate", 1.0)))
            self.usd_gel_var.set(str(defaults.get("usd_gel_rate", 1.0)))
        
        # Save country selection
        self.settings.set("country", country_key)
        self.settings.save()
        
        # Refresh entire UI
        self._refresh_ui()
    
    def _refresh_ui(self):
        """Destroy and recreate UI with updated country settings"""
        # Destroy old UI
        if hasattr(self, 'main_frame') and self.main_frame:
            self.main_frame.destroy()
        
        # Recreate UI
        self._create_ui()
        self.calculate()
    
    def _rebuild_country_menu(self):
        """Rebuild country dropdown menu"""
        self.country_menu.delete(0, "end")
        
        for key, profile in self.all_countries.items():
            label = f"{profile['flag']} {profile['name']} ({profile['local_currency']})"
            self.country_menu.add_command(
                label=label,
                command=lambda k=key: self._change_country(k)
            )
    
    def _show_country_manager(self):
        """Show country manager dialog with scrollable list"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Управление странами")
        dialog.geometry("550x650")
        dialog.configure(bg=self.colors["bg"])
        dialog.transient(self.root)
        
        # Center dialog
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() - 550) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 650) // 2
        dialog.geometry(f"+{x}+{y}")
        
        # Title
        tk.Label(dialog, text="🌍 Управление странами",
                font=("Segoe UI", 14, "bold"),
                bg=self.colors["bg"],
                fg=self.colors["accent"]).pack(pady=10)
        
        # ===== SCROLLABLE COUNTRY LIST =====
        list_container = tk.Frame(dialog, bg=self.colors["bg_card"], height=280)
        list_container.pack(fill="x", padx=20, pady=5)
        list_container.pack_propagate(False)
        
        tk.Label(list_container, text="📋 Существующие страны (кликни для выбора):",
                font=("Segoe UI", 10, "bold"),
                bg=self.colors["bg_card"],
                fg=self.colors["fg"]).pack(anchor="w", padx=10, pady=5)
        
        # Canvas for scrolling
        canvas = tk.Canvas(list_container, bg=self.colors["bg_card"], 
                          highlightthickness=0, height=220)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["bg_card"])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        canvas.pack(side="left", fill="both", expand=True, padx=(10, 0))
        scrollbar.pack(side="right", fill="y", padx=(0, 5))
        
        # Populate country list
        for key, profile in self.all_countries.items():
            row = tk.Frame(scrollable_frame, bg=self.colors["bg_card"])
            row.pack(fill="x", pady=1)
            
            is_selected = (key == self.country_key)
            bg_color = self.colors["accent"] if is_selected else self.colors["bg_card"]
            fg_color = "#ffffff" if is_selected else self.colors["fg"]
            
            btn = tk.Button(row, 
                           text=f"{profile['flag']} {profile['name']} ({profile['local_currency']})",
                           font=("Segoe UI", 10),
                           bg=bg_color, fg=fg_color,
                           bd=0, anchor="w",
                           padx=10, pady=3,
                           cursor="hand2",
                           command=lambda k=key, d=dialog: self._select_country_and_close(k, d))
            btn.pack(side="left", fill="x", expand=True)
            
            # Delete button for custom countries
            if key not in COUNTRY_PROFILES:
                tk.Button(row, text="✕", font=("Segoe UI", 8),
                         bg=self.colors["loss"], fg="#ffffff",
                         bd=0, padx=5,
                         command=lambda k=key, d=dialog: self._delete_country(k, d)).pack(side="right", padx=5)
        
        # ===== ADD NEW COUNTRY FORM =====
        tk.Frame(dialog, height=2, bg=self.colors["border"]).pack(fill="x", padx=20, pady=10)
        
        tk.Label(dialog, text="➕ Добавить новую страну",
                font=("Segoe UI", 11, "bold"),
                bg=self.colors["bg"],
                fg=self.colors["profit"]).pack(anchor="w", padx=20)
        
        form_frame = tk.Frame(dialog, bg=self.colors["bg"])
        form_frame.pack(fill="x", padx=20, pady=5)
        
        fields = {}
        field_defs = [
            ("key", "ID (англ)", "mycountry"),
            ("name", "Название", "Моя страна"),
            ("flag", "Флаг", "🏳️"),
            ("city", "Город", "Город"),
            ("local_currency", "Валюта", "USD"),
            ("local_symbol", "Символ", "$"),
            ("nbg_rate", "Курс EUR→", "1.0"),
        ]
        
        for key, label, placeholder in field_defs:
            row = tk.Frame(form_frame, bg=self.colors["bg"])
            row.pack(fill="x", pady=1)
            
            tk.Label(row, text=label, width=12, anchor="w",
                    font=("Segoe UI", 9),
                    bg=self.colors["bg"],
                    fg=self.colors["fg_secondary"]).pack(side="left")
            
            entry = tk.Entry(row, font=("Segoe UI", 9), width=20,
                           bg=self.colors["entry_bg"],
                           fg=self.colors["fg"],
                           relief="flat",
                           highlightthickness=1,
                           highlightbackground=self.colors["border"])
            entry.pack(side="left", ipady=2)
            entry.insert(0, placeholder)
            fields[key] = entry
        
        def add_country():
            try:
                key = fields["key"].get().strip().lower().replace(" ", "_")
                if not key: return
                
                rate = float(fields["nbg_rate"].get().replace(",", "."))
                new_country = {
                    "name": fields["name"].get(),
                    "flag": fields["flag"].get(),
                    "city": fields["city"].get(),
                    "local_currency": fields["local_currency"].get().upper(),
                    "local_symbol": fields["local_symbol"].get(),
                    "local_name": fields["local_currency"].get(),
                    "central_bank": "ЦБ",
                    "central_bank_full": "Центробанк",
                    "central_bank_api": "",
                    "street_exchange": "Обменник",
                    "default_rates": {
                        "nbg_rate": rate,
                        "street_rate": rate * 0.99,
                        "direct_rate": rate * 0.96,
                        "eur_usd_rate": 1.08,
                        "usd_gel_rate": rate / 1.08,
                    }
                }
                
                self.settings.add_country(key, new_country)
                self.all_countries = self.settings.get_countries()
                self._rebuild_country_menu()
                dialog.destroy()
                self._show_country_manager()  # Reopen to show new country
            except Exception as e:
                print(f"Error: {e}")
        
        btn_frame = tk.Frame(dialog, bg=self.colors["bg"])
        btn_frame.pack(pady=10)
        
        tk.Button(btn_frame, text="✓ Добавить",
                 font=("Segoe UI", 10, "bold"),
                 bg=self.colors["profit"], fg="#ffffff",
                 bd=0, padx=15, pady=5, cursor="hand2",
                 command=add_country).pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="Закрыть",
                 font=("Segoe UI", 10),
                 bg=self.colors["border"], fg=self.colors["fg"],
                 bd=0, padx=15, pady=5,
                 command=dialog.destroy).pack(side="left", padx=5)
        
        # Unbind mousewheel when dialog closes
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            dialog.destroy()
        dialog.protocol("WM_DELETE_WINDOW", on_close)
    
    def _select_country_and_close(self, country_key: str, dialog):
        """Select country and close dialog"""
        dialog.destroy()
        self._change_country(country_key)
    
    def _delete_country(self, country_key: str, dialog):
        """Delete a custom country"""
        if country_key in self.all_countries and country_key not in COUNTRY_PROFILES:
            # Remove from settings
            custom = self.settings.settings.get("custom_countries", {})
            if country_key in custom:
                del custom[country_key]
                self.settings.settings["custom_countries"] = custom
                self.settings.save()
            
            # Update all_countries
            del self.all_countries[country_key]
            
            # If current country was deleted, switch to first available
            if self.country_key == country_key:
                first_key = list(self.all_countries.keys())[0]
                self._change_country(first_key)
            
            # Rebuild menu
            self._rebuild_country_menu()
            
            # Close and reopen dialog to refresh list
            dialog.destroy()
            self._show_country_manager()
    
    def _create_input_panel(self, parent):
        """Create input panel with method-grouped sections"""
        # Create scrollable panel (now using pack for PanedWindow)
        panel = tk.Frame(parent, bg=self.colors["bg_secondary"], padx=15, pady=10)
        panel.pack(fill="both", expand=True)
        
        # Title
        title = tk.Label(panel, text="⚙️ НАСТРОЙКИ",
                        font=("Segoe UI", 14, "bold"),
                        bg=self.colors["bg_secondary"],
                        fg=self.colors["fg"])
        title.pack(anchor="w", pady=(0, 10))
        
        # Amount input (main)
        self._create_input_field(panel, "💶 Сумма траты (EUR)", self.amount_var, is_main=True)
        
        # Calculate button
        calc_btn = tk.Button(panel,
                            text="⚡ РАССЧИТАТЬ",
                            font=("Segoe UI", 13, "bold"),
                            bg=self.colors["profit"],
                            fg="#000000",
                            bd=0,
                            pady=10,
                            cursor="hand2",
                            command=self.calculate)
        calc_btn.pack(fill="x", pady=(10, 15))
        
        # ===== Central Bank Reference (dynamic) =====
        c = self.country
        self._create_method_section(
            panel, 
            f"🏛️ ЭТАЛОН ({c['central_bank_full']})", 
            self.colors["accent"],
            [(f"Курс {c['central_bank']} (1 EUR = ? {c['local_currency']})", self.nbg_var)],
            date_var=self.nbg_date_var
        )
        
        # ===== Method 1: Direct Card with Rate Calculator =====
        self._create_method1_section(panel)
        
        # ===== Method 2: Transfer =====
        self._create_method_section(
            panel,
            "📲 МЕТОД 2: Перевод IBT → Credo",
            self.colors["warning"],
            [
                ("Комиссия перевода (%)", self.ibt_fee_var),
                ("Курс EUR → USD", self.eur_usd_var),
                (f"Курс USD → {c['local_currency']} (Credo)", self.usd_gel_var),
            ],
            date_var=self.transfer_date_var
        )
        
        # ===== Method 3: Cash =====
        self._create_method_section(
            panel,
            "💵 МЕТОД 3: Наличные + Обменник",
            self.colors["profit"],
            [
                ("Комиссия банкомата (%)", self.atm_fee_pct_var),
                ("Фикс. комиссия ATM (EUR)", self.atm_fee_fix_var),
                (f"Курс обменника ({c['street_exchange']})", self.street_var),
            ],
            date_var=self.cash_date_var
        )
    
    def _create_method1_section(self, parent):
        """Create Method 1 section with built-in rate calculator"""
        color = self.colors["loss"]
        
        # Section container
        section = tk.Frame(parent, bg=self.colors["bg_card"], highlightthickness=0)
        section.pack(fill="x", pady=5)
        
        # Colored accent bar
        accent_bar = tk.Frame(section, width=4, bg=color)
        accent_bar.pack(side="left", fill="y")
        
        # Content
        content = tk.Frame(section, bg=self.colors["bg_card"], padx=10, pady=8)
        content.pack(side="left", fill="x", expand=True)
        
        # Header with title and date
        header_frame = tk.Frame(content, bg=self.colors["bg_card"])
        header_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(header_frame, text="💳 МЕТОД 1: Прямая оплата картой",
                font=("Segoe UI", 10, "bold"),
                bg=self.colors["bg_card"],
                fg=color).pack(side="left")
        
        # Date picker
        date_frame = tk.Frame(header_frame, bg=self.colors["bg_card"])
        date_frame.pack(side="right")
        
        cal_icon = tk.Label(date_frame, text="📅",
                           font=("Segoe UI", 10),
                           bg=self.colors["bg_card"],
                           fg=self.colors["accent"],
                           cursor="hand2")
        cal_icon.pack(side="left")
        cal_icon.bind("<Button-1>", lambda e: CalendarPopup(
            date_frame, self.direct_date_var, self.colors))
        
        tk.Entry(date_frame, textvariable=self.direct_date_var,
                font=("Segoe UI", 9), width=10,
                bg=self.colors["entry_bg"],
                fg=self.colors["fg_secondary"],
                relief="flat", highlightthickness=1,
                highlightbackground=self.colors["border"]).pack(side="left", padx=(3, 0))
        
        # === Rate Calculator Section ===
        calc_frame = tk.Frame(content, bg=self.colors["bg_elevated"] if "bg_elevated" in self.colors else self.colors["bg_card"],
                             highlightthickness=1,
                             highlightbackground=self.colors["border"])
        calc_frame.pack(fill="x", pady=(5, 8), padx=2, ipady=5)
        
        calc_title = tk.Label(calc_frame, text="🧮 Калькулятор курса из транзакции",
                             font=("Segoe UI", 9, "bold"),
                             bg=calc_frame["bg"],
                             fg=self.colors["fg_secondary"])
        calc_title.pack(anchor="w", padx=8, pady=(5, 3))
        
        # Input row
        input_row = tk.Frame(calc_frame, bg=calc_frame["bg"])
        input_row.pack(fill="x", padx=8, pady=3)
        
        # Local currency received
        tk.Label(input_row, text=f"Получил {self.country['local_currency']}:",
                font=("Segoe UI", 9),
                bg=calc_frame["bg"],
                fg=self.colors["fg_secondary"]).pack(side="left")
        
        gel_entry = tk.Entry(input_row, textvariable=self.trans_gel_var,
                            font=("Segoe UI", 10, "bold"), width=8,
                            bg=self.colors["entry_bg"],
                            fg=self.colors["profit"],
                            relief="flat", highlightthickness=1,
                            highlightbackground=self.colors["border"])
        gel_entry.pack(side="left", padx=(5, 15))
        gel_entry.bind("<KeyRelease>", lambda e: self._calc_trans_rate())
        
        # EUR charged
        tk.Label(input_row, text="Списали EUR:",
                font=("Segoe UI", 9),
                bg=calc_frame["bg"],
                fg=self.colors["fg_secondary"]).pack(side="left")
        
        eur_entry = tk.Entry(input_row, textvariable=self.trans_eur_var,
                            font=("Segoe UI", 10, "bold"), width=8,
                            bg=self.colors["entry_bg"],
                            fg=self.colors["loss"],
                            relief="flat", highlightthickness=1,
                            highlightbackground=self.colors["border"])
        eur_entry.pack(side="left", padx=(5, 15))
        eur_entry.bind("<KeyRelease>", lambda e: self._calc_trans_rate())
        
        # Result: Calculated rate
        tk.Label(input_row, text="=",
                font=("Segoe UI", 12, "bold"),
                bg=calc_frame["bg"],
                fg=self.colors["fg"]).pack(side="left", padx=5)
        
        self.trans_rate_label = tk.Label(input_row, text="3.02",
                                        font=("Segoe UI", 12, "bold"),
                                        bg=calc_frame["bg"],
                                        fg=self.colors["accent"])
        self.trans_rate_label.pack(side="left")
        
        tk.Label(input_row, text=f"{self.country['local_currency']}/EUR",
                font=("Segoe UI", 9),
                bg=calc_frame["bg"],
                fg=self.colors["fg_secondary"]).pack(side="left", padx=(3, 0))
        
        # Apply button
        apply_btn = tk.Button(input_row, text="✓ Применить",
                             font=("Segoe UI", 9),
                             bg=color, fg="#ffffff",
                             bd=0, padx=10, pady=2,
                             cursor="hand2",
                             command=self._apply_trans_rate)
        apply_btn.pack(side="right")
        
        # Current rate field (editable)
        rate_frame = tk.Frame(content, bg=self.colors["bg_card"])
        rate_frame.pack(fill="x", pady=2)
        
        tk.Label(rate_frame, text="Используемый курс:",
                font=("Segoe UI", 9),
                bg=self.colors["bg_card"],
                fg=self.colors["fg_secondary"]).pack(anchor="w")
        
        tk.Entry(rate_frame, textvariable=self.direct_var,
                font=("Segoe UI", 11),
                bg=self.colors["entry_bg"],
                fg=self.colors["fg"],
                relief="flat", highlightthickness=1,
                highlightbackground=self.colors["border"],
                highlightcolor=color).pack(fill="x", pady=(2, 0), ipady=4)
    
    def _calc_trans_rate(self):
        """Calculate rate from transaction data"""
        try:
            gel = float(self.trans_gel_var.get().replace(",", "."))
            eur = float(self.trans_eur_var.get().replace(",", "."))
            if eur > 0:
                rate = gel / eur
                self.trans_rate_label.configure(text=f"{rate:.4f}")
                self.trans_rate_var.set(f"{rate:.4f}")
        except:
            pass
    
    def _apply_trans_rate(self):
        """Apply calculated rate to the direct rate field"""
        try:
            rate = float(self.trans_rate_var.get().replace(",", "."))
            self.direct_var.set(f"{rate:.4f}")
            self.calculate()
        except:
            pass
    
    def _create_method_section(self, parent, title: str, color: str, fields: list, date_var=None):
        """Create a colored section for a method with optional date field"""
        # Section container with colored left border
        section = tk.Frame(parent, bg=self.colors["bg_card"], 
                          highlightthickness=0)
        section.pack(fill="x", pady=5)
        
        # Colored accent bar on left
        accent_bar = tk.Frame(section, width=4, bg=color)
        accent_bar.pack(side="left", fill="y")
        
        # Content
        content = tk.Frame(section, bg=self.colors["bg_card"], padx=10, pady=8)
        content.pack(side="left", fill="x", expand=True)
        
        # Header with title and date
        header_frame = tk.Frame(content, bg=self.colors["bg_card"])
        header_frame.pack(fill="x", pady=(0, 5))
        
        # Section title
        title_lbl = tk.Label(header_frame, text=title,
                            font=("Segoe UI", 10, "bold"),
                            bg=self.colors["bg_card"],
                            fg=color)
        title_lbl.pack(side="left")
        
        # Date field (right side of header)
        if date_var:
            date_frame = tk.Frame(header_frame, bg=self.colors["bg_card"])
            date_frame.pack(side="right")
            
            # Clickable calendar icon
            cal_icon = tk.Label(date_frame, text="📅",
                               font=("Segoe UI", 10),
                               bg=self.colors["bg_card"],
                               fg=self.colors["accent"],
                               cursor="hand2")
            cal_icon.pack(side="left")
            cal_icon.bind("<Button-1>", lambda e: CalendarPopup(
                date_frame, date_var, self.colors))
            
            date_entry = tk.Entry(date_frame,
                                 textvariable=date_var,
                                 font=("Segoe UI", 9),
                                 width=10,
                                 bg=self.colors["entry_bg"],
                                 fg=self.colors["fg_secondary"],
                                 insertbackground=self.colors["fg"],
                                 relief="flat",
                                 highlightthickness=1,
                                 highlightbackground=self.colors["border"],
                                 highlightcolor=color)
            date_entry.pack(side="left", padx=(3, 0))
        
        # Fields
        for field_info in fields:
            label = field_info[0]
            var = field_info[1]
            hint = field_info[2] if len(field_info) > 2 else None
            
            field_frame = tk.Frame(content, bg=self.colors["bg_card"])
            field_frame.pack(fill="x", pady=2)
            
            lbl = tk.Label(field_frame, text=label,
                          font=("Segoe UI", 9),
                          bg=self.colors["bg_card"],
                          fg=self.colors["fg_secondary"])
            lbl.pack(anchor="w")
            
            entry = tk.Entry(field_frame,
                            textvariable=var,
                            font=("Segoe UI", 11),
                            bg=self.colors["entry_bg"],
                            fg=self.colors["fg"],
                            insertbackground=self.colors["fg"],
                            relief="flat",
                            highlightthickness=1,
                            highlightbackground=self.colors["border"],
                            highlightcolor=color)
            entry.pack(fill="x", pady=(2, 0), ipady=4)
            entry.bind("<Return>", lambda e: self.calculate())
            
            if hint:
                hint_lbl = tk.Label(field_frame, text=hint,
                                   font=("Segoe UI", 8),
                                   bg=self.colors["bg_card"],
                                   fg=self.colors["fg_secondary"])
                hint_lbl.pack(anchor="w")
    
    def _create_input_field(self, parent, label: str, var: tk.StringVar, is_main: bool = False):
        """Create input field with label"""
        frame = tk.Frame(parent, bg=self.colors["bg_secondary"])
        frame.pack(fill="x", pady=5)
        
        lbl = tk.Label(frame, text=label,
                      font=("Segoe UI", 11 if is_main else 9),
                      bg=self.colors["bg_secondary"],
                      fg=self.colors["fg"] if is_main else self.colors["fg_secondary"])
        lbl.pack(anchor="w")
        
        entry = tk.Entry(frame,
                        textvariable=var,
                        font=("Segoe UI", 16 if is_main else 11, "bold" if is_main else "normal"),
                        bg=self.colors["entry_bg"],
                        fg=self.colors["fg"],
                        insertbackground=self.colors["fg"],
                        relief="flat",
                        highlightthickness=2,
                        highlightbackground=self.colors["border"],
                        highlightcolor=self.colors["accent"])
        entry.pack(fill="x", pady=(3, 0), ipady=8 if is_main else 5)
        
        entry.bind("<Return>", lambda e: self.calculate())
    
    def _create_results_panel(self, parent):
        """Create results panel"""
        self.results_panel = tk.Frame(parent, bg=self.colors["bg_secondary"], padx=15, pady=15)
        self.results_panel.pack(fill="both", expand=True)
        
        # Title
        title = tk.Label(self.results_panel, text="📋 РЕЗУЛЬТАТЫ СРАВНЕНИЯ",
                        font=("Segoe UI", 14, "bold"),
                        bg=self.colors["bg_secondary"],
                        fg=self.colors["fg"])
        title.pack(anchor="w", pady=(0, 15))
        
        # Results container
        self.results_container = tk.Frame(self.results_panel, bg=self.colors["bg_secondary"])
        self.results_container.pack(fill="both", expand=True)
    
    def _create_chart_panel(self, parent):
        """Create chart panel"""
        self.chart_panel = tk.Frame(parent, bg=self.colors["bg_secondary"], padx=15, pady=15)
        self.chart_panel.pack(fill="both", expand=True)
        
        # Title
        title = tk.Label(self.chart_panel, text="📊 ВИЗУАЛИЗАЦИЯ",
                        font=("Segoe UI", 14, "bold"),
                        bg=self.colors["bg_secondary"],
                        fg=self.colors["fg"])
        title.pack(anchor="w", pady=(0, 15))
        
        # Chart container
        self.chart_container = tk.Frame(self.chart_panel, bg=self.colors["bg_secondary"])
        self.chart_container.pack(fill="both", expand=True)
    
    def _create_recommendation_banner(self, parent):
        """Create recommendation banner"""
        self.banner = tk.Frame(parent, bg=self.colors["bg_card"], height=100)
        self.banner.pack(fill="x", pady=(10, 0))
        self.banner.pack_propagate(False)
        
        # Configure border
        self.banner.configure(highlightthickness=3, highlightbackground=self.colors["accent"])
        
        # Icon
        self.banner_icon = tk.Label(self.banner, text="👑",
                                   font=("Segoe UI", 40),
                                   bg=self.colors["bg_card"])
        self.banner_icon.pack(side="left", padx=20, pady=15)
        
        # Text container
        text_frame = tk.Frame(self.banner, bg=self.colors["bg_card"])
        text_frame.pack(side="left", fill="both", expand=True, pady=15)
        
        # Main recommendation
        self.banner_title = tk.Label(text_frame,
                                    text="РАССЧИТАЙТЕ СУММУ",
                                    font=("Segoe UI", 22, "bold"),
                                    bg=self.colors["bg_card"],
                                    fg=self.colors["profit"])
        self.banner_title.pack(anchor="w")
        
        # Subtitle
        self.banner_subtitle = tk.Label(text_frame,
                                       text="Введите сумму в EUR и нажмите Рассчитать",
                                       font=("Segoe UI", 12),
                                       bg=self.colors["bg_card"],
                                       fg=self.colors["fg_secondary"])
        self.banner_subtitle.pack(anchor="w")
        
        # Savings
        self.banner_savings = tk.Label(self.banner,
                                      text="",
                                      font=("Segoe UI", 20, "bold"),
                                      bg=self.colors["bg_card"],
                                      fg=self.colors["accent"])
        self.banner_savings.pack(side="right", padx=30, pady=15)
    
    def _get_float(self, var: tk.StringVar, default: float = 0.0) -> float:
        """Safe float conversion"""
        try:
            return float(var.get().replace(',', '.'))
        except ValueError:
            return default
    
    def calculate(self):
        """Perform calculation and update UI"""
        # Get values
        spend_eur = self._get_float(self.amount_var, 100.0)
        nbg_rate = self._get_float(self.nbg_var, 3.1515)
        direct_rate = self._get_float(self.direct_var, 3.02)
        eur_usd = self._get_float(self.eur_usd_var, 1.16)
        usd_gel = self._get_float(self.usd_gel_var, 2.69)
        street_rate = self._get_float(self.street_var, 3.143)
        ibt_fee = self._get_float(self.ibt_fee_var, 1.5)
        atm_fee_pct = self._get_float(self.atm_fee_pct_var, 1.5)
        atm_fee_fix = self._get_float(self.atm_fee_fix_var, 1.0)
        
        if spend_eur <= 0:
            messagebox.showwarning("Ошибка", "Введите корректную сумму!")
            return
        
        # Calculate scenarios
        nbg_ref = Calculator.calc_nbg_reference(spend_eur, nbg_rate)
        direct_gel = Calculator.calc_direct(spend_eur, direct_rate)
        transfer_gel = Calculator.calc_transfer(spend_eur, ibt_fee, eur_usd, usd_gel)
        cash_gel = Calculator.calc_cash(spend_eur, atm_fee_pct, atm_fee_fix, street_rate)
        
        # Calculate losses
        direct_loss = Calculator.calc_loss_percent(direct_gel, nbg_ref)
        transfer_loss = Calculator.calc_loss_percent(transfer_gel, nbg_ref)
        cash_loss = Calculator.calc_loss_percent(cash_gel, nbg_ref)
        
        # Store results
        self.results = {
            "nbg": nbg_ref,
            "direct": {"gel": direct_gel, "loss": direct_loss, "name": "💳 Прямая оплата IBT"},
            "transfer": {"gel": transfer_gel, "loss": transfer_loss, "name": "📲 Перевод IBT→Credo"},
            "cash": {"gel": cash_gel, "loss": cash_loss, "name": "💵 Наличные (ATM+Обменник)"},
        }
        
        # Find winner
        winner_key = max(["direct", "transfer", "cash"], 
                        key=lambda k: self.results[k]["gel"])
        
        # Update UI
        self._update_results_table(winner_key)
        self._update_chart()
        self._update_banner(winner_key, spend_eur)
        
        # Save settings
        self._save_current_settings()
    
    def _update_results_table(self, winner_key: str):
        """Update results table"""
        # Clear previous
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        # Header
        header = tk.Frame(self.results_container, bg=self.colors["bg_card"])
        header.pack(fill="x", pady=(0, 5))
        
        headers = ["Метод", f"Получите ({self.country['local_currency']})", "Потери (%)", f"Потери ({self.country['local_currency']})"]
        for i, h in enumerate(headers):
            lbl = tk.Label(header, text=h,
                          font=("Segoe UI", 10, "bold"),
                          bg=self.colors["bg_card"],
                          fg=self.colors["fg_secondary"],
                          width=18 if i == 0 else 12)
            lbl.pack(side="left", padx=5, pady=8)
        
        # Central Bank Reference row (dynamic)
        ref_row = tk.Frame(self.results_container, bg=self.colors["border"])
        ref_row.pack(fill="x", pady=2)
        
        tk.Label(ref_row, text=f"🏛️ Эталон ({self.country['central_bank']})",
                font=("Segoe UI", 10),
                bg=self.colors["border"],
                fg=self.colors["fg_secondary"],
                width=18).pack(side="left", padx=5, pady=8)
        tk.Label(ref_row, text=f"{self.results['nbg']:.2f}",
                font=("Segoe UI", 10, "bold"),
                bg=self.colors["border"],
                fg=self.colors["accent"],
                width=12).pack(side="left", padx=5, pady=8)
        tk.Label(ref_row, text="0.00%",
                bg=self.colors["border"],
                fg=self.colors["fg_secondary"],
                width=12).pack(side="left", padx=5, pady=8)
        tk.Label(ref_row, text="—",
                bg=self.colors["border"],
                fg=self.colors["fg_secondary"],
                width=12).pack(side="left", padx=5, pady=8)
        
        # Data rows
        for key in ["direct", "transfer", "cash"]:
            data = self.results[key]
            is_winner = (key == winner_key)
            
            row_bg = self.colors["profit"] if is_winner else self.colors["bg_card"]
            text_fg = "#000000" if is_winner else self.colors["fg"]
            
            row = tk.Frame(self.results_container, bg=row_bg,
                          highlightthickness=2 if is_winner else 0,
                          highlightbackground=self.colors["profit"])
            row.pack(fill="x", pady=2)
            
            # Name
            name_text = data["name"] + (" 👑" if is_winner else "")
            tk.Label(row, text=name_text,
                    font=("Segoe UI", 10, "bold" if is_winner else "normal"),
                    bg=row_bg,
                    fg=text_fg,
                    width=18,
                    anchor="w").pack(side="left", padx=5, pady=12)
            
            # Amount received
            tk.Label(row, text=f"{data['gel']:.2f} {self.country['local_symbol']}",
                    font=("Segoe UI", 12, "bold"),
                    bg=row_bg,
                    fg=text_fg,
                    width=12).pack(side="left", padx=5, pady=12)
            
            # Loss %
            loss_fg = self.colors["loss"] if not is_winner else text_fg
            tk.Label(row, text=f"-{data['loss']:.2f}%",
                    font=("Segoe UI", 10),
                    bg=row_bg,
                    fg=loss_fg,
                    width=12).pack(side="left", padx=5, pady=12)
            
            # Loss in local currency
            loss_gel = self.results["nbg"] - data["gel"]
            tk.Label(row, text=f"-{loss_gel:.2f} {self.country['local_symbol']}",
                    font=("Segoe UI", 10),
                    bg=row_bg,
                    fg=loss_fg,
                    width=12).pack(side="left", padx=5, pady=12)
    
    def _update_chart(self):
        """Update chart"""
        for widget in self.chart_container.winfo_children():
            widget.destroy()
        
        if HAS_MATPLOTLIB:
            self._draw_matplotlib_chart()
        else:
            self._draw_text_chart()
    
    def _draw_matplotlib_chart(self):
        """Draw improved horizontal bar chart with loss percentages"""
        fig = Figure(figsize=(5, 4), dpi=100)
        fig.patch.set_facecolor(self.colors["bg_secondary"])
        
        ax = fig.add_subplot(111)
        ax.set_facecolor(self.colors["bg_secondary"])
        
        # Data - only 3 methods (not NBG reference)
        methods = ["💳 Карта IBT", "📲 Перевод", "💵 Наличные"]
        values = [
            self.results["direct"]["gel"],
            self.results["transfer"]["gel"],
            self.results["cash"]["gel"],
        ]
        losses = [
            self.results["direct"]["loss"],
            self.results["transfer"]["loss"],
            self.results["cash"]["loss"],
        ]
        
        # Find winner
        max_val = max(values)
        
        # Colors based on winner
        bar_colors = []
        for v in values:
            if v == max_val:
                bar_colors.append(self.colors["profit"])
            elif v == min(values):
                bar_colors.append(self.colors["loss"])
            else:
                bar_colors.append(self.colors["warning"])
        
        # Horizontal bars
        y_pos = range(len(methods))
        bars = ax.barh(y_pos, values, color=bar_colors, edgecolor='white', 
                       linewidth=1, height=0.6)
        
        # Add NBG reference line
        ax.axvline(x=self.results["nbg"], color=self.colors["accent"], 
                   linestyle='--', linewidth=2, alpha=0.8, label=f'Эталон {self.country["central_bank"]}')
        
        # Value labels on bars
        for i, (bar, val, loss) in enumerate(zip(bars, values, losses)):
            width = bar.get_width()
            # Value inside bar
            ax.text(width - (width * 0.02), bar.get_y() + bar.get_height()/2,
                   f'{val:.1f} {self.country["local_symbol"]}',
                   ha='right', va='center',
                   fontsize=11, fontweight='bold',
                   color='white' if val == max_val else self.colors["fg"])
            # Loss percentage outside bar
            loss_color = self.colors["loss"] if loss > 2 else self.colors["fg_secondary"]
            ax.text(width + 5, bar.get_y() + bar.get_height()/2,
                   f'-{loss:.1f}%',
                   ha='left', va='center',
                   fontsize=9,
                   color=loss_color)
        
        # NBG value annotation
        ax.text(self.results["nbg"] + 5, len(methods) - 0.5,
               f'{self.country["central_bank"]}: {self.results["nbg"]:.1f}',
               fontsize=9, color=self.colors["accent"])
        
        # Styling
        ax.set_yticks(y_pos)
        ax.set_yticklabels(methods, fontsize=10)
        ax.set_xlabel(self.country['local_currency'], fontsize=10, color=self.colors["fg"])
        ax.tick_params(colors=self.colors["fg"], labelsize=9)
        ax.spines['bottom'].set_color(self.colors["border"])
        ax.spines['left'].set_color(self.colors["border"])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.invert_yaxis()  # Best at top
        
        # Set x-axis to start from 90% of min value for better visualization
        min_val = min(values) * 0.95
        ax.set_xlim(min_val, self.results["nbg"] * 1.05)
        
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
    
    def _draw_text_chart(self):
        """Draw Apple-style card visualization"""
        # Header with subtle styling
        header_frame = tk.Frame(self.chart_container, bg=self.colors["bg_secondary"])
        header_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(header_frame, 
                text="Сравнение методов",
                font=("Segoe UI", 13, "bold"),
                bg=self.colors["bg_secondary"],
                fg=self.colors["fg"]).pack(side="left")
        
        tk.Label(header_frame,
                text=self.country['local_currency'],
                font=("Segoe UI", 11),
                bg=self.colors["bg_secondary"],
                fg=self.colors["fg_secondary"]).pack(side="right")
        
        # Method cards data
        methods_data = [
            ("💳", "Карта IBT", "Прямая оплата", 
             self.results["direct"]["gel"], self.results["direct"]["loss"], 
             self.colors.get("chart_bar_1", self.colors["loss"])),
            ("📲", "Перевод Credo", "Через приложение", 
             self.results["transfer"]["gel"], self.results["transfer"]["loss"],
             self.colors.get("chart_bar_2", self.colors["warning"])),
            ("💵", "Наличные", "ATM + Обменник", 
             self.results["cash"]["gel"], self.results["cash"]["loss"],
             self.colors.get("chart_bar_3", self.colors["profit"])),
        ]
        
        max_val = max(d[3] for d in methods_data)
        nbg_val = self.results["nbg"]
        
        for icon, name, subtitle, val, loss, default_color in methods_data:
            is_best = val == max_val
            is_worst = val == min(d[3] for d in methods_data)
            
            # Choose color based on position
            if is_best:
                bar_color = self.colors["profit"]
                badge_text = "✓ ЛУЧШИЙ"
                badge_color = self.colors["profit"]
            elif is_worst:
                bar_color = self.colors["loss"]
                badge_text = "✗ ХУДШИЙ"
                badge_color = self.colors["loss"]
            else:
                bar_color = self.colors["warning"]
                badge_text = ""
                badge_color = None
            
            # Card container
            card = tk.Frame(self.chart_container, 
                           bg=self.colors["bg_card"],
                           highlightthickness=1,
                           highlightbackground=self.colors["border"])
            card.pack(fill="x", pady=6, ipady=12, ipadx=12)
            
            # Left side: Icon + Text
            left_frame = tk.Frame(card, bg=self.colors["bg_card"])
            left_frame.pack(side="left", fill="y", padx=(10, 15))
            
            # Icon in colored circle
            icon_lbl = tk.Label(left_frame, text=icon,
                               font=("Segoe UI Emoji", 20),
                               bg=self.colors["bg_card"],
                               fg=self.colors["fg"])
            icon_lbl.pack(side="left", padx=(0, 10))
            
            # Name and subtitle
            text_frame = tk.Frame(left_frame, bg=self.colors["bg_card"])
            text_frame.pack(side="left")
            
            tk.Label(text_frame, text=name,
                    font=("Segoe UI", 12, "bold"),
                    bg=self.colors["bg_card"],
                    fg=self.colors["fg"]).pack(anchor="w")
            
            tk.Label(text_frame, text=subtitle,
                    font=("Segoe UI", 9),
                    bg=self.colors["bg_card"],
                    fg=self.colors["fg_secondary"]).pack(anchor="w")
            
            # Right side: Value + Progress
            right_frame = tk.Frame(card, bg=self.colors["bg_card"])
            right_frame.pack(side="right", fill="y", padx=(10, 25))
            
            # Value
            val_frame = tk.Frame(right_frame, bg=self.colors["bg_card"])
            val_frame.pack(anchor="e")
            
            tk.Label(val_frame, text=f"{val:.2f}",
                    font=("Segoe UI", 16, "bold"),
                    bg=self.colors["bg_card"],
                    fg=bar_color).pack(side="left")
            
            tk.Label(val_frame, text=f" {self.country['local_symbol']}",
                    font=("Segoe UI", 12),
                    bg=self.colors["bg_card"],
                    fg=self.colors["fg_secondary"]).pack(side="left")
            
            # Loss percentage
            loss_text = f"-{loss:.1f}% от {self.country['central_bank']}"
            loss_color = self.colors["loss"] if loss > 2 else self.colors["fg_secondary"]
            tk.Label(right_frame, text=loss_text,
                    font=("Segoe UI", 9),
                    bg=self.colors["bg_card"],
                    fg=loss_color).pack(anchor="e")
            
            # Progress bar (iOS style - NBG = 100%)
            progress_frame = tk.Frame(card, bg=self.colors["bg_card"])
            progress_frame.pack(side="right", fill="y", padx=10, pady=5)
            
            # Background track (this represents 100% = NBG)
            track_width = 140
            track_height = 10
            track = tk.Canvas(progress_frame, 
                             width=track_width, height=track_height,
                             bg=self.colors["bg_card"], 
                             highlightthickness=0)
            track.pack(pady=5)
            
            # Draw full track background (represents NBG = 100%)
            track.create_rectangle(0, 0, track_width, track_height,
                                  fill=self.colors["border"], 
                                  outline="")
            
            # Progress fill (percentage of NBG)
            progress_pct = min(val / nbg_val, 1.0) if nbg_val > 0 else 0
            fill_width = int(track_width * progress_pct)
            
            # Fill the achieved amount
            track.create_rectangle(0, 0, fill_width, track_height,
                                  fill=bar_color, 
                                  outline="")
            
            # Show loss gap (the part we're losing)
            if fill_width < track_width:
                # Darker area showing loss gap
                loss_gap_color = "#3a2020" if self.current_theme == "dark" else "#ffcccc"
                track.create_rectangle(fill_width, 0, track_width, track_height,
                                      fill=loss_gap_color,
                                      outline="")
            
            # Percentage label below bar
            pct_text = f"{progress_pct*100:.1f}%"
            tk.Label(progress_frame, text=pct_text,
                    font=("Segoe UI", 8),
                    bg=self.colors["bg_card"],
                    fg=bar_color).pack()
            
            # Badge for best/worst
            if badge_text:
                badge_frame = tk.Frame(card, bg=self.colors["bg_card"])
                badge_frame.pack(side="right", padx=5)
                
                tk.Label(badge_frame, text=badge_text,
                        font=("Segoe UI", 8, "bold"),
                        bg=self.colors["bg_card"],
                        fg=badge_color).pack()
        
        # NBG Reference bar (100% full - the benchmark)
        ref_card = tk.Frame(self.chart_container, 
                           bg=self.colors["bg_card"],
                           highlightthickness=1,
                           highlightbackground=self.colors["accent"])
        ref_card.pack(fill="x", pady=(15, 0), ipady=10, ipadx=10)
        
        ref_left = tk.Frame(ref_card, bg=self.colors["bg_card"])
        ref_left.pack(side="left", padx=10)
        
        tk.Label(ref_left, text="🏛️",
                font=("Segoe UI Emoji", 16),
                bg=self.colors["bg_card"]).pack(side="left", padx=(0, 8))
        
        ref_text = tk.Frame(ref_left, bg=self.colors["bg_card"])
        ref_text.pack(side="left")
        
        tk.Label(ref_text, text=f"Эталон {self.country['central_bank']}",
                font=("Segoe UI", 11, "bold"),
                bg=self.colors["bg_card"],
                fg=self.colors["accent"]).pack(anchor="w")
        
        tk.Label(ref_text, text=self.country['central_bank_full'],
                font=("Segoe UI", 8),
                bg=self.colors["bg_card"],
                fg=self.colors["fg_secondary"]).pack(anchor="w")
        
        # NBG value and 100% bar
        ref_right = tk.Frame(ref_card, bg=self.colors["bg_card"])
        ref_right.pack(side="right", padx=(10, 25))
        
        tk.Label(ref_right, text=f"{nbg_val:.2f} {self.country['local_symbol']}",
                font=("Segoe UI", 14, "bold"),
                bg=self.colors["bg_card"],
                fg=self.colors["accent"]).pack(anchor="e")
        
        # Full progress bar for NBG
        ref_bar_frame = tk.Frame(ref_card, bg=self.colors["bg_card"])
        ref_bar_frame.pack(side="right", padx=10)
        
        ref_track = tk.Canvas(ref_bar_frame, 
                             width=140, height=10,
                             bg=self.colors["bg_card"], 
                             highlightthickness=0)
        ref_track.pack()
        
        # Full blue bar = 100%
        ref_track.create_rectangle(0, 0, 140, 10,
                                  fill=self.colors["accent"], 
                                  outline="")
        
        tk.Label(ref_bar_frame, text="100%",
                font=("Segoe UI", 8, "bold"),
                bg=self.colors["bg_card"],
                fg=self.colors["accent"]).pack()
    
    def _update_banner(self, winner_key: str, spend_eur: float):
        """Update recommendation banner"""
        winner = self.results[winner_key]
        
        all_values = [self.results[k]["gel"] for k in ["direct", "transfer", "cash"]]
        min_val = min(all_values)
        savings = winner["gel"] - min_val
        
        if winner_key == "cash":
            title = "💵 СНИМАЙТЕ НАЛИЧНЫЕ!"
            subtitle = f"Идите в {self.country['street_exchange']}. Это выгоднее на {savings:.2f} {self.country['local_currency']}"
            icon = "🏆"
            color = self.colors["profit"]
        elif winner_key == "transfer":
            title = "📲 ПЕРЕВОДИТЕ В CREDO!"
            subtitle = f"Используйте приложение IBT. Экономия {savings:.2f} {self.country['local_currency']}"
            icon = "📱"
            color = self.colors["warning"]
        else:
            title = "💳 ПЛАТИТЕ КАРТОЙ IBT"
            subtitle = "Странно, но прямая оплата выгоднее (проверьте курсы)"
            icon = "🤔"
            color = self.colors["accent"]
        
        self.banner_icon.configure(text=icon)
        self.banner_title.configure(text=title, fg=color)
        self.banner_subtitle.configure(text=subtitle)
        self.banner_savings.configure(text=f"+{winner['gel']:.2f} {self.country['local_symbol']}", fg=color)
        self.banner.configure(highlightbackground=color)
    
    def _save_current_settings(self):
        """Save current settings"""
        self.settings.set("last_amount", self._get_float(self.amount_var))
        self.settings.set("nbg_rate", self._get_float(self.nbg_var))
        self.settings.set("eur_usd_rate", self._get_float(self.eur_usd_var))
        self.settings.set("usd_gel_rate", self._get_float(self.usd_gel_var))
        self.settings.set("street_rate", self._get_float(self.street_var))
        self.settings.set("direct_implied_rate", self._get_float(self.direct_var))
        self.settings.set("ibt_transfer_fee", self._get_float(self.ibt_fee_var))
        self.settings.set("atm_fee_pct", self._get_float(self.atm_fee_pct_var))
        self.settings.set("atm_fee_fix", self._get_float(self.atm_fee_fix_var))
        self.settings.set("theme", self.current_theme)
        # Save dates
        self.settings.set("nbg_date", self.nbg_date_var.get())
        self.settings.set("direct_date", self.direct_date_var.get())
        self.settings.set("transfer_date", self.transfer_date_var.get())
        self.settings.set("cash_date", self.cash_date_var.get())
        self.settings.save()
    
    def _fetch_nbg_rates(self):
        """Fetch all available rates automatically"""
        c = self.country
        
        # Check if API is available for current country
        if not c.get("central_bank_api"):
            messagebox.showwarning(
                "API недоступен",
                f"Для {c['name']} автоматическая загрузка курсов пока не реализована.\n"
                f"Введите курс {c['central_bank']} вручную."
            )
            return
        
        # Currently only NBG (Georgia) full API automation is implemented
        if self.country_key != "georgia":
            messagebox.showwarning(
                "API в разработке",
                f"Автоматизация для {c['name']} пока не реализована.\n"
                f"Поддерживается только Грузия."
            )
            return
        
        self.banner_title.configure(text="⏳ Загрузка всех курсов...", 
                                   fg=self.colors["warning"])
        self.root.update()
        
        rates = RateFetcher.fetch_georgia_rates()
        success = []
        
        if rates:
            if "EUR" in rates:
                self.nbg_var.set(str(round(rates["EUR"], 4)))
                success.append(f"✅ {c['central_bank']}: 1 EUR = {rates['EUR']:.4f} {c['local_currency']}")
                
            if "street_eur" in rates:
                self.street_var.set(str(round(rates["street_eur"], 4)))
                success.append(f"🏦 Обменник: {rates['street_eur']:.4f}")
                
            if "credo_usd" in rates:
                self.usd_gel_var.set(str(round(rates["credo_usd"], 4)))
                success.append(f"💵 Credo (USD): {rates['credo_usd']:.4f}")
                
            if "eur_usd" in rates:
                self.eur_usd_var.set(str(round(rates["eur_usd"], 4)))
                success.append(f"🌍 EUR/USD кросс-курс: {rates['eur_usd']:.4f}")
                
            # Если не удалось получить EUR/USD, но есть курсы НБГ, считаем implied
            if "eur_usd" not in rates and "EUR" in rates and "USD" in rates:
                implied_eur_usd = rates["EUR"] / rates["USD"]
                self.eur_usd_var.set(str(round(implied_eur_usd, 4)))
                success.append(f"💡 Расчетный EUR/USD: {implied_eur_usd:.4f}")
        
        if success:
            messagebox.showinfo("Авто-обновление", "\n".join(success))
            self.calculate()
        else:
            messagebox.showerror(
                "Ошибка API",
                "Не удалось загрузить курсы.\n"
                "Проверьте интернет-соединение!"
            )
            self.banner_title.configure(text="❌ Ошибка загрузки", 
                                        fg=self.colors["loss"])
    
    def _toggle_theme(self):
        """Toggle between dark and light theme"""
        self.current_theme = "light" if self.current_theme == "dark" else "dark"
        self._save_current_settings()
        
        # Rebuild UI
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self._apply_theme()
        self._create_ui()
        self.calculate()
    
    def _on_closing(self):
        """Handle window close"""
        self._save_current_settings()
        self.root.destroy()

# ==============================================================================
# ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    # Fallback to pure tkinter if needed
    root = tk.Tk()
    app = CurrencyCalculatorApp(root)
    root.mainloop()

"""Конфигурация системы мониторинга."""
from pathlib import Path
from datetime import datetime

# === ПУТИ ===
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
HISTORY_FILE = DATA_DIR / "history.json"
REPORT_FILE = BASE_DIR / "REPORT.md"

# === ИСТОЧНИКИ ДАННЫХ (дефолтные, можно переопределять) ===
RSS_FEEDS = [
    "https://www.merkur.de/rssfeed.rdf",
    "https://www.tz.de/rssfeed.rdf",
    "https://rss.dw.com/xml/rss-ru-all",
]

DORK_TEMPLATES = {
    "crime": [
        'site:twitter.com "{location}" (polizei OR polizey OR criminal OR grabizh OR napad)',
        '"{location}" (Polizeibericht OR Einbruch OR Vandalismus OR zlochyn)',
    ],
    "business": [
        '"{location}" (Miete OR Gewerbefläche OR Leerstand OR orenda OR zakryttia)',
    ],
    "infrastructure": [
        '"{location}" (Straßenbau OR Sanierung OR Umleitung OR budivnytstvo OR remount)',
    ],
}

# === LLM НАСТРОЙКИ ===
GROQ_API_KEY = "YOUR_GROQ_API_KEY_HERE"  # Замени на свой ключ!
GROQ_MODEL = "llama-3.3-70b-versatile"

# === БЕЗОПАСНОСТЬ ===
REQUEST_DELAY = 3
TIMEOUT = 30

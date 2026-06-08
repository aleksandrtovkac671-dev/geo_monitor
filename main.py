"""Главный скрипт с CLI: --search и --analysis."""
import asyncio
import argparse
import logging
import re
from datetime import datetime
from transliterate import translit
import config
from collectors.rss_collector import RSSCollector
from collectors.dork_collector import DorkCollector
from analyzers.state_manager import StateManager
from analyzers.llm_analyzer import LLMAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def slugify(text):
    """Превращает 'Киев грабеж' в 'kyiv_grabizh'."""
    try:
        latin = translit(text, 'uk', reversed=True)
    except Exception:
        latin = text
    slug = re.sub(r'[^\w\s-]', '', latin).strip().lower()
    return re.sub(r'[\s\-]+', '_', slug)[:40]


def parse_args():
    parser = argparse.ArgumentParser(description="GeoMonitor OSINT Tool")
    parser.add_argument("--search", type=str, help="Поиск и сохранение снапшота по запросу")
    parser.add_argument("--analysis", type=str, help="LLM-анализ изменений по запросу")
    parser.add_argument("--from-date", type=str, help="Начальная дата (YYYY-MM-DD)")
    parser.add_argument("--to-date", type=str, help="Конечная дата (YYYY-MM-DD)")
    return parser.parse_args()


async def run_search(query):
    """Сбор данных и сохранение снапшота."""
    config.LOCATION_QUERY = query
    slug = slugify(query)
    date_str = datetime.now().strftime('%Y-%m-%d')
    
    # Человеческое имя файла
    snapshot_name = f"{slug}_{date_str}.json"
    config.SNAPSHOT_FILE = config.DATA_DIR / snapshot_name
    
    logger.info(f"🔍 Поиск: {query}")
    logger.info(f"💾 Файл: {snapshot_name}")
    
    sm = StateManager(config)
    data = {}
    
    # RSS
    try:
        rss = RSSCollector(config)
        data['rss'] = await rss.collect(config.RSS_FEEDS)
    except Exception as e:
        logger.error(f"❌ RSS: {e}")
    
    # Dorks
    try:
        dork = DorkCollector(config)
        data['dorks'] = await dork.collect(config.DORK_TEMPLATES)
    except Exception as e:
        logger.error(f"❌ Dorks: {e}")
    
    sm.save_snapshot(data)
    logger.info("✅ Снапшот сохранён!")


async def run_analysis(query):
    """LLM-анализ двух последних снапшотов."""
    config.LOCATION_QUERY = query
    sm = StateManager(config)
    
    snap1, snap2 = sm.get_last_two_snapshots()
    if not snap1 or not snap2:
        logger.warning("⚠️ Нужно минимум 2 снапшота для анализа. Сначала запусти --search дважды.")
        return
    
    logger.info(f"🧠 Анализ изменений по запросу: {query}")
    
    analyzer = LLMAnalyzer(config)
    result = await analyzer.analyze_changes(snap1, snap2)
    
    if result:
        print("\n" + "=" * 60)
        print(result)
        print("=" * 60)
        analyzer.save_report(result, config.REPORT_FILE)
    else:
        logger.error("❌ LLM-анализ не удался")


if __name__ == "__main__":
    args = parse_args()
    
    if args.search:
        asyncio.run(run_search(args.search))
    elif args.analysis:
        asyncio.run(run_analysis(args.analysis))
    else:
        print("Использование:")
        print("  python main.py --search 'Киев грабеж'")
        print("  python main.py --analysis 'Киев грабеж'")

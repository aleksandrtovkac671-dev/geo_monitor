"""Сборщик RSS-лент новостей."""
import asyncio
import aiohttp
import feedparser
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class RSSCollector:
    """Собирает новости из RSS-лент."""
    
    def __init__(self, config):
        self.config = config
        self.location = config.LOCATION_QUERY.lower()
    
    async def fetch_feed(self, session, feed_url):
        """Парсит одну RSS-ленту."""
        try:
            async with session.get(feed_url, timeout=self.config.TIMEOUT) as resp:
                if resp.status != 200:
                    logger.warning(f"RSS {feed_url} вернул статус {resp.status}")
                    return []
                
                content = await resp.text()
                feed = feedparser.parse(content)
                
                articles = []
                for entry in feed.entries[:15]:
                    # Простая фильтрация по локации
                    text = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
                    if self.location in text or 'münchen' in text or 'munich' in text:
                        articles.append({
                            'title': entry.get('title', ''),
                            'link': entry.get('link', ''),
                            'published': entry.get('published', ''),
                            'summary': entry.get('summary', '')[:500],
                            'source': feed.feed.get('title', feed_url)
                        })
                
                logger.info(f"✅ {feed_url}: найдено {len(articles)} релевантных статей")
                return articles
        
        except Exception as e:
            logger.error(f"❌ Ошибка парсинга RSS {feed_url}: {e}")
            return []
    
    async def collect(self, feeds):
        """Собирает данные из всех указанных RSS-лент."""
        all_articles = []
        
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_feed(session, url) for url in feeds]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, list):
                    all_articles.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"Исключение в задаче RSS: {result}")
        
        return {
            'source': 'rss',
            'timestamp': datetime.now().isoformat(),
            'location': self.config.LOCATION_QUERY,
            'count': len(all_articles),
            'data': all_articles
        }

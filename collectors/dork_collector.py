"""Сборщик через поисковые дорки (Локальный SearXNG)."""
import asyncio
import aiohttp
from urllib.parse import quote_plus
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# ТОЛЬКО ЛОКАЛЬНЫЙ ИНСТАНС
SEARXNG_INSTANCES = ["http://localhost:8304"]

class DorkCollector:
    def __init__(self, config):
        self.config = config
        self.location = config.LOCATION_QUERY
        self.delay = config.REQUEST_DELAY
    
    async def search_searxng(self, session, query, instance_url):
        try:
            url = f"{instance_url}/search?q={quote_plus(query)}&format=json&categories=general"
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0',
                'Accept': 'application/json',
            }
            
            async with session.get(url, headers=headers, timeout=self.config.TIMEOUT) as resp:
                if resp.status != 200:
                    logger.warning(f"SearXNG вернул статус {resp.status}")
                    return None
                
                data = await resp.json()
                results = []
                for r in data.get('results', [])[:5]:
                    results.append({
                        'title': r.get('title', ''),
                        'url': r.get('url', ''),
                        'snippet': r.get('content', ''),
                        'query': query
                    })
                
                logger.info(f"✅ Найдено {len(results)} результатов")
                return results
        
        except Exception as e:
            logger.error(f"❌ Ошибка SearXNG: {e}")
            return None
    
    async def collect(self, dork_templates):
        all_results = {}
        
        async with aiohttp.ClientSession() as session:
            for category, templates in dork_templates.items():
                category_results = []
                
                for template in templates:
                    query = template.format(location=self.location)
                    result = await self.search_searxng(session, query, SEARXNG_INSTANCES[0])
                    if result:
                        category_results.extend(result)
                    await asyncio.sleep(self.delay)
                
                all_results[category] = category_results
                logger.info(f"📊 [{category}]: {len(category_results)} результатов")
        
        return {
            'source': 'dorks',
            'timestamp': datetime.now().isoformat(),
            'location': self.location,
            'data': all_results
        }

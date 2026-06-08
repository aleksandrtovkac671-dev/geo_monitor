"""LLM-анализатор через Groq API."""
import aiohttp
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class LLMAnalyzer:
    def __init__(self, config):
        self.config = config
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
    
    async def analyze_changes(self, snap1, snap2):
        prompt = f"""Ты старший OSINT-аналитик. Сравни два снапшота по локации "{self.config.LOCATION_QUERY}".

СНАПШОТ 1 (старый):
{json.dumps(snap1, ensure_ascii=False)[:3000]}

СНАПШОТ 2 (новый):
{json.dumps(snap2, ensure_ascii=False)[:3000]}

Задача:
1. Критические изменения (новые риски, инциденты, закрытия).
2. Тренд (хуже/лучше/стабильно).
3. Рекомендации: куда копать дальше, какие источники проверить.
4. Краткий вывод для принятия решений.

Ответь структурированно на русском в Markdown."""
        
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.config.GROQ_MODEL,
                    "messages": [
                        {"role": "system", "content": "Ты эксперт OSINT и геоаналитик."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "max_tokens": 2000,
                }
                headers = {
                    "Authorization": f"Bearer {self.config.GROQ_API_KEY}",
                    "Content-Type": "application/json",
                }
                
                async with session.post(self.api_url, headers=headers, json=payload, timeout=60) as resp:
                    if resp.status != 200:
                        logger.error(f"Groq API error: {await resp.text()}")
                        return None
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Ошибка LLM: {e}")
            return None
    
    def save_report(self, analysis, filepath):
        report = f"# 📊 Аналитический отчёт\n**Запрос:** {self.config.LOCATION_QUERY}\n**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n---\n\n{analysis}\n"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"📄 Отчёт сохранён: {filepath}")

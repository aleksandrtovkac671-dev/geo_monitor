"""Менеджер состояния и снапшотов."""
import json
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class StateManager:
    """Управляет историей снапшотов для анализа изменений."""
    
    def __init__(self, config):
        self.config = config
        self.history_file = config.HISTORY_FILE
    
    def save_snapshot(self, data):
        """Сохраняет текущий снапшот и обновляет историю."""
        # Сохраняем снапшот с уникальным именем
        snapshot_file = self.config.SNAPSHOT_FILE
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Снапшот сохранён: {snapshot_file.name}")
        
        # Обновляем историю
        history = self.load_history()
        history.append({
            'date': datetime.now().isoformat(),
            'file': str(snapshot_file),
            'summary': self._summarize(data),
        })
        
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def load_history(self):
        """Загружает историю снапшотов."""
        if not self.history_file.exists():
            return []
        with open(self.history_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_last_two_snapshots(self):
        """Возвращает два последних снапшота для LLM-анализа."""
        history = self.load_history()
        if len(history) < 2:
            logger.warning("Нужно минимум 2 снапшота для анализа")
            return None, None
        
        last_two = history[-2:]
        snapshots = []
        for entry in last_two:
            try:
                with open(entry['file'], 'r', encoding='utf-8') as f:
                    snapshots.append(json.load(f))
            except FileNotFoundError:
                logger.error(f"Файл снапшота не найден: {entry['file']}")
                return None, None
        
        return snapshots[0], snapshots[1]
    
    def _summarize(self, data):
        """Краткое резюме снапшота для истории."""
        summary = {}
        for source, content in data.items():
            if isinstance(content, dict) and 'data' in content:
                d = content['data']
                if isinstance(d, list):
                    summary[source] = len(d)
                elif isinstance(d, dict):
                    summary[source] = sum(len(v) if isinstance(v, list) else 0 for v in d.values())
        return summary

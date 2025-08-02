"""
Реализация отслеживания загруженных файлов
"""
import json
import os
from typing import List, Dict, Any
from interfaces import IDownloadTracker, ILogger


class JsonDownloadTracker(IDownloadTracker):
    """Отслеживание загруженных файлов через JSON файл"""
    
    def __init__(self, archive_file: str, logger: ILogger):
        self.archive_file = archive_file
        self.logger = logger
        self._downloaded_data = self._load_archive()
    
    def _load_archive(self) -> Dict[str, Any]:
        """Загрузить архив загруженных файлов"""
        if not os.path.exists(self.archive_file):
            self.logger.info(f"Файл архива {self.archive_file} не найден, создаем новый")
            return {"downloaded": {}}
        
        try:
            with open(self.archive_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.logger.info(f"Загружен архив с {len(data.get('downloaded', {}))} записями")
                return data
        except (json.JSONDecodeError, IOError) as e:
            self.logger.error(f"Ошибка при загрузке архива: {e}")
            return {"downloaded": {}}
    
    def _save_archive(self) -> None:
        """Сохранить архив загруженных файлов"""
        try:
            with open(self.archive_file, 'w', encoding='utf-8') as f:
                json.dump(self._downloaded_data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"Архив сохранен в {self.archive_file}")
        except IOError as e:
            self.logger.error(f"Ошибка при сохранении архива: {e}")
    
    def is_downloaded(self, video_id: str) -> bool:
        """Проверить, был ли файл уже загружен"""
        return video_id in self._downloaded_data.get("downloaded", {})
    
    def mark_as_downloaded(self, video_id: str, file_path: str) -> None:
        """Отметить файл как загруженный"""
        if "downloaded" not in self._downloaded_data:
            self._downloaded_data["downloaded"] = {}
        
        self._downloaded_data["downloaded"][video_id] = {
            "file_path": file_path,
            "download_date": str(datetime.now())
        }
        self._save_archive()
        self.logger.info(f"Файл {video_id} отмечен как загруженный")
    
    def get_downloaded_list(self) -> List[str]:
        """Получить список загруженных файлов"""
        return list(self._downloaded_data.get("downloaded", {}).keys())


# Импорт datetime для использования в классе
from datetime import datetime

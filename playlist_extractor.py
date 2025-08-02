"""
Реализация извлечения информации о плейлисте YouTube
"""
import yt_dlp
from typing import List, Dict, Any
from interfaces import IPlaylistExtractor, ILogger


class YouTubePlaylistExtractor(IPlaylistExtractor):
    """Извлечение информации о плейлисте YouTube с помощью yt-dlp"""
    
    def __init__(self, logger: ILogger):
        self.logger = logger
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,  # Получаем только метаданные без загрузки
        }
    
    def get_video_list(self, playlist_url: str) -> List[Dict[str, Any]]:
        """Получить список видео из плейлиста"""
        try:
            self.logger.info(f"Извлекаем информацию о плейлисте: {playlist_url}")
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)
                
                if not playlist_info or 'entries' not in playlist_info:
                    self.logger.error("Не удалось получить информацию о плейлисте")
                    return []
                
                videos = []
                for entry in playlist_info['entries']:
                    if entry:  # Проверяем, что entry не None
                        video_info = {
                            'id': entry.get('id', ''),
                            'title': entry.get('title', 'Неизвестное название'),
                            'url': entry.get('url', ''),
                            'duration': entry.get('duration', 0),
                            'uploader': entry.get('uploader', 'Неизвестный автор')
                        }
                        videos.append(video_info)
                
                self.logger.info(f"Найдено {len(videos)} видео в плейлисте")
                return videos
                
        except Exception as e:
            self.logger.error(f"Ошибка при извлечении плейлиста: {e}")
            return []

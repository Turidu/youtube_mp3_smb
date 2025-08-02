"""
Абстрактные интерфейсы для соблюдения принципов SOLID
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any


class IPlaylistExtractor(ABC):
    """Интерфейс для извлечения информации о плейлисте"""
    
    @abstractmethod
    def get_video_list(self, playlist_url: str) -> List[Dict[str, Any]]:
        """Получить список видео из плейлиста"""
        pass


class IDownloadTracker(ABC):
    """Интерфейс для отслеживания загруженных файлов"""
    
    @abstractmethod
    def is_downloaded(self, video_id: str) -> bool:
        """Проверить, был ли файл уже загружен"""
        pass
    
    @abstractmethod
    def mark_as_downloaded(self, video_id: str, file_path: str) -> None:
        """Отметить файл как загруженный"""
        pass
    
    @abstractmethod
    def get_downloaded_list(self) -> List[str]:
        """Получить список загруженных файлов"""
        pass


class IAudioDownloader(ABC):
    """Интерфейс для загрузки аудио"""
    
    @abstractmethod
    def download_audio(self, video_url: str, output_path: str) -> str:
        """Загрузить аудио файл"""
        pass


class IFileUploader(ABC):
    """Интерфейс для загрузки файлов на удаленный сервер"""
    
    @abstractmethod
    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Загрузить файл на удаленный сервер"""
        pass
    
    @abstractmethod
    def connect(self) -> bool:
        """Подключиться к удаленному серверу"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """Отключиться от удаленного сервера"""
        pass


class ILogger(ABC):
    """Интерфейс для логирования"""
    
    @abstractmethod
    def info(self, message: str) -> None:
        """Информационное сообщение"""
        pass
    
    @abstractmethod
    def error(self, message: str) -> None:
        """Сообщение об ошибке"""
        pass
    
    @abstractmethod
    def warning(self, message: str) -> None:
        """Предупреждение"""
        pass

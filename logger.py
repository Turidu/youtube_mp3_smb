"""
Реализация логгера для приложения
"""
import logging
from datetime import datetime
from interfaces import ILogger


class ConsoleLogger(ILogger):
    """Простой консольный логгер"""
    
    def __init__(self, name: str = "YouTubeMP3Downloader"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Создаем обработчик для консоли
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Создаем форматтер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # Добавляем обработчик к логгеру
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
    
    def info(self, message: str) -> None:
        """Информационное сообщение"""
        self.logger.info(message)
    
    def error(self, message: str) -> None:
        """Сообщение об ошибке"""
        self.logger.error(message)
    
    def warning(self, message: str) -> None:
        """Предупреждение"""
        self.logger.warning(message)

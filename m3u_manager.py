"""
Менеджер для создания и управления M3U плейлистами
"""
import os
from typing import List, Optional
import smbclient
from interfaces import ILogger


class M3UPlaylistManager:
    """Класс для создания и управления M3U плейлистами на SMB сервере"""
    
    def __init__(self, logger: ILogger):
        self.logger = logger
    
    def create_m3u_playlist(self, smb_config: dict, folder_path: str, playlist_name: str) -> bool:
        """
        Создать M3U плейлист на основе MP3 файлов в папке SMB
        
        Args:
            smb_config: Конфигурация SMB (server, share, username, password, domain)
            folder_path: Путь к папке с MP3 файлами на SMB сервере
            playlist_name: Имя M3U файла плейлиста
            
        Returns:
            True если плейлист успешно создан
        """
        try:
            server = smb_config['server']
            share = smb_config['share']
            username = smb_config['username']
            password = smb_config['password']
            domain = smb_config.get('domain', '')
            
            # Настраиваем подключение к SMB
            smbclient.ClientConfig(username=username, password=password, domain=domain)
            
            # Формируем пути
            base_path = f"\\\\{server}\\{share}"
            folder_full_path = os.path.join(base_path, folder_path).replace('/', '\\')
            playlist_full_path = os.path.join(folder_full_path, playlist_name).replace('/', '\\')
            
            self.logger.info(f"Создаем M3U плейлист: {playlist_name}")
            self.logger.info(f"Сканируем папку: {folder_full_path}")
            
            # Получаем список MP3 файлов в папке
            mp3_files = self._get_mp3_files_from_smb(folder_full_path)
            
            if not mp3_files:
                self.logger.warning(f"Не найдено MP3 файлов в папке {folder_path}")
                return False
            
            self.logger.info(f"Найдено {len(mp3_files)} MP3 файлов")
            
            # Удаляем существующий плейлист если есть
            if self._playlist_exists(playlist_full_path):
                self.logger.info(f"Удаляем существующий плейлист: {playlist_name}")
                smbclient.remove(playlist_full_path)
            
            # Создаем новый M3U плейлист
            m3u_content = self._generate_m3u_content(mp3_files)
            
            # Записываем M3U файл на SMB
            with smbclient.open_file(playlist_full_path, mode='w', encoding='utf-8') as f:
                f.write(m3u_content)
            
            self.logger.info(f"M3U плейлист успешно создан: {playlist_full_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при создании M3U плейлиста: {e}")
            return False
    
    def _get_mp3_files_from_smb(self, folder_path: str) -> List[str]:
        """
        Получить список MP3 файлов из папки на SMB сервере
        
        Args:
            folder_path: Полный путь к папке на SMB сервере
            
        Returns:
            Список имен MP3 файлов
        """
        try:
            files = smbclient.listdir(folder_path)
            mp3_files = [f for f in files if f.lower().endswith('.mp3')]
            
            # Сортируем файлы по алфавиту для консистентности
            mp3_files.sort()
            
            return mp3_files
            
        except Exception as e:
            self.logger.error(f"Ошибка при получении списка MP3 файлов: {e}")
            return []
    
    def _playlist_exists(self, playlist_path: str) -> bool:
        """
        Проверить существование плейлиста на SMB сервере
        
        Args:
            playlist_path: Полный путь к плейлисту
            
        Returns:
            True если плейлист существует
        """
        try:
            return smbclient.path.exists(playlist_path)
        except Exception:
            return False
    
    def _generate_m3u_content(self, mp3_files: List[str]) -> str:
        """
        Сгенерировать содержимое M3U плейлиста
        
        Args:
            mp3_files: Список имен MP3 файлов
            
        Returns:
            Содержимое M3U файла
        """
        lines = ["#EXTM3U"]
        
        for mp3_file in mp3_files:
            # Добавляем информацию о треке (можно расширить в будущем)
            lines.append(f"#EXTINF:-1,{os.path.splitext(mp3_file)[0]}")
            lines.append(mp3_file)
        
        return "\n".join(lines) + "\n"

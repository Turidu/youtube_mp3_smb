"""
Основной класс приложения для синхронизации MP3 из YouTube плейлиста на SMB диск
"""
import os
from typing import List, Dict, Any
from interfaces import (
    IPlaylistExtractor, IDownloadTracker, IAudioDownloader, 
    IFileUploader, ILogger
)
from m3u_manager import M3UPlaylistManager


class YouTubeMP3Synchronizer:
    """
    Основной класс для синхронизации MP3 файлов из YouTube плейлиста на SMB диск.
    Следует принципам SOLID: Single Responsibility, Open/Closed, Liskov Substitution,
    Interface Segregation, Dependency Inversion
    """
    
    def __init__(
        self,
        playlist_extractor: IPlaylistExtractor,
        download_tracker: IDownloadTracker,
        audio_downloader: IAudioDownloader,
        file_uploader: IFileUploader,
        logger: ILogger,
        temp_dir: str = "temp_downloads"
    ):
        """
        Инициализация синхронизатора с внедрением зависимостей
        
        Args:
            playlist_extractor: Экстрактор плейлиста
            download_tracker: Трекер загруженных файлов
            audio_downloader: Загрузчик аудио
            file_uploader: Загрузчик файлов на сервер
            logger: Логгер
            temp_dir: Временная директория для загрузок
        """
        self.playlist_extractor = playlist_extractor
        self.download_tracker = download_tracker
        self.audio_downloader = audio_downloader
        self.file_uploader = file_uploader
        self.logger = logger
        self.temp_dir = temp_dir
        self.m3u_manager = M3UPlaylistManager(logger)
        
        # Создаем временную директорию если она не существует
        os.makedirs(self.temp_dir, exist_ok=True)
    
    def sync(self) -> None:
        """Выполнить синхронизацию всех плейлистов"""
        from config import PLAYLISTS_CONFIG
        
        total_processed = 0
        total_successful = 0
        
        self.logger.info(f"Начинаем синхронизацию {len(PLAYLISTS_CONFIG)} плейлистов")
        
        for i, playlist_config in enumerate(PLAYLISTS_CONFIG, 1):
            playlist_url = playlist_config["url"]
            target_folder = playlist_config["folder"]
            description = playlist_config.get("description", "")
            smb_config = playlist_config["smb_config"]
            
            self.logger.info(f"[{i}/{len(PLAYLISTS_CONFIG)}] Обрабатываем плейлист: {description}")
            self.logger.info(f"URL: {playlist_url}")
            self.logger.info(f"Папка назначения: {target_folder}")
            
            # Подключаемся к SMB серверу для этого плейлиста
            if not self.file_uploader.connect(smb_config, target_folder):
                self.logger.error(f"Не удалось подключиться к SMB серверу {smb_config['server']}")
                continue
            
            try:
                # Получаем список видео из плейлиста
                videos = self.playlist_extractor.get_video_list(playlist_url)
                if not videos:
                    self.logger.warning(f"Плейлист пуст или недоступен: {playlist_url}")
                    continue
                
                self.logger.info(f"Найдено {len(videos)} видео в плейлисте")
                
                playlist_processed = 0
                playlist_successful = 0
                
                for video in videos:
                    video_id = video.get('id', '')
                    video_title = video.get('title', 'Неизвестное название')
                    video_url = video.get('url', '')
                    
                    if not video_id or not video_url:
                        self.logger.warning(f"Пропускаем видео с неполными данными: {video_title}")
                        continue
                    
                    # Проверяем, не загружено ли уже это видео
                    if self.download_tracker.is_downloaded(video_id):
                        self.logger.info(f"Видео уже загружено, пропускаем: {video_title}")
                        continue
                    
                    self.logger.info(f"Обрабатываем видео: {video_title}")
                    playlist_processed += 1
                    
                    # Скачиваем аудио
                    self.logger.info(f"Начинаем загрузку: {video_url}")
                    local_path = self.audio_downloader.download_audio(video_url, f"{self.temp_dir}/{video_title}.mp3")
                    
                    if not local_path:
                        self.logger.error(f"Не удалось скачать аудио: {video_title}")
                        continue
                    
                    # Загружаем файл на SMB сервер
                    remote_filename = os.path.basename(local_path)
                    if self.file_uploader.upload_file(local_path, remote_filename):
                        # Отмечаем как загруженный
                        self.download_tracker.mark_as_downloaded(video_id, local_path)
                        
                        # Удаляем временный файл
                        self._cleanup_temp_file(local_path)
                        
                        self.logger.info(f"Успешно обработано: {video_title}")
                        playlist_successful += 1
                    else:
                        self.logger.error(f"Не удалось загрузить файл на SMB сервер: {video_title}")
                    
                    # Удаляем временный файл
                    self._cleanup_temp_file(local_path)
                    
                total_processed += playlist_processed
                total_successful += playlist_successful
                
                self.logger.info(f"Плейлист '{description}' завершен. Обработано новых видео: {playlist_processed}, успешно: {playlist_successful}")
                
                # Создаем M3U плейлист если указан параметр playlist
                playlist_name = playlist_config.get("playlist", "")
                if playlist_name and playlist_name.strip():
                    self.logger.info(f"Создаем M3U плейлист: {playlist_name}")
                    if self.m3u_manager.create_m3u_playlist(smb_config, target_folder, playlist_name):
                        self.logger.info(f"M3U плейлист успешно создан: {playlist_name}")
                    else:
                        self.logger.warning(f"Не удалось создать M3U плейлист: {playlist_name}")
                else:
                    self.logger.debug("Параметр playlist не указан, пропускаем создание M3U плейлиста")
                
            except Exception as e:
                self.logger.error(f"Ошибка при обработке плейлиста '{description}': {e}")
            finally:
                # Отключаемся от SMB сервера
                self.file_uploader.disconnect()
        
        self.logger.info(f"Синхронизация завершена. Всего обработано новых видео: {total_processed}, успешно: {total_successful}")
        
        if total_successful == 0:
            self.logger.warning("[WARNING] No new files were synchronized!")
        
        self.logger.info("[SUCCESS] Synchronization completed successfully!")
    
    def synchronize_playlist(self, playlist_url: str) -> bool:
        """
        Синхронизировать плейлист: загрузить новые MP3 и отправить на SMB
        
        Args:
            playlist_url: URL плейлиста YouTube
            
        Returns:
            True если синхронизация прошла успешно
        """
        try:
            self.logger.info("Начинаем синхронизацию плейлиста")
            
            # 1. Получаем список видео из плейлиста
            videos = self.playlist_extractor.get_video_list(playlist_url)
            if not videos:
                self.logger.error("Не удалось получить список видео из плейлиста")
                return False
            
            # 2. Подключаемся к SMB серверу
            if not self.file_uploader.connect():
                self.logger.error("Не удалось подключиться к SMB серверу")
                return False
            
            try:
                # 3. Обрабатываем каждое видео
                success_count = 0
                total_new_videos = 0
                
                for video in videos:
                    video_id = video.get('id', '')
                    if not video_id:
                        continue
                    
                    # Проверяем, не загружали ли мы уже это видео
                    if self.download_tracker.is_downloaded(video_id):
                        self.logger.info(f"Видео уже загружено: {video.get('title', 'Неизвестное')}")
                        continue
                    
                    total_new_videos += 1
                    
                    # Загружаем и загружаем на SMB
                    if self._process_video(video):
                        success_count += 1
                
                self.logger.info(
                    f"Синхронизация завершена. Обработано новых видео: {total_new_videos}, "
                    f"успешно: {success_count}"
                )
                
                return success_count > 0 or total_new_videos == 0
                
            finally:
                # 4. Отключаемся от SMB сервера
                self.file_uploader.disconnect()
                
        except Exception as e:
            self.logger.error(f"Ошибка при синхронизации плейлиста: {e}")
            return False
    
    def _process_video(self, video: Dict[str, Any]) -> bool:
        """
        Обработать одно видео: загрузить MP3 и отправить на SMB
        
        Args:
            video: Информация о видео
            
        Returns:
            True если обработка прошла успешно
        """
        video_id = video.get('id', '')
        video_title = video.get('title', 'Неизвестное название')
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        
        try:
            self.logger.info(f"Обрабатываем видео: {video_title}")
            
            # 1. Загружаем MP3 файл
            safe_filename = self._create_safe_filename(video_title)
            local_path = os.path.join(self.temp_dir, f"{safe_filename}.mp3")
            
            downloaded_path = self.audio_downloader.download_audio(video_url, local_path)
            if not downloaded_path or not os.path.exists(downloaded_path):
                self.logger.error(f"Не удалось загрузить аудио для: {video_title}")
                return False
            
            # 2. Загружаем файл на SMB сервер
            remote_filename = os.path.basename(downloaded_path)
            if self.file_uploader.upload_file(downloaded_path, remote_filename):
                # 3. Отмечаем как загруженный
                self.download_tracker.mark_as_downloaded(video_id, downloaded_path)
                
                # 4. Удаляем временный файл
                self._cleanup_temp_file(downloaded_path)
                
                self.logger.info(f"Успешно обработано: {video_title}")
                return True
            else:
                self.logger.error(f"Не удалось загрузить файл на SMB сервер: {video_title}")
                self._cleanup_temp_file(downloaded_path)
                return False
                
        except Exception as e:
            self.logger.error(f"Ошибка при обработке видео {video_title}: {e}")
            return False
    
    def _create_safe_filename(self, title: str) -> str:
        """Создать безопасное имя файла"""
        # Заменяем недопустимые символы
        invalid_chars = '<>:"/\\|?*'
        safe_title = title
        for char in invalid_chars:
            safe_title = safe_title.replace(char, '_')
        
        # Ограничиваем длину
        if len(safe_title) > 100:
            safe_title = safe_title[:100]
        
        return safe_title.strip()
    
    def _cleanup_temp_file(self, file_path: str) -> None:
        """Удалить временный файл"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                self.logger.info(f"Временный файл удален: {file_path}")
        except Exception as e:
            self.logger.warning(f"Не удалось удалить временный файл {file_path}: {e}")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """
        Получить статус синхронизации
        
        Returns:
            Словарь со статистикой
        """
        downloaded_list = self.download_tracker.get_downloaded_list()
        return {
            "total_downloaded": len(downloaded_list),
            "downloaded_ids": downloaded_list
        }

"""
Реализация загрузки аудио из YouTube
"""
import os
import yt_dlp
from typing import Optional
from interfaces import IAudioDownloader, ILogger


class YouTubeAudioDownloader(IAudioDownloader):
    """Загрузка аудио из YouTube с помощью yt-dlp"""
    
    def __init__(self, download_options: dict, logger: ILogger):
        self.logger = logger
        self.download_options = download_options.copy()
    
    def download_audio(self, video_url: str, output_path: str) -> Optional[str]:
        """
        Загрузить аудио файл
        
        Args:
            video_url: URL видео для загрузки
            output_path: Путь для сохранения файла
            
        Returns:
            Путь к загруженному файлу или None в случае ошибки
        """
        try:
            # Создаем директорию если она не существует
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Настраиваем опции для конкретной загрузки
            ydl_opts = self.download_options.copy()
            
            self.logger.info(f"Начинаем загрузку: {video_url}")
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Получаем информацию о видео
                info = ydl.extract_info(video_url, download=False)
                if not info:
                    self.logger.error(f"Не удалось получить информацию о видео: {video_url}")
                    return None
                
                # Формируем безопасное имя файла
                safe_title = self._sanitize_filename(info.get('title', 'unknown'))
                
                # Проверяем, есть ли постпроцессор FFmpeg
                has_ffmpeg_processor = any(
                    pp.get('key') == 'FFmpegExtractAudio' 
                    for pp in ydl_opts.get('postprocessors', [])
                )
                
                if has_ffmpeg_processor:
                    # С FFmpeg - убираем .mp3 из пути, FFmpeg сам добавит
                    if output_path.endswith('.mp3'):
                        final_output_path = output_path[:-4]  # Убираем .mp3
                    else:
                        final_output_path = output_path
                    
                    # Заменяем %(title)s на безопасное имя
                    final_output_path = final_output_path.replace('%(title)s', safe_title)
                    final_output_path = final_output_path.replace('%(ext)s', '')
                    
                    # Ожидаемый путь после обработки FFmpeg
                    expected_output = final_output_path + '.mp3'
                else:
                    # Без FFmpeg - используем путь как есть
                    final_output_path = output_path.replace('%(title)s', safe_title)
                    final_output_path = final_output_path.replace('%(ext)s', 'mp3')
                    expected_output = final_output_path
                
                # Обновляем путь в опциях
                ydl_opts['outtmpl'] = final_output_path
                
                # Загружаем файл
                with yt_dlp.YoutubeDL(ydl_opts) as ydl_download:
                    ydl_download.download([video_url])
                
                # Проверяем, что файл был создан
                if os.path.exists(expected_output):
                    self.logger.info(f"Файл успешно загружен: {expected_output}")
                    return expected_output
                else:
                    self.logger.error(f"Файл не был создан: {expected_output}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке аудио: {e}")
            return None
    
    def _sanitize_filename(self, filename: str) -> str:
        """Очистить имя файла от недопустимых символов"""
        # Заменяем недопустимые символы
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Ограничиваем длину
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename.strip()

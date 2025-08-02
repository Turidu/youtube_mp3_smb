"""
Конфигурация приложения для загрузки MP3 из YouTube плейлиста
"""
import os
import subprocess
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройки загрузки
DOWNLOAD_ARCHIVE_FILE = "downloaded.json"
TEMP_DOWNLOAD_DIR = "temp_downloads"

# Конфигурация плейлистов с индивидуальными настройками SMB
# Каждый элемент содержит: URL плейлиста, настройки SMB и папку назначения
PLAYLISTS_CONFIG = [
    {
        "url": "https://www.youtube.com/playlist?list=PL3OB1-iYN3MPRgQY1kdHJP5aKRw2yp8Kd",
        "folder": "Music/Correr 2025.2",  # Путь на SMB сервере
        "description": "Плейлист для бега",
        "playlist": "Correr 2025.2.m3u",  # Имя M3U плейлиста (опционально)
        "smb_config": {
            "server": "MYCLOUDEX2ULTRA",  # Имя SMB сервера
            "share": "leon",              # Имя SMB шары
            "username": os.getenv("SMB_USERNAME_MYCLOUDEX2ULTRA", "admin"),  # Логин из .env
            "password": os.getenv("SMB_PASSWORD_MYCLOUDEX2ULTRA", ""),       # Пароль из .env
            "domain": ""                  # Домен (обычно не требуется)
        }
    },
    {
        "url": "https://www.youtube.com/playlist?list=PLuYNdOlG3X4avQtZA1-XbEbR6SvS-9phw",
        "folder": "Music/Workout vol.1",  # Путь на SMB сервере
        "description": "Плейлист для тренеровок",
        "playlist": "Workout vol.1.m3u",  # Имя M3U плейлиста (опционально)
        "smb_config": {
            "server": "MYCLOUDEX2ULTRA",  # Имя SMB сервера
            "share": "leon",              # Имя SMB шары
            "username": os.getenv("SMB_USERNAME_MYCLOUDEX2ULTRA", "admin"),  # Логин из .env
            "password": os.getenv("SMB_PASSWORD_MYCLOUDEX2ULTRA", ""),       # Пароль из .env
            "domain": ""                  # Домен (обычно не требуется)
        }
    },
    # Добавьте дополнительные плейлисты здесь:
    # {
    #     "url": "https://www.youtube.com/playlist?list=PLAYLIST_ID_2",
    #     "folder": "Music/Workout",
    #     "description": "Плейлист для тренировок",
    #     "playlist": "Workout.m3u",  # Имя M3U плейлиста (опционально)
    #     "smb_config": {
    #         "server": "ANOTHER_SERVER",
    #         "share": "music_share",
    #         "username": os.getenv("SMB_USERNAME_ANOTHER", "user"),
    #         "password": os.getenv("SMB_PASSWORD_ANOTHER", ""),
    #         "domain": ""
    #     }
    # },
]

def _check_ffmpeg_available() -> bool:
    """Проверить доступность ffmpeg в системе"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

# Проверяем доступность ffmpeg
_check_ffmpeg_available()

# Определяем доступность ffmpeg
FFMPEG_AVAILABLE = _check_ffmpeg_available()

# Настройки yt-dlp с автоматической адаптацией
if FFMPEG_AVAILABLE:
    # С ffmpeg - можем конвертировать в MP3
    YT_DLP_OPTIONS = {
        'format': 'bestaudio/best',
        'outtmpl': '%(title)s',  # Без расширения, FFmpeg добавит .mp3
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'writeinfojson': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'ignoreerrors': True,
    }
    print("OK: FFmpeg detected - will convert to MP3")
else:
    # Без ffmpeg - скачиваем лучший доступный аудио формат
    YT_DLP_OPTIONS = {
        'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio',
        'outtmpl': '%(title)s.%(ext)s',
        'writeinfojson': False,
        'writesubtitles': False,
        'writeautomaticsub': False,
        'ignoreerrors': True,
    }
    print("WARNING: FFmpeg not found - will download best available audio format")

"""
Главный файл приложения для синхронизации MP3 из YouTube плейлиста на SMB диск
"""
import os
import sys
from config import (
    DOWNLOAD_ARCHIVE_FILE, TEMP_DOWNLOAD_DIR,
    YT_DLP_OPTIONS, PLAYLISTS_CONFIG
)
from logger import ConsoleLogger
from download_tracker import JsonDownloadTracker
from playlist_extractor import YouTubePlaylistExtractor
from audio_downloader import YouTubeAudioDownloader
from smb_uploader import SMBFileUploader
from youtube_mp3_sync import YouTubeMP3Synchronizer


def check_smb_configuration() -> bool:
    """Проверить настройки SMB для всех плейлистов"""
    try:
        for i, playlist_config in enumerate(PLAYLISTS_CONFIG, 1):
            smb_config = playlist_config.get("smb_config", {})
            server = smb_config.get("server", "")
            share = smb_config.get("share", "")
            username = smb_config.get("username", "")
            password = smb_config.get("password", "")
            
            if not server or not share or not username or not password:
                print(f"[ERROR] SMB configuration incomplete for playlist {i}!")
                print(f"Playlist: {playlist_config.get('description', 'Unknown')}")
                print("\nCheck config.py and ensure each playlist has complete smb_config:")
                print("- server: SMB server name or IP")
                print("- share: SMB share name")
                print("- username: SMB username")
                print("- password: SMB password")
                return False
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Configuration error: {e}")
        return False


def main() -> int:
    """Главная функция приложения"""
    try:
        print("YouTube MP3 Synchronizer")
        print("=" * 50)
        
        # Проверяем конфигурацию SMB
        if not check_smb_configuration():
            return 1
        
        # Инициализируем компоненты
        logger = ConsoleLogger()
        download_tracker = JsonDownloadTracker(DOWNLOAD_ARCHIVE_FILE, logger)
        playlist_extractor = YouTubePlaylistExtractor(logger)
        audio_downloader = YouTubeAudioDownloader(YT_DLP_OPTIONS, logger)
        file_uploader = SMBFileUploader(logger)
        
        # Создаем синхронизатор
        synchronizer = YouTubeMP3Synchronizer(
            playlist_extractor=playlist_extractor,
            download_tracker=download_tracker,
            audio_downloader=audio_downloader,
            file_uploader=file_uploader,
            logger=logger,
            temp_dir=TEMP_DOWNLOAD_DIR
        )
        
        # Запускаем синхронизацию
        logger.info("Запускаем синхронизацию...")
        synchronizer.sync()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n[INFO] Synchronization interrupted by user")
        return 0
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

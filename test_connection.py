"""
Тестовый скрипт для проверки подключения к YouTube и SMB серверу
"""
import sys
from config import (
    PLAYLISTS_CONFIG, SMB_SERVER, SMB_SHARE, SMB_USERNAME, SMB_PASSWORD, SMB_DOMAIN
)
from logger import ConsoleLogger
from playlist_extractor import YouTubePlaylistExtractor
from smb_uploader import SMBFileUploader


def test_youtube_connection():
    """Тестировать подключение к YouTube"""
    print("[TEST] Checking YouTube connection...")
    
    logger = ConsoleLogger("YouTubeTest")
    extractor = YouTubePlaylistExtractor(logger)
    
    try:
        # Тестируем первый плейлист из конфигурации
        if not PLAYLISTS_CONFIG:
            print("[ERROR] No playlists configured!")
            return False
            
        first_playlist = PLAYLISTS_CONFIG[0]
        playlist_url = first_playlist["url"]
        description = first_playlist.get("description", "")
        
        videos = extractor.get_video_list(playlist_url)
        
        if videos:
            print(f"[OK] Success! Found {len(videos)} videos in playlist: {description}")
            print("First 3 videos:")
            for i, video in enumerate(videos[:3], 1):
                title = video['title']
                try:
                    print(f"  {i}. {title}")
                except UnicodeEncodeError:
                    print(f"  {i}. [Video with special characters]")
            return True
        else:
            print("[ERROR] No videos found in playlist")
            return False
            
    except Exception as e:
        print(f"[ERROR] YouTube connection failed: {e}")
        return False


def test_smb_connection():
    """Тестировать подключение к SMB серверу"""
    print("[TEST] Checking SMB server connection...")
    
    logger = ConsoleLogger("SMBTest")
    uploader = SMBFileUploader(
        SMB_SERVER, SMB_SHARE, SMB_USERNAME, SMB_PASSWORD, logger, SMB_DOMAIN
    )
    
    try:
        if uploader.connect():
            print("[OK] Successfully connected to SMB server!")
            uploader.disconnect()
            return True
        else:
            print("[ERROR] Failed to connect to SMB server")
            return False
            
    except Exception as e:
        print(f"[ERROR] SMB connection failed: {e}")
        return False


def main():
    """Главная функция тестирования"""
    print("TESTING YouTube MP3 Synchronizer Components")
    print("=" * 60)
    print()
    
    # Проверяем конфигурацию
    if not PLAYLISTS_CONFIG:
        print("[ERROR] No playlists configured in config.py!")
        return 1
    
    print(f"Configured playlists: {len(PLAYLISTS_CONFIG)}")
    for i, playlist in enumerate(PLAYLISTS_CONFIG, 1):
        description = playlist.get('description', 'No description')
        folder = playlist['folder']
        try:
            print(f"  {i}. {description} -> {folder}")
        except UnicodeEncodeError:
            print(f"  {i}. [Playlist {i}] -> {folder}")
    print()
    
    # Тестируем YouTube
    youtube_ok = test_youtube_connection()
    print()
    
    # Тестируем SMB
    smb_ok = test_smb_connection()
    print()
    
    # Результаты
    print("TEST RESULTS:")
    print(f"YouTube connection: {'[OK]' if youtube_ok else '[FAILED]'}")
    print(f"SMB connection: {'[OK]' if smb_ok else '[FAILED]'}")
    print()
    
    if youtube_ok and smb_ok:
        print("All tests passed! You can run main.py")
        return 0
    else:
        print("Some tests failed. Please check your configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Test script for corrected yt-dlp configuration
"""

from playlist_extractor import YouTubePlaylistExtractor
from audio_downloader import YouTubeAudioDownloader
from logger import ConsoleLogger
from config import PLAYLISTS_CONFIG, YT_DLP_OPTIONS
import os

def main():
    print("Testing corrected yt-dlp configuration...")
    print("=" * 50)
    
    # Create components with proper dependencies
    logger = ConsoleLogger()
    playlist_extractor = YouTubePlaylistExtractor(logger)
    audio_downloader = YouTubeAudioDownloader(logger, YT_DLP_OPTIONS)
    
    playlist = PLAYLISTS_CONFIG[0]
    
    # Get video list
    videos = playlist_extractor.get_video_list(playlist['url'])
    print(f"Found {len(videos)} videos in playlist")
    
    if not videos:
        print("No videos found!")
        return
    
    # Test download of first video
    video = videos[0]
    print(f"Testing download: {video['title']}")
    
    file_path = audio_downloader.download_audio(video['url'], 'temp_downloads')
    
    if file_path and os.path.exists(file_path):
        print(f"SUCCESS: Downloaded to {file_path}")
        
        # Check file size
        file_size = os.path.getsize(file_path)
        print(f"File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
        
        # Check file header
        with open(file_path, 'rb') as f:
            header = f.read(16)
            print(f"File header (hex): {header.hex()}")
            
            if header.startswith(b'ID3'):
                print("SUCCESS: Found ID3 header - valid MP3!")
            elif header[0:2] == b'\xff\xfb' or header[0:2] == b'\xff\xfa':
                print("SUCCESS: Found MP3 frame header - valid MP3!")
            elif header.startswith(b'\x00\x00\x00\x18ftyp'):
                print("ERROR: Still DASH container format!")
            else:
                print("WARNING: Unknown file format")
                
    else:
        print("ERROR: Download failed!")

if __name__ == "__main__":
    main()

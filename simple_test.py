#!/usr/bin/env python3
"""
Simple test for yt-dlp with FFmpeg
"""

import yt_dlp
import os

def test_simple_download():
    print("Testing simple yt-dlp download with FFmpeg...")
    
    # Простые настройки для теста
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'temp_downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    
    # URL первого видео из плейлиста
    video_url = "https://www.youtube.com/watch?v=cJuO985zF8E"
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"Downloading: {video_url}")
            ydl.download([video_url])
            print("Download completed!")
            
        # Проверяем результат
        files = [f for f in os.listdir('temp_downloads') if f.endswith('.mp3')]
        if files:
            print(f"SUCCESS: Found MP3 files: {files}")
            
            # Проверяем первый файл
            file_path = os.path.join('temp_downloads', files[0])
            file_size = os.path.getsize(file_path)
            print(f"File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
            
            # Проверяем заголовок
            with open(file_path, 'rb') as f:
                header = f.read(16)
                print(f"File header (hex): {header.hex()}")
                
                if header.startswith(b'ID3'):
                    print("SUCCESS: Valid MP3 with ID3 header!")
                elif header[0:2] == b'\xff\xfb' or header[0:2] == b'\xff\xfa':
                    print("SUCCESS: Valid MP3 with frame header!")
                else:
                    print("WARNING: Unexpected file format")
        else:
            print("ERROR: No MP3 files found!")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_simple_download()

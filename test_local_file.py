#!/usr/bin/env python3
"""
Script for testing local MP3 file
"""

import os
import subprocess
import hashlib
from config import TEMP_DOWNLOAD_DIR

def test_mp3_file(file_path):
    """Tests MP3 file"""
    print(f"Testing file: {file_path}")
    
    if not os.path.exists(file_path):
        print("ERROR: File not found!")
        return False
    
    # Check file size
    file_size = os.path.getsize(file_path)
    print(f"File size: {file_size:,} bytes ({file_size / (1024*1024):.2f} MB)")
    
    # Calculate hash
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_md5.update(chunk)
    print(f"MD5 hash: {hash_md5.hexdigest()}")
    
    # Check file header (first bytes)
    with open(file_path, 'rb') as f:
        header = f.read(16)
        print(f"File header (hex): {header.hex()}")
        print(f"File header (ascii): {header}")
        
        # Check MP3 header
        if header.startswith(b'ID3'):
            print("OK: Found ID3 header")
        elif header[0:2] == b'\xff\xfb' or header[0:2] == b'\xff\xfa':
            print("OK: Found MP3 frame header")
        else:
            print("WARNING: No standard MP3 header found")
            print("This appears to be a DASH container format, not pure MP3")
    
    # Try to play with ffmpeg (if installed)
    try:
        result = subprocess.run([
            'ffmpeg', '-v', 'error', '-i', file_path, '-f', 'null', '-'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("OK: FFmpeg successfully processed file")
        else:
            print(f"ERROR: FFmpeg error: {result.stderr}")
    except FileNotFoundError:
        print("WARNING: FFmpeg not found, skipping check")
    except subprocess.TimeoutExpired:
        print("WARNING: FFmpeg check timed out")
    except Exception as e:
        print(f"WARNING: FFmpeg check error: {e}")
    
    return True

def main():
    print("MP3 File Tester")
    print("=" * 50)
    
    # Look for MP3 files in temp_downloads
    temp_dir = TEMP_DOWNLOAD_DIR
    if not os.path.exists(temp_dir):
        print(f"ERROR: Directory {temp_dir} not found!")
        return
    
    mp3_files = [f for f in os.listdir(temp_dir) if f.endswith('.mp3')]
    
    if not mp3_files:
        print(f"ERROR: No MP3 files found in {temp_dir}")
        return
    
    print(f"Found {len(mp3_files)} MP3 files:")
    for i, file in enumerate(mp3_files, 1):
        print(f"{i}. {file}")
    
    # Test each file
    for file in mp3_files:
        file_path = os.path.join(temp_dir, file)
        print("\n" + "="*60)
        test_mp3_file(file_path)

if __name__ == "__main__":
    main()

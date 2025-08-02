# YouTube MP3 SMB Synchronizer

🎵 **Automatic YouTube playlist to SMB network drive synchronizer with M3U playlist support**

A Python-based tool that automatically downloads MP3 files from YouTube playlists, uploads them to SMB network shares, and creates M3U playlists for easy music management.

## ✨ Features

- ✅ **YouTube MP3 Download**: Extract MP3 audio from YouTube playlists using yt-dlp + FFmpeg
- ✅ **SMB Network Upload**: Automatically upload files to SMB/CIFS network drives
- ✅ **M3U Playlist Generation**: Create M3U playlists on SMB server for easy music player integration
- ✅ **Multiple Playlists Support**: Configure multiple YouTube playlists with individual SMB destinations
- ✅ **Download Tracking**: Avoid re-downloading already processed videos
- ✅ **File Integrity Verification**: MD5 hash verification ensures complete file transfers
- ✅ **Chunked Upload**: Handle large files with SMB protocol limitations
- ✅ **Automatic Cleanup**: Remove temporary files after successful upload
- ✅ **Clean Architecture**: Built with OOP, SOLID, and DRY principles

## 🚀 Quick Start

### 1. Prerequisites

- **Python 3.11+** installed on your system
- **Windows OS** (tested on Windows 10/11)
- **SMB network access** to your target server/NAS
- **Internet connection** for YouTube access

### 2. Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Tur1du/youtube_mp3_smb.git
   cd youtube_mp3_smb
   ```

2. **Run the setup script:**
   ```bash
   setup.bat
   ```
   This will:
   - Create a Python virtual environment
   - Install all required dependencies
   - Check for FFmpeg and install if needed
   - Create necessary directories

### 3. Configuration

1. **Create environment file:**
   ```bash
   copy .env.example .env
   ```

2. **Edit `.env` file** with your SMB credentials:
   ```env
   SMB_USERNAME_MYCLOUDEX2ULTRA=your_username
   SMB_PASSWORD_MYCLOUDEX2ULTRA=your_password
   ```

3. **Edit `config.py`** to configure your playlists:
   ```python
   PLAYLISTS_CONFIG = [
       {
           "url": "https://www.youtube.com/playlist?list=YOUR_PLAYLIST_ID",
           "folder": "Music/YourFolder",
           "description": "Your playlist description",
           "playlist": "YourPlaylist.m3u",  # Optional M3U file
           "smb_config": {
               "server": "YOUR_SMB_SERVER",
               "share": "your_share",
               "username": os.getenv("SMB_USERNAME_YOUR_SERVER", "admin"),
               "password": os.getenv("SMB_PASSWORD_YOUR_SERVER", ""),
               "domain": ""
           }
       }
   ]
   ```

### 4. Run the Synchronizer

```bash
run.bat
```

The tool will:
- Extract videos from your YouTube playlists
- Download MP3 audio files
- Upload them to your SMB network drive
- Create M3U playlists
- Clean up temporary files

## 📁 Project Structure

```
youtube_mp3_smb/
├── main.py                 # Application entry point
├── config.py              # Configuration settings
├── youtube_mp3_sync.py    # Main synchronizer class
├── audio_downloader.py    # YouTube audio extraction
├── smb_uploader.py        # SMB file upload handler
├── m3u_manager.py         # M3U playlist generator
├── playlist_extractor.py  # YouTube playlist parser
├── download_tracker.py    # Download history tracking
├── interfaces.py          # Abstract interfaces
├── logger.py              # Logging utilities
├── requirements.txt       # Python dependencies
├── setup.bat             # Setup script
├── run.bat               # Run script
├── .env.example          # Environment template
└── README.md             # This file
```

## ⚙️ Configuration Details

### SMB Configuration

Each playlist can have its own SMB server configuration:

```python
"smb_config": {
    "server": "192.168.1.100",    # SMB server IP or hostname
    "share": "music",             # SMB share name
    "username": os.getenv("SMB_USERNAME_SERVER", "user"),
    "password": os.getenv("SMB_PASSWORD_SERVER", ""),
    "domain": ""                  # Windows domain (usually empty)
}
```

### Environment Variables

Add SMB credentials to `.env` file:

```env
# Format: SMB_USERNAME_<SERVER_NAME>=username
SMB_USERNAME_MYCLOUDEX2ULTRA=admin
SMB_PASSWORD_MYCLOUDEX2ULTRA=your_secure_password

# Add more servers as needed
SMB_USERNAME_ANOTHER_SERVER=user
SMB_PASSWORD_ANOTHER_SERVER=another_password
```

### YouTube Playlist URLs

Get playlist URLs from YouTube:
1. Go to your YouTube playlist
2. Copy the URL (format: `https://www.youtube.com/playlist?list=PLAYLIST_ID`)
3. Add to `config.py`

## 🔧 Troubleshooting

### FFmpeg Not Found
The setup script will automatically download and install FFmpeg. If you encounter issues:
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to a folder
3. Add the folder to your system PATH

### SMB Connection Issues
- Verify SMB server is accessible: `\\server_ip\share_name`
- Check username/password in `.env` file
- Ensure SMB/CIFS is enabled on target server
- Try connecting manually through Windows Explorer first

### YouTube Download Errors
- Check internet connection
- Verify playlist is public or accessible
- Some videos may be region-restricted or unavailable

### Permission Errors
- Run as Administrator if needed
- Check SMB share permissions
- Verify write access to target folders

## 📝 Logs

The application creates detailed logs showing:
- YouTube playlist extraction
- MP3 download progress
- SMB upload status
- M3U playlist creation
- Error messages and troubleshooting info

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source. Feel free to use and modify as needed.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all prerequisites are met
4. Verify your configuration files

@echo off
chcp 65001 >nul
echo 🚀 YouTube MP3 SMB Synchronizer Setup
echo ====================================
echo.

echo 📋 Checking prerequisites...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.11+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Check if FFmpeg is installed
echo.
echo 🔍 Checking for FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  FFmpeg not found in PATH
    echo 📥 Downloading and installing FFmpeg...
    
    REM Create ffmpeg directory
    if not exist "ffmpeg" mkdir ffmpeg
    
    REM Download FFmpeg (using a reliable source)
    echo Downloading FFmpeg... This may take a few minutes.
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip' -OutFile 'ffmpeg.zip'}"
    
    if exist "ffmpeg.zip" (
        echo 📦 Extracting FFmpeg...
        powershell -Command "Expand-Archive -Path 'ffmpeg.zip' -DestinationPath 'ffmpeg_temp' -Force"
        
        REM Move ffmpeg.exe to ffmpeg directory
        for /d %%i in (ffmpeg_temp\ffmpeg-*) do (
            copy "%%i\bin\ffmpeg.exe" "ffmpeg\" >nul
            copy "%%i\bin\ffprobe.exe" "ffmpeg\" >nul
        )
        
        REM Cleanup
        rmdir /s /q ffmpeg_temp >nul 2>&1
        del ffmpeg.zip >nul 2>&1
        
        REM Add to PATH for current session
        set PATH=%PATH%;%CD%\ffmpeg
        
        echo ✅ FFmpeg installed successfully
        echo 📝 Note: FFmpeg is installed locally in the project folder
        echo    For system-wide installation, add %CD%\ffmpeg to your system PATH
    ) else (
        echo ❌ Failed to download FFmpeg
        echo Please download manually from https://ffmpeg.org/download.html
        echo and add to your system PATH
    )
) else (
    echo ✅ FFmpeg found
    ffmpeg -version 2>&1 | findstr "ffmpeg version"
)

echo.
echo 🐍 Setting up Python virtual environment...

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)

echo.
echo 📦 Installing Python dependencies...

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo Installing required packages...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

echo.
echo 📁 Creating necessary directories...

REM Create temp directory
if not exist "temp_downloads" mkdir temp_downloads
echo ✅ temp_downloads directory ready

echo.
echo 📄 Setting up configuration files...

REM Create .env file if it doesn't exist
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo ✅ .env file created from template
        echo ⚠️  Please edit .env file with your SMB credentials
    ) else (
        echo # SMB Configuration > .env
        echo # Add your SMB server credentials here >> .env
        echo SMB_USERNAME_MYCLOUDEX2ULTRA=admin >> .env
        echo SMB_PASSWORD_MYCLOUDEX2ULTRA=your_password_here >> .env
        echo ✅ .env file created
        echo ⚠️  Please edit .env file with your SMB credentials
    )
) else (
    echo ✅ .env file already exists
)

REM Create downloaded.json if it doesn't exist
if not exist "downloaded.json" (
    echo {"downloaded": {}} > downloaded.json
    echo ✅ downloaded.json tracking file created
) else (
    echo ✅ downloaded.json tracking file exists
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo 📋 Next steps:
echo 1. Edit .env file with your SMB server credentials
echo 2. Edit config.py to configure your YouTube playlists
echo 3. Run the application with: run.bat
echo.
echo 📚 For detailed instructions, see README.md
echo.

deactivate
pause

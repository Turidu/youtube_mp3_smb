@echo off
echo 🎵 Запуск YouTube MP3 Синхронизатора
echo ==================================

echo.
echo Активируем виртуальное окружение...
call venv\Scripts\activate.bat

echo.
echo Запускаем приложение...
python main.py

echo.
pause

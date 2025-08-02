@echo off
echo 🔧 Настройка YouTube MP3 Синхронизатора
echo =====================================

echo.
echo Активируем виртуальное окружение...
call venv\Scripts\activate.bat

echo.
echo Устанавливаем зависимости...
pip install -r requirements.txt

echo.
echo ✅ Настройка завершена!
echo.
echo Для запуска приложения используйте:
echo   run.bat
echo.
echo Для тестирования подключений:
echo   test.bat
echo.
pause

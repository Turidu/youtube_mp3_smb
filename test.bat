@echo off
echo 🧪 Тестирование подключений
echo ===========================

echo.
echo Активируем виртуальное окружение...
call venv\Scripts\activate.bat

echo.
echo Запускаем тесты...
python test_connection.py

echo.
pause

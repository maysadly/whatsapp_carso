#!/bin/bash

# Запуск скрипта для настройки ngrok туннеля к Flask-приложению

# Проверка, запущен ли уже Flask
if pgrep -f "python app.py" > /dev/null; then
    echo "Flask-приложение уже запущено"
else
    echo "Запуск Flask-приложения..."
    # Запуск Flask в фоновом режиме
    python app.py &
    # Даем время Flask для запуска
    sleep 2
    echo "Flask-приложение запущено на порту 5000"
fi

# Запуск ngrok для создания туннеля к порту 5000
echo "Запуск ngrok туннеля..."
ngrok http 5050

# Примечание: Этот скрипт не останавливает Flask при выходе из ngrok
# Для остановки Flask используйте: pkill -f "python app.py"
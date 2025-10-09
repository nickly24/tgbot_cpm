#!/bin/bash

# Скрипт для запуска Flask API сервера
echo "🚀 Запуск Flask API Server..."

# Получаем директорию скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Останавливаем все существующие процессы Flask
echo "🛑 Остановка существующих процессов API..."
pkill -f "python3 app.py" 2>/dev/null
sleep 2

# Проверяем, что процессы остановлены
REMAINING=$(ps aux | grep "python3 app.py" | grep -v grep | wc -l)
if [ $REMAINING -gt 0 ]; then
    echo "⚠️ Принудительная остановка процессов..."
    pkill -9 -f "python3 app.py" 2>/dev/null
    sleep 1
fi

# Активируем виртуальное окружение и запускаем API
echo "📡 Запуск API сервера..."
cd "$SCRIPT_DIR"
source venv/bin/activate
python3 app.py


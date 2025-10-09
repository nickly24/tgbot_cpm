#!/bin/bash

# Скрипт для безопасного запуска бота
echo "🤖 Запуск Telegram Bot..."

# Получаем директорию скрипта
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Останавливаем все существующие процессы
echo "🛑 Остановка существующих процессов..."
pkill -f "python3 bot.py" 2>/dev/null
sleep 2

# Проверяем, что процессы остановлены
REMAINING=$(ps aux | grep "python3 bot.py" | grep -v grep | wc -l)
if [ $REMAINING -gt 0 ]; then
    echo "⚠️ Принудительная остановка процессов..."
    pkill -9 -f "python3 bot.py" 2>/dev/null
    sleep 1
fi

# Активируем виртуальное окружение и запускаем бота
echo "🚀 Запуск нового экземпляра бота..."
cd "$SCRIPT_DIR"
source venv/bin/activate
python3 bot.py

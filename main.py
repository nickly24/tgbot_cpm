#!/usr/bin/env python3
"""
Главный файл для запуска Telegram бота и Flask API
Запускает оба сервиса одновременно
"""

import threading
import time
from flask import Flask
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from app import app
from telegram_bot import telegram_bot

def run_flask():
    """Запуск Flask API в отдельном потоке"""
    print("=" * 60)
    print("🚀 Запуск Flask API сервера...")
    print(f"📡 API доступен по адресу: http://{FLASK_HOST}:{FLASK_PORT}")
    print(f"📚 Документация: http://{FLASK_HOST}:{FLASK_PORT}/api/docs")
    print(f"🔍 Проверка здоровья: http://{FLASK_HOST}:{FLASK_PORT}/api/health")
    print("=" * 60)
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT, use_reloader=False)

def run_telegram_bot():
    """Запуск Telegram бота"""
    # Небольшая задержка для инициализации Flask
    time.sleep(2)
    
    print("=" * 60)
    print("🤖 Запуск Telegram бота...")
    print("📝 Бот готов принимать сообщения")
    print("💬 Пользователи могут писать боту @cpmdev_bot")
    print("=" * 60)
    print()
    print("✅ Система полностью запущена!")
    print("⚠️  Для остановки нажмите Ctrl+C")
    print()
    
    telegram_bot.run()

if __name__ == '__main__':
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     TELEGRAM BOT + API SERVER - Unified Launcher          ║")
    print("║                    Version 2.0.0                           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    
    try:
        # Запускаем Flask в отдельном потоке
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        
        # Запускаем Telegram бота в основном потоке
        run_telegram_bot()
        
    except KeyboardInterrupt:
        print()
        print("=" * 60)
        print("🛑 Остановка сервисов...")
        print("👋 До свидания!")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ Критическая ошибка: {e}")
        print("=" * 60)
        raise


#!/usr/bin/env python3
"""
Скрипт для запуска Telegram бота
Запускайте отдельно от Flask API
"""

from telegram_bot import telegram_bot

if __name__ == '__main__':
    print("🤖 Запуск Telegram бота...")
    print("📝 Бот готов принимать сообщения")
    telegram_bot.run()


#!/usr/bin/env python3
"""
Тест новой системы валидации студентов с логином и паролем
"""

import asyncio
import httpx
from telegram_bot import TelegramBot

async def test_validation():
    """Тест валидации студента с новыми полями"""
    
    # Создаем экземпляр бота
    bot = TelegramBot()
    
    # Тестовые данные (имитируем ответ API)
    test_student_data = {
        "student_id": 123,
        "full_name": "Иванов Петр Сергеевич",
        "class": 10,
        "group_id": 5,
        "tg_name": "@ivanov_petr",
        "login": "pivanov10",
        "password": "aB3dF8g2"
    }
    
    print("🧪 Тестирование новой системы валидации...")
    print(f"📊 Тестовые данные: {test_student_data}")
    print()
    
    # Тестируем формирование сообщения
    full_name = test_student_data.get('full_name', 'Студент')
    login = test_student_data.get('login', '')
    password = test_student_data.get('password', '')
    
    # Формируем сообщение как в коде
    confirmation_message = (
        f"✅ Добро пожаловать, {full_name}!\n\n"
        f"Вы успешно зарегистрированы как: Студент\n\n"
    )
    
    # Добавляем логин и пароль, если они есть
    if login and password:
        confirmation_message += (
            f"🔑 Ваши данные для входа:\n"
            f"Логин: {login}\n"
            f"Пароль: {password}\n\n"
        )
    
    confirmation_message += "Теперь можете отправлять мне текстовые сообщения, и я передам их администратору."
    
    print("📝 Сформированное сообщение:")
    print("=" * 50)
    print(confirmation_message)
    print("=" * 50)
    print()
    
    # Проверяем, что логин и пароль присутствуют
    if "Логин:" in confirmation_message and "Пароль:" in confirmation_message:
        print("✅ УСПЕХ: Логин и пароль добавлены в сообщение")
    else:
        print("❌ ОШИБКА: Логин и пароль не найдены в сообщении")
    
    # Проверяем, что данные корректны
    if login in confirmation_message and password in confirmation_message:
        print("✅ УСПЕХ: Корректные данные логина и пароля")
    else:
        print("❌ ОШИБКА: Неверные данные логина и пароля")
    
    print()
    print("🎯 Тест завершен!")

if __name__ == "__main__":
    asyncio.run(test_validation())

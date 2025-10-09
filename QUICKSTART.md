# 🚀 Быстрый старт

## Пошаговая инструкция запуска проекта

### 1️⃣ Создание .env файла

Создайте файл `.env` в корне проекта:

```bash
nano .env
```

Вставьте следующее содержимое:

```env
# MongoDB Configuration
MONGO_HOST=109.73.202.73
MONGO_PORT=27017
MONGO_USERNAME=gen_user
MONGO_PASSWORD=77tanufe
MONGO_AUTH_DB=admin
MONGO_DATABASE=chatbot

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8327908006:AAG-aR5WnP34rwIwwk5cHNOgZJK9GDW4DCA

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=80
FLASK_DEBUG=True
```

Сохраните (Ctrl+O, Enter, Ctrl+X).

### 2️⃣ Активация виртуального окружения

```bash
source venv/bin/activate
```

### 3️⃣ Запуск (два варианта)

#### Вариант А: Использование скриптов (рекомендуется)

**Терминал 1 - API:**

```bash
chmod +x start_api.sh
./start_api.sh
```

**Терминал 2 - Бот:**

```bash
chmod +x start_bot.sh
./start_bot.sh
```

#### Вариант Б: Ручной запуск

**Терминал 1 - API:**

```bash
source venv/bin/activate
python3 app.py
```

**Терминал 2 - Бот:**

```bash
source venv/bin/activate
python3 bot.py
```

### 4️⃣ Проверка работы

Откройте в браузере: http://0.0.0.0:80

Или через curl:

```bash
curl http://0.0.0.0:80/api/health
```

### 5️⃣ Тестирование бота

1. Найдите бота в Telegram: `@cpmdev_bot`
2. Отправьте команду `/start`
3. Выберите статус (студент, абитуриент и т.д.)
4. Отправьте тестовое сообщение

### 6️⃣ Проверка API

Получить список чатов:

```bash
curl http://0.0.0.0:80/api/chats
```

Отправить сообщение (замените CHAT_ID):

```bash
curl -X POST http://0.0.0.0:80/api/chats/CHAT_ID/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Тестовое сообщение от админа"}'
```

Пометить как прочитанное:

```bash
curl -X POST http://0.0.0.0:80/api/chats/CHAT_ID/mark-read
```

---

## ⚠️ Решение частых проблем

### Порт 80 занят или требует root

Измените порт в `.env`:

```env
FLASK_PORT=8000
```

Затем используйте: `http://0.0.0.0:8000`

### MongoDB недоступна

Проверьте подключение:

```bash
python3 -c "from database import db; print('OK')"
```

### Бот не отвечает

1. Проверьте, что `bot.py` запущен
2. Убедитесь, что токен правильный
3. Проверьте логи в консоли

---

## 📚 Дальнейшие шаги

1. Прочитайте [README.md](README.md) для полной документации
2. Изучите [API_DOCUMENTATION.md](API_DOCUMENTATION.md) для API
3. Смотрите [REACT_EXAMPLES.md](REACT_EXAMPLES.md) для frontend примеров

---

**Успешного запуска! 🎉**

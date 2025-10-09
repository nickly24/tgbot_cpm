# Telegram Bot API Server

Веб-сервер на Flask и Telegram бот для управления клиентскими чатами через веб-интерфейс админки.

## 🚀 Основной функционал

- **Telegram бот** - принимает текстовые сообщения от клиентов с выбором статуса
- **REST API сервер** - предоставляет API для веб-админки
- **MongoDB** - надежное хранение всех данных
- **Статусы клиентов** - студент, абитуриент, родитель студента, родитель абитуриента
- **Статусы прочитанности** - отслеживание непрочитанных сообщений
- **Веб-интерфейс** - админка для переписки с клиентами

## 📋 Новые возможности v2.0

✅ **Новая структура БД** - оптимизированная схема (коллекции: users, messages)  
✅ **Статусы клиентов** - 4 типа: студент, абитуриент, родители  
✅ **Inline клавиатура** - клиент выбирает статус при первом контакте  
✅ **Статус прочитанности** - отслеживание непрочитанных сообщений  
✅ **Раздельный запуск** - Flask API и Telegram бот запускаются отдельно  
✅ **Безопасность** - секреты в .env файле

## 🛠 Установка

### 1. Клонирование и установка зависимостей

```bash
cd cpm-bot
python3 -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# MongoDB Configuration
MONGO_HOST=109.73.202.73
MONGO_PORT=27017
MONGO_USERNAME=gen_user
MONGO_PASSWORD=your_password
MONGO_AUTH_DB=admin
MONGO_DATABASE=chatbot

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token

# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=80
FLASK_DEBUG=True
```

**⚠️ ВАЖНО:** Никогда не коммитьте `.env` файл в git!

## 🚀 Запуск

Теперь Flask API и Telegram бот запускаются **отдельно**:

### Вариант 1: Использование скриптов (рекомендуется)

**Запуск API сервера:**

```bash
chmod +x start_api.sh
./start_api.sh
```

**Запуск Telegram бота (в другом терминале):**

```bash
chmod +x start_bot.sh
./start_bot.sh
```

### Вариант 2: Ручной запуск

**Терминал 1 - API сервер:**

```bash
source venv/bin/activate
python3 app.py
```

**Терминал 2 - Telegram бот:**

```bash
source venv/bin/activate
python3 bot.py
```

После запуска:

- 📡 API доступен: `http://0.0.0.0:80`
- 🤖 Бот готов принимать сообщения
- 📚 Документация: `http://0.0.0.0:80/api/docs`

**Для остановки:** Нажмите `Ctrl+C` в каждом терминале

## 📊 Структура базы данных

### Коллекция `users`

```json
{
  "chat_id": 123456789,
  "user_id": 123456789,
  "username": "username",
  "first_name": "Имя",
  "last_name": "Фамилия",
  "name": "Полное Имя",
  "status": "student",
  "created_at": "2025-10-09T12:00:00",
  "updated_at": "2025-10-09T12:00:00"
}
```

### Коллекция `messages`

```json
{
  "_id": "ObjectId",
  "chat_id": 123456789,
  "text": "Текст сообщения",
  "timestamp": "2025-10-09T12:00:00",
  "from_user": true,
  "is_read": false,
  "message_id": 123,
  "admin_name": "Администратор"
}
```

## 📡 API Endpoints

### Чаты

- `GET /api/chats` - Список всех чатов
- `GET /api/chats/<chat_id>` - История чата
- `POST /api/chats/<chat_id>/send` - Отправить сообщение
- `POST /api/chats/<chat_id>/mark-read` - Пометить как прочитанное

### Пользователи

- `GET /api/chats/<chat_id>/user` - Информация о пользователе
- `PUT /api/chats/<chat_id>/name` - Обновить имя

### Статусы

- `GET /api/chats/<chat_id>/status` - Получить статус
- `PUT /api/chats/<chat_id>/status` - Обновить статус
- `GET /api/statuses` - Список всех статусов

### Статистика

- `GET /api/stats` - Общая статистика
- `GET /api/health` - Проверка состояния

## 🎯 Статусы клиентов

| Значение           | Название             |
| ------------------ | -------------------- |
| `student`          | Студент              |
| `applicant`        | Абитуриент           |
| `parent_student`   | Родитель студента    |
| `parent_applicant` | Родитель абитуриента |

## 💬 Работа с ботом

### Первый контакт

1. Пользователь отправляет `/start`
2. Бот предлагает выбрать статус через inline кнопки
3. После выбора пользователь может отправлять сообщения

### Ограничения

- ✅ Принимаются только **текстовые сообщения**
- ❌ Фото, видео, голосовые, файлы - отклоняются
- 📩 Все сообщения сохраняются в БД

## 📚 Документация для разработчиков

### Основные файлы

- **[API_DOCUMENTATION.md](API_DOCUMENTATION.md)** - Полная документация API
- **[REACT_EXAMPLES.md](REACT_EXAMPLES.md)** - Примеры для React
- **[api_examples.json](api_examples.json)** - Примеры JSON ответов

### Структура проекта

```
cpm-bot/
├── app.py                  # Flask API сервер
├── bot.py                  # Точка входа Telegram бота
├── telegram_bot.py         # Логика Telegram бота
├── api.py                  # API endpoints
├── database.py             # Работа с MongoDB
├── config.py               # Конфигурация
├── .env                    # Переменные окружения (создать!)
├── .gitignore              # Игнорируемые файлы
├── requirements.txt        # Зависимости Python
├── start_api.sh            # Скрипт запуска API
├── start_bot.sh            # Скрипт запуска бота
└── docs/                   # Документация
```

## 🔧 Примеры использования API

### Получение списка чатов

```bash
curl http://0.0.0.0:80/api/chats
```

### Отправка сообщения

```bash
curl -X POST http://0.0.0.0:80/api/chats/123456789/send \
  -H "Content-Type: application/json" \
  -d '{"message": "Привет!", "admin_name": "Менеджер"}'
```

### Пометить сообщения как прочитанные

```bash
curl -X POST http://0.0.0.0:80/api/chats/123456789/mark-read
```

### Обновить статус клиента

```bash
curl -X PUT http://0.0.0.0:80/api/chats/123456789/status \
  -H "Content-Type: application/json" \
  -d '{"status": "student"}'
```

### Получить статистику

```bash
curl http://0.0.0.0:80/api/stats
```

## 🐛 Отладка

### Проверка подключения к MongoDB

```python
python3 -c "from database import db; print('✅ БД подключена' if db.client else '❌ Ошибка')"
```

### Проверка API

```bash
curl http://0.0.0.0:80/api/health
```

### Логи

- Flask выводит логи в консоль
- Telegram бот логирует через `logging` модуль

## ⚠️ Важные замечания

1. **Порт 80** требует root прав на Linux/Mac. Для разработки используйте порт 8000+
2. **MongoDB** должна быть доступна и настроена
3. **Telegram Bot Token** должен быть валидным
4. Запускайте **оба процесса** (API + Bot) для полной работы системы
5. `.env` файл не должен попадать в git

## 🔐 Безопасность

- ✅ Все секреты в `.env` файле
- ✅ `.gitignore` настроен правильно
- ✅ Валидация входных данных в API
- ✅ Проверка статусов перед обновлением
- ⚠️ Для production добавьте аутентификацию в API

## 📝 Лицензия

Проект для внутреннего использования.

## 🤝 Поддержка

При возникновении проблем:

1. Проверьте `.env` файл
2. Убедитесь, что MongoDB доступна
3. Проверьте логи в консоли
4. Используйте `/api/health` для диагностики

---

**Версия:** 2.0.0  
**Последнее обновление:** 09.10.2025

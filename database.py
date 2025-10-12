from pymongo import MongoClient, DESCENDING
from datetime import datetime
from config import MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_AUTH_DB, MONGO_DATABASE

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.users = None
        self.messages = None
        self.config = None
        self.connect()
    
    def connect(self):
        """Подключение к MongoDB"""
        try:
            connection_string = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/?authSource={MONGO_AUTH_DB}&directConnection=true"
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            self.db = self.client[MONGO_DATABASE]
            
            # Основные коллекции
            self.users = self.db['users']
            self.messages = self.db['messages']
            self.config = self.db['config']
            
            # Создаем индексы для оптимизации
            self.users.create_index("chat_id", unique=True)
            self.messages.create_index([("chat_id", 1), ("timestamp", DESCENDING)])
            self.messages.create_index("is_read")
            self.config.create_index("type", unique=True)
            
            print("✅ Успешное подключение к MongoDB")
        except Exception as e:
            print(f"❌ Ошибка подключения к MongoDB: {e}")
            raise
    
    # ==================== ПОЛЬЗОВАТЕЛИ ====================
    
    def save_user(self, chat_id, user_info, status=None):
        """Сохранить или обновить информацию о пользователе"""
        user_data = {
            "chat_id": chat_id,
            "user_id": user_info.get("user_id"),
            "username": user_info.get("username"),
            "first_name": user_info.get("first_name"),
            "last_name": user_info.get("last_name"),
            # name НЕ заполняется автоматически - пользователь вводит сам
            "status": status,  # студент, абитуриент, родитель студента, родитель абитуриента
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.users.update_one(
            {"chat_id": chat_id},
            {"$set": user_data},
            upsert=True
        )
        return True
    
    def get_user(self, chat_id):
        """Получить информацию о пользователе"""
        return self.users.find_one({"chat_id": chat_id})
    
    def update_user_status(self, chat_id, status):
        """Обновить статус пользователя"""
        result = self.users.update_one(
            {"chat_id": chat_id},
            {
                "$set": {
                    "status": status,
                    "updated_at": datetime.now().isoformat()
                }
            },
            upsert=True
        )
        
        return result.matched_count > 0 or result.upserted_id is not None
    
    def update_user_name(self, chat_id, new_name):
        """Обновить имя пользователя"""
        result = self.users.update_one(
            {"chat_id": chat_id},
            {
                "$set": {
                    "name": new_name,
                    "updated_at": datetime.now().isoformat()
                }
            }
        )
        return result.modified_count > 0
    
    def get_all_users(self):
        """Получить список всех пользователей"""
        return list(self.users.find().sort("updated_at", DESCENDING))
    
    # ==================== СООБЩЕНИЯ ====================
    
    def save_message(self, chat_id, message_data):
        """Сохранить сообщение"""
        message_doc = {
            "chat_id": chat_id,
            "text": message_data.get("text"),
            "timestamp": message_data.get("timestamp", datetime.now().isoformat()),
            "from_user": message_data.get("from_user", True),  # True - от клиента, False - от админа
            "is_read": message_data.get("is_read", False),  # Статус прочитанности (только для сообщений от клиента)
            "message_id": message_data.get("message_id"),  # ID сообщения в Telegram (если от клиента)
            "admin_name": message_data.get("admin_name"),  # Имя админа (если от админа)
        }
        
        result = self.messages.insert_one(message_doc)
        return result.inserted_id
    
    def get_chat_messages(self, chat_id, limit=None):
        """Получить сообщения чата"""
        query = {"chat_id": chat_id}
        cursor = self.messages.find(query).sort("timestamp", 1)
        
        if limit:
            cursor = cursor.limit(limit)
        
        return list(cursor)
    
    def mark_messages_as_read(self, chat_id):
        """Пометить все непрочитанные сообщения клиента как прочитанные"""
        result = self.messages.update_many(
            {
                "chat_id": chat_id,
                "from_user": True,
                "is_read": False
            },
            {
                "$set": {
                    "is_read": True,
                    "read_at": datetime.now().isoformat()
                }
            }
        )
        return result.modified_count
    
    def get_unread_count(self, chat_id):
        """Получить количество непрочитанных сообщений от клиента"""
        return self.messages.count_documents({
            "chat_id": chat_id,
            "from_user": True,
            "is_read": False
        })
    
    def get_last_message(self, chat_id):
        """Получить последнее сообщение в чате"""
        return self.messages.find_one(
            {"chat_id": chat_id},
            sort=[("timestamp", DESCENDING)]
        )
    
    # ==================== ЧАТЫ ====================
    
    def get_all_chats(self):
        """Получить список всех чатов с последними сообщениями и непрочитанными"""
        users = self.get_all_users()
        chats = []
        
        for user in users:
            chat_id = user['chat_id']
            last_message = self.get_last_message(chat_id)
            unread_count = self.get_unread_count(chat_id)
            
            chats.append({
                "chat_id": chat_id,
                "user_info": {
                    "user_id": user.get("user_id"),
                    "username": user.get("username"),
                    "name": user.get("name"),
                    "created_at": user.get("created_at")
                },
                "status": user.get("status"),
                "last_message": {
                    "text": last_message.get("text"),
                    "timestamp": last_message.get("timestamp"),
                    "from_user": last_message.get("from_user")
                } if last_message else None,
                "unread_count": unread_count,
                "updated_at": user.get("updated_at")
            })
        
        return chats
    
    def delete_chat(self, chat_id):
        """Удалить чат со всеми сообщениями"""
        try:
            # Удаляем пользователя
            user_result = self.users.delete_one({"chat_id": chat_id})
            
            # Удаляем все сообщения
            messages_result = self.messages.delete_many({"chat_id": chat_id})
            
            return {
                "user_deleted": user_result.deleted_count > 0,
                "messages_deleted": messages_result.deleted_count
            }
        except Exception as e:
            print(f"Ошибка удаления чата {chat_id}: {e}")
            return None
    
    # ==================== КОНФИГУРАЦИЯ ====================
    
    def get_bot_messages(self):
        """Получить все сообщения бота"""
        config_doc = self.config.find_one({"type": "bot_messages"})
        if config_doc:
            return config_doc.get("messages", {})
        return None
    
    def update_bot_messages(self, messages):
        """Обновить сообщения бота"""
        result = self.config.update_one(
            {"type": "bot_messages"},
            {
                "$set": {
                    "messages": messages,
                    "updated_at": datetime.now().isoformat()
                }
            },
            upsert=True
        )
        return result.matched_count > 0 or result.upserted_id is not None
    
    def get_bot_message(self, message_key):
        """Получить конкретное сообщение бота по ключу"""
        messages = self.get_bot_messages()
        if messages:
            return messages.get(message_key)
        return None
    
    def update_bot_message(self, message_key, message_text):
        """Обновить конкретное сообщение бота"""
        result = self.config.update_one(
            {"type": "bot_messages"},
            {
                "$set": {
                    f"messages.{message_key}": message_text,
                    "updated_at": datetime.now().isoformat()
                }
            }
        )
        return result.modified_count > 0
    
    def get_client_statuses(self):
        """Получить все статусы клиентов"""
        config_doc = self.config.find_one({"type": "client_statuses"})
        if config_doc:
            return config_doc.get("statuses", [])
        return None
    
    def update_client_statuses(self, statuses):
        """Обновить все статусы клиентов"""
        result = self.config.update_one(
            {"type": "client_statuses"},
            {
                "$set": {
                    "statuses": statuses,
                    "updated_at": datetime.now().isoformat()
                }
            },
            upsert=True
        )
        return result.matched_count > 0 or result.upserted_id is not None
    
    def add_client_status(self, status_data):
        """Добавить новый статус клиента"""
        statuses = self.get_client_statuses()
        if statuses is None:
            statuses = []
        
        # Проверяем, не существует ли уже такой статус
        if any(s.get("value") == status_data.get("value") for s in statuses):
            return False
        
        statuses.append(status_data)
        return self.update_client_statuses(statuses)
    
    def update_client_status(self, status_value, status_data):
        """Обновить существующий статус"""
        statuses = self.get_client_statuses()
        if statuses is None:
            return False
        
        for i, status in enumerate(statuses):
            if status.get("value") == status_value:
                # Проверяем, не системный ли это статус
                if status.get("is_system", False):
                    # Для системных статусов можно обновить только label и emoji
                    statuses[i]["label"] = status_data.get("label", status["label"])
                    statuses[i]["emoji"] = status_data.get("emoji", status.get("emoji", ""))
                else:
                    # Для не системных можно обновить всё кроме is_system
                    statuses[i].update(status_data)
                    statuses[i]["is_system"] = False  # Убеждаемся что не изменился
                
                statuses[i]["updated_at"] = datetime.now().isoformat()
                return self.update_client_statuses(statuses)
        
        return False
    
    def delete_client_status(self, status_value):
        """Удалить статус клиента (только не системные)"""
        statuses = self.get_client_statuses()
        if statuses is None:
            return False
        
        for status in statuses:
            if status.get("value") == status_value:
                if status.get("is_system", False):
                    return False  # Нельзя удалять системные статусы
        
        # Удаляем статус
        statuses = [s for s in statuses if s.get("value") != status_value]
        return self.update_client_statuses(statuses)
    
    def init_default_config(self):
        """Инициализация конфигурации по умолчанию"""
        # Проверяем, есть ли уже конфигурация
        bot_messages = self.get_bot_messages()
        if bot_messages is None:
            # Создаем дефолтные сообщения
            default_messages = {
                "welcome": "Привет! 👋\n\nЯ бот для связи с администратором.\n\nКак мне вас называть? Напишите ваше имя:",
                "ask_status": "Приятно познакомиться, {name}! 😊\n\nТеперь выберите, кто вы:",
                "status_selected": "✅ Отлично! Вы выбрали статус: {status_name}\n\nТеперь можете отправлять мне текстовые сообщения, и я передам их администратору.",
                "welcome_back": "С возвращением, {name}! 👋\n\nВаш статус: {status_name}\n\nОтправляйте мне текстовые сообщения, и я передам их администратору.",
                "message_received": "✅ Ваше сообщение получено и передано администратору. Ожидайте ответа!",
                "unsupported_message": "❌ Извините, я обрабатываю только текстовые сообщения. Пожалуйста, отправьте текст.",
                "need_status": "⚠️ Пожалуйста, сначала выберите ваш статус с помощью кнопок выше.",
                "admin_message_prefix": "📩 Сообщение от {admin_name}:\n\n"
            }
            self.update_bot_messages(default_messages)
            print("✅ Инициализированы дефолтные сообщения бота")
        
        client_statuses = self.get_client_statuses()
        if client_statuses is None:
            # Создаем дефолтные статусы
            default_statuses = [
                {
                    "value": "student",
                    "label": "Студент",
                    "emoji": "👨‍🎓",
                    "is_system": True,
                    "order": 0,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "value": "reserve",
                    "label": "Резерв",
                    "emoji": "📝",
                    "is_system": True,
                    "order": 1,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "value": "applicant",
                    "label": "Абитуриент",
                    "emoji": "🎓",
                    "is_system": False,
                    "order": 2,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "value": "parent_student",
                    "label": "Родитель студента",
                    "emoji": "👨‍👦",
                    "is_system": False,
                    "order": 3,
                    "created_at": datetime.now().isoformat()
                },
                {
                    "value": "parent_applicant",
                    "label": "Родитель абитуриента",
                    "emoji": "👨‍👧",
                    "is_system": False,
                    "order": 4,
                    "created_at": datetime.now().isoformat()
                }
            ]
            self.update_client_statuses(default_statuses)
            print("✅ Инициализированы дефолтные статусы клиентов")

# Глобальный экземпляр базы данных
db = Database()

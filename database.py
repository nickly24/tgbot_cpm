from pymongo import MongoClient, DESCENDING
from datetime import datetime
from config import MONGO_HOST, MONGO_PORT, MONGO_USERNAME, MONGO_PASSWORD, MONGO_AUTH_DB, MONGO_DATABASE

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.users = None
        self.messages = None
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
            
            # Создаем индексы для оптимизации
            self.users.create_index("chat_id", unique=True)
            self.messages.create_index([("chat_id", 1), ("timestamp", DESCENDING)])
            self.messages.create_index("is_read")
            
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
            "name": f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip(),
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

# Глобальный экземпляр базы данных
db = Database()

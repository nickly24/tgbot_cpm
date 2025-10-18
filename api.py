from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import ObjectId
from database import db
from telegram_bot import telegram_bot

def convert_objectid(obj):
    """Конвертирует ObjectId в строку для JSON сериализации"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_objectid(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    return obj

def get_client_statuses_dict():
    """Получить статусы клиентов в виде словаря {value: label}"""
    statuses = db.get_client_statuses()
    if statuses:
        return {s['value']: s['label'] for s in statuses}
    return {"student": "Студент", "reserve": "Резерв"}

# Создаем Blueprint для API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Обработчик для CORS preflight запросов
@api_bp.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({})
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response

# Добавляем CORS заголовки ко всем ответам
@api_bp.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# ==================== ЧАТЫ ====================

@api_bp.route('/chats', methods=['GET'])
def get_all_chats():
    """Получить список всех чатов"""
    try:
        chats = db.get_all_chats()
        # Конвертируем ObjectId в строки
        chats = convert_objectid(chats)
        return jsonify({
            "success": True,
            "data": chats
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/chats/<int:chat_id>', methods=['GET'])
def get_chat_history(chat_id):
    """Получить историю конкретного чата"""
    try:
        messages = db.get_chat_messages(chat_id)
        user_info = db.get_user(chat_id)
        unread_count = db.get_unread_count(chat_id)
        
        # Конвертируем ObjectId в строки
        messages = convert_objectid(messages)
        user_info = convert_objectid(user_info) if user_info else None
        
        return jsonify({
            "success": True,
            "data": {
                "chat_id": chat_id,
                "user_info": {
                    "user_id": user_info.get("user_id"),
                    "username": user_info.get("username"),
                    "name": user_info.get("name"),
                    "created_at": user_info.get("created_at")
                } if user_info else None,
                "status": user_info.get("status") if user_info else None,
                "status_name": get_client_statuses_dict().get(user_info.get("status")) if user_info and user_info.get("status") else None,
                "messages": messages,
                "unread_count": unread_count
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/chats/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Удалить чат со всеми сообщениями"""
    try:
        # Проверяем, существует ли чат
        user = db.get_user(chat_id)
        if not user:
            return jsonify({
                "success": False,
                "error": "Чат не найден"
            }), 404
        
        # Удаляем чат
        result = db.delete_chat(chat_id)
        
        if result is None:
            return jsonify({
                "success": False,
                "error": "Ошибка при удалении чата"
            }), 500
        
        return jsonify({
            "success": True,
            "message": "Чат успешно удален",
            "deleted": {
                "user": result["user_deleted"],
                "messages_count": result["messages_deleted"]
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== СООБЩЕНИЯ ====================

@api_bp.route('/chats/<int:chat_id>/send', methods=['POST'])
def send_message_to_chat(chat_id):
    """Отправить сообщение в чат от имени администратора"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Поле 'message' обязательно"
            }), 400
        
        message_text = data['message'].strip()
        if not message_text:
            return jsonify({
                "success": False,
                "error": "Сообщение не может быть пустым"
            }), 400
        
        admin_name = data.get('admin_name', 'Администратор')
        
        # Отправляем сообщение через Telegram бота (синхронный метод)
        result = telegram_bot.send_message_sync(chat_id, message_text, admin_name)
        
        if result:
            return jsonify({
                "success": True,
                "message": "Сообщение отправлено успешно"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Не удалось отправить сообщение"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/chats/<int:chat_id>/mark-read', methods=['POST'])
def mark_chat_as_read(chat_id):
    """Пометить все сообщения клиента как прочитанные"""
    try:
        count = db.mark_messages_as_read(chat_id)
        
        return jsonify({
            "success": True,
            "message": f"Помечено как прочитано: {count} сообщений",
            "marked_count": count
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== ПОЛЬЗОВАТЕЛИ ====================

@api_bp.route('/chats/<int:chat_id>/user', methods=['GET'])
def get_user_info(chat_id):
    """Получить информацию о пользователе чата"""
    try:
        user_info = db.get_user(chat_id)
        
        if user_info:
            user_data = convert_objectid(user_info)
            # Добавляем читаемое название статуса
            if user_data.get("status"):
                user_data["status_name"] = get_client_statuses_dict().get(user_data["status"])
            
            return jsonify({
                "success": True,
                "data": user_data
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Информация о пользователе не найдена"
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/chats/<int:chat_id>/name', methods=['PUT'])
def update_user_name(chat_id):
    """Обновить имя пользователя в чате"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                "success": False,
                "error": "Поле 'name' обязательно"
            }), 400
        
        new_name = data['name'].strip()
        if not new_name:
            return jsonify({
                "success": False,
                "error": "Имя не может быть пустым"
            }), 400
        
        success = db.update_user_name(chat_id, new_name)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Имя пользователя обновлено успешно"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Не удалось обновить имя пользователя"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== СТАТУСЫ ====================

@api_bp.route('/chats/<int:chat_id>/status', methods=['GET'])
def get_user_status(chat_id):
    """Получить статус пользователя"""
    try:
        user_info = db.get_user(chat_id)
        
        if user_info:
            status = user_info.get("status")
            return jsonify({
                "success": True,
                "data": {
                    "chat_id": chat_id,
                    "status": status,
                    "status_name": get_client_statuses_dict().get(status) if status else None
                }
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Пользователь не найден"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/chats/<int:chat_id>/status', methods=['PUT'])
def update_user_status(chat_id):
    """Обновить статус пользователя"""
    try:
        data = request.get_json()
        
        if not data or 'status' not in data:
            return jsonify({
                "success": False,
                "error": "Поле 'status' обязательно"
            }), 400
        
        status = data['status'].strip()
        if not status:
            return jsonify({
                "success": False,
                "error": "Статус не может быть пустым"
            }), 400
        
        # Проверяем, что статус валидный
        valid_statuses = get_client_statuses_dict()
        if status not in valid_statuses:
            return jsonify({
                "success": False,
                "error": f"Недопустимый статус. Доступные: {', '.join(valid_statuses.keys())}"
            }), 400
        
        success = db.update_user_status(chat_id, status)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Статус пользователя обновлен успешно",
                "status_name": get_client_statuses_dict().get(status)
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Не удалось обновить статус пользователя"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/statuses', methods=['GET'])
def get_all_statuses():
    """Получить список всех доступных статусов (совместимость со старым API)"""
    try:
        statuses_from_db = db.get_client_statuses()
        
        if statuses_from_db:
            # Преобразуем в старый формат для совместимости
            statuses = [
                {
                    "value": s.get('value'),
                    "label": s.get('label')
                }
                for s in sorted(statuses_from_db, key=lambda x: x.get('order', 999))
            ]
        else:
            # Fallback на дефолтные
            statuses = [
                {"value": "student", "label": "Студент"},
                {"value": "reserve", "label": "Резерв"}
            ]
        
        return jsonify({
            "success": True,
            "data": statuses
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== СЛУЖЕБНЫЕ ====================

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Проверка состояния API"""
    return jsonify({
        "success": True,
        "message": "API работает",
        "timestamp": datetime.now().isoformat()
    }), 200

@api_bp.route('/stats', methods=['GET'])
def get_statistics():
    """Получить общую статистику"""
    try:
        all_chats = db.get_all_chats()
        
        total_chats = len(all_chats)
        total_unread = sum(chat.get('unread_count', 0) for chat in all_chats)
        
        # Статистика по статусам
        status_stats = {}
        for chat in all_chats:
            status = chat.get('status')
            if status:
                status_stats[status] = status_stats.get(status, 0) + 1
        
        return jsonify({
            "success": True,
            "data": {
                "total_chats": total_chats,
                "total_unread_messages": total_unread,
                "status_distribution": status_stats
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== МАССОВАЯ РАССЫЛКА ====================

@api_bp.route('/broadcast', methods=['POST'])
def broadcast_message():
    """Массовая рассылка сообщений по статусам"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                "success": False,
                "error": "Поле 'message' обязательно"
            }), 400
        
        message_text = data['message'].strip()
        if not message_text:
            return jsonify({
                "success": False,
                "error": "Сообщение не может быть пустым"
            }), 400
        
        # Параметры рассылки
        target_statuses = data.get('statuses', [])  # Список статусов или пусто для всех
        admin_name = data.get('admin_name', 'Администратор')
        
        # Валидация статусов
        if target_statuses:
            valid_statuses = get_client_statuses_dict()
            for status in target_statuses:
                if status not in valid_statuses:
                    return jsonify({
                        "success": False,
                        "error": f"Недопустимый статус: {status}"
                    }), 400
        
        # Получаем всех пользователей
        all_users = db.get_all_users()
        
        # Фильтруем по статусам если указаны
        target_users = []
        for user in all_users:
            user_status = user.get('status')
            # Если статусы не указаны - отправляем всем
            # Если указаны - только тем, кто в списке
            if not target_statuses or user_status in target_statuses:
                if user_status:  # Только пользователи с выбранным статусом
                    target_users.append(user)
        
        if not target_users:
            return jsonify({
                "success": False,
                "error": "Нет пользователей с указанными статусами"
            }), 400
        
        # Отправляем сообщения (синхронный метод)
        success_count = 0
        failed_count = 0
        failed_chats = []
        
        for user in target_users:
            chat_id = user.get('chat_id')
            try:
                result = telegram_bot.send_message_sync(chat_id, message_text, admin_name)
                if result:
                    success_count += 1
                else:
                    failed_count += 1
                    failed_chats.append(chat_id)
            except Exception as e:
                failed_count += 1
                failed_chats.append(chat_id)
                print(f"Ошибка отправки в чат {chat_id}: {e}")
        
        return jsonify({
            "success": True,
            "message": f"Рассылка завершена",
            "stats": {
                "total_target": len(target_users),
                "success": success_count,
                "failed": failed_count,
                "failed_chats": failed_chats
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== СООБЩЕНИЯ БОТА ====================

@api_bp.route('/bot-messages', methods=['GET'])
def get_bot_messages():
    """Получить все сообщения бота"""
    try:
        messages = db.get_bot_messages()
        
        if messages is None:
            return jsonify({
                "success": False,
                "error": "Сообщения бота не найдены"
            }), 404
        
        return jsonify({
            "success": True,
            "data": messages
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/bot-messages', methods=['PUT'])
def update_bot_messages():
    """Обновить все сообщения бота"""
    try:
        data = request.get_json()
        
        if not data or 'messages' not in data:
            return jsonify({
                "success": False,
                "error": "Поле 'messages' обязательно"
            }), 400
        
        messages = data['messages']
        if not isinstance(messages, dict):
            return jsonify({
                "success": False,
                "error": "Поле 'messages' должно быть объектом"
            }), 400
        
        success = db.update_bot_messages(messages)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Сообщения бота обновлены успешно"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Не удалось обновить сообщения"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/bot-messages/<message_key>', methods=['GET'])
def get_bot_message(message_key):
    """Получить конкретное сообщение бота"""
    try:
        message = db.get_bot_message(message_key)
        
        if message is None:
            return jsonify({
                "success": False,
                "error": f"Сообщение '{message_key}' не найдено"
            }), 404
        
        return jsonify({
            "success": True,
            "data": {
                "key": message_key,
                "text": message
            }
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/bot-messages/<message_key>', methods=['PUT'])
def update_bot_message(message_key):
    """Обновить конкретное сообщение бота"""
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({
                "success": False,
                "error": "Поле 'text' обязательно"
            }), 400
        
        text = data['text']
        if not isinstance(text, str) or not text.strip():
            return jsonify({
                "success": False,
                "error": "Текст сообщения не может быть пустым"
            }), 400
        
        success = db.update_bot_message(message_key, text)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"Сообщение '{message_key}' обновлено успешно"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Не удалось обновить сообщение"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ==================== УПРАВЛЕНИЕ СТАТУСАМИ ====================

@api_bp.route('/config/statuses', methods=['GET'])
def get_config_statuses():
    """Получить все статусы клиентов из конфигурации"""
    try:
        statuses = db.get_client_statuses()
        
        if statuses is None:
            return jsonify({
                "success": False,
                "error": "Статусы не найдены"
            }), 404
        
        return jsonify({
            "success": True,
            "data": statuses
        }), 200
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/config/statuses', methods=['POST'])
def add_config_status():
    """Добавить новый статус клиента"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Отсутствуют данные"
            }), 400
        
        # Проверяем обязательные поля
        required_fields = ['value', 'label']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"Поле '{field}' обязательно"
                }), 400
        
        value = data['value'].strip()
        label = data['label'].strip()
        
        if not value or not label:
            return jsonify({
                "success": False,
                "error": "Значение и название не могут быть пустыми"
            }), 400
        
        # Проверяем, что value состоит из букв, цифр и подчеркиваний
        if not value.replace('_', '').isalnum():
            return jsonify({
                "success": False,
                "error": "Значение (value) может содержать только буквы, цифры и подчеркивания"
            }), 400
        
        # Получаем текущие статусы
        existing_statuses = db.get_client_statuses() or []
        
        # Определяем следующий order
        max_order = max([s.get('order', 0) for s in existing_statuses], default=-1)
        
        status_data = {
            "value": value,
            "label": label,
            "emoji": data.get('emoji', ''),
            "is_system": False,  # Новые статусы всегда не системные
            "order": max_order + 1,
            "created_at": datetime.now().isoformat()
        }
        
        success = db.add_client_status(status_data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Статус добавлен успешно",
                "data": status_data
            }), 201
        else:
            return jsonify({
                "success": False,
                "error": "Не удалось добавить статус (возможно, такой статус уже существует)"
            }), 400
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/config/statuses/<status_value>', methods=['PUT'])
def update_config_status(status_value):
    """Обновить существующий статус"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Отсутствуют данные"
            }), 400
        
        # Получаем текущий статус
        statuses = db.get_client_statuses() or []
        current_status = next((s for s in statuses if s.get('value') == status_value), None)
        
        if not current_status:
            return jsonify({
                "success": False,
                "error": "Статус не найден"
            }), 404
        
        # Подготавливаем данные для обновления
        update_data = {}
        
        if 'label' in data:
            label = data['label'].strip()
            if not label:
                return jsonify({
                    "success": False,
                    "error": "Название не может быть пустым"
                }), 400
            update_data['label'] = label
        
        if 'emoji' in data:
            update_data['emoji'] = data['emoji']
        
        if 'order' in data:
            update_data['order'] = data['order']
        
        # Для не системных статусов можно изменить value
        if not current_status.get('is_system', False) and 'value' in data:
            new_value = data['value'].strip()
            if not new_value.replace('_', '').isalnum():
                return jsonify({
                    "success": False,
                    "error": "Значение (value) может содержать только буквы, цифры и подчеркивания"
                }), 400
            update_data['value'] = new_value
        
        if not update_data:
            return jsonify({
                "success": False,
                "error": "Нет данных для обновления"
            }), 400
        
        success = db.update_client_status(status_value, update_data)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Статус обновлен успешно"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Не удалось обновить статус"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_bp.route('/config/statuses/<status_value>', methods=['DELETE'])
def delete_config_status(status_value):
    """Удалить статус клиента (только не системные)"""
    try:
        # Получаем текущий статус
        statuses = db.get_client_statuses() or []
        current_status = next((s for s in statuses if s.get('value') == status_value), None)
        
        if not current_status:
            return jsonify({
                "success": False,
                "error": "Статус не найден"
            }), 404
        
        if current_status.get('is_system', False):
            return jsonify({
                "success": False,
                "error": "Нельзя удалить системный статус"
            }), 403
        
        success = db.delete_client_status(status_value)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Статус удален успешно"
            }), 200
        else:
            return jsonify({
                "success": False,
                "error": "Не удалось удалить статус"
            }), 500
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

from flask import Blueprint, request, jsonify
from datetime import datetime
from bson import ObjectId
from database import db
from telegram_bot import telegram_bot
from config import CLIENT_STATUSES

def convert_objectid(obj):
    """Конвертирует ObjectId в строку для JSON сериализации"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: convert_objectid(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    return obj

# Создаем Blueprint для API
api_bp = Blueprint('api', __name__, url_prefix='/api')

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
                "status_name": CLIENT_STATUSES.get(user_info.get("status")) if user_info and user_info.get("status") else None,
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
                user_data["status_name"] = CLIENT_STATUSES.get(user_data["status"])
            
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
                    "status_name": CLIENT_STATUSES.get(status) if status else None
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
        if status not in CLIENT_STATUSES:
            return jsonify({
                "success": False,
                "error": f"Недопустимый статус. Доступные: {', '.join(CLIENT_STATUSES.keys())}"
            }), 400
        
        success = db.update_user_status(chat_id, status)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Статус пользователя обновлен успешно",
                "status_name": CLIENT_STATUSES.get(status)
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
    """Получить список всех доступных статусов"""
    try:
        statuses = [
            {
                "value": key,
                "label": value
            }
            for key, value in CLIENT_STATUSES.items()
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
            for status in target_statuses:
                if status not in CLIENT_STATUSES:
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

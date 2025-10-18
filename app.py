from flask import Flask, jsonify
from flask_cors import CORS
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from api import api_bp
from database import db

# Создаем Flask приложение
app = Flask(__name__)

# Настройка CORS для работы с фронтендом
CORS(app, 
     origins=[
         "https://tgbot-admin.cpm-lms.ru",
         "http://localhost:3000",
         "http://127.0.0.1:3000"
     ],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=True
)

# Регистрируем Blueprint для API
app.register_blueprint(api_bp)

@app.route('/')
def index():
    """Главная страница"""
    return jsonify({
        "message": "Telegram Bot API Server",
        "version": "2.2.0",
        "endpoints": {
            "GET /api/chats": "Получить список всех чатов",
            "GET /api/chats/<chat_id>": "Получить историю конкретного чата",
            "DELETE /api/chats/<chat_id>": "Удалить чат со всеми сообщениями",
            "POST /api/chats/<chat_id>/send": "Отправить сообщение в чат",
            "POST /api/chats/<chat_id>/mark-read": "Пометить сообщения как прочитанные",
            "GET /api/chats/<chat_id>/user": "Получить информацию о пользователе",
            "PUT /api/chats/<chat_id>/name": "Обновить имя пользователя",
            "GET /api/chats/<chat_id>/status": "Получить статус пользователя",
            "PUT /api/chats/<chat_id>/status": "Обновить статус пользователя",
            "GET /api/statuses": "Получить список всех статусов (упрощенный)",
            "POST /api/broadcast": "Массовая рассылка по статусам",
            "GET /api/stats": "Получить общую статистику",
            "GET /api/health": "Проверка состояния API",
            "": "",
            "🆕 НАСТРОЙКИ БОТА v2.2": "",
            "GET /api/bot-messages": "Получить все сообщения бота 🆕",
            "PUT /api/bot-messages": "Обновить все сообщения бота 🆕",
            "GET /api/bot-messages/<key>": "Получить конкретное сообщение бота 🆕",
            "PUT /api/bot-messages/<key>": "Обновить конкретное сообщение бота 🆕",
            " ": "",
            "GET /api/config/statuses": "Получить все статусы (полная информация) 🆕",
            "POST /api/config/statuses": "Добавить новый статус 🆕",
            "PUT /api/config/statuses/<value>": "Обновить статус 🆕",
            "DELETE /api/config/statuses/<value>": "Удалить статус 🆕"
        }
    })

@app.route('/api/docs')
def api_docs():
    """Документация API"""
    return jsonify({
        "API Documentation": {
            "GET /api/chats": {
                "description": "Получить список всех чатов",
                "response": {
                    "success": "boolean",
                    "data": "array of chat objects"
                }
            },
            "GET /api/chats/<chat_id>": {
                "description": "Получить историю конкретного чата",
                "parameters": {
                    "chat_id": "ID чата (integer)"
                },
                "response": {
                    "success": "boolean",
                    "data": {
                        "chat_id": "integer",
                        "user_info": "object",
                        "status": "string",
                        "status_name": "string",
                        "messages": "array of message objects",
                        "unread_count": "integer"
                    }
                }
            },
            "POST /api/chats/<chat_id>/send": {
                "description": "Отправить сообщение в чат от имени администратора",
                "parameters": {
                    "chat_id": "ID чата (integer)"
                },
                "request_body": {
                    "message": "string (обязательно)",
                    "admin_name": "string (опционально, по умолчанию 'Администратор')"
                },
                "example": {
                    "message": "Привет! Как дела?",
                    "admin_name": "Администратор"
                },
                "response": {
                    "success": "boolean",
                    "message": "string"
                }
            },
            "POST /api/chats/<chat_id>/mark-read": {
                "description": "Пометить все сообщения клиента как прочитанные",
                "parameters": {
                    "chat_id": "ID чата (integer)"
                },
                "response": {
                    "success": "boolean",
                    "message": "string",
                    "marked_count": "integer"
                }
            },
            "GET /api/chats/<chat_id>/user": {
                "description": "Получить информацию о пользователе чата",
                "parameters": {
                    "chat_id": "ID чата (integer)"
                },
                "response": {
                    "success": "boolean",
                    "data": "user info object"
                }
            },
            "PUT /api/chats/<chat_id>/name": {
                "description": "Обновить имя пользователя в чате",
                "parameters": {
                    "chat_id": "ID чата (integer)"
                },
                "request_body": {
                    "name": "string (обязательно) - новое имя пользователя"
                },
                "example": {
                    "name": "Иван Петров"
                },
                "response": {
                    "success": "boolean",
                    "message": "string"
                }
            },
            "GET /api/chats/<chat_id>/status": {
                "description": "Получить статус пользователя",
                "parameters": {
                    "chat_id": "ID чата (integer)"
                },
                "response": {
                    "success": "boolean",
                    "data": {
                        "chat_id": "integer",
                        "status": "string",
                        "status_name": "string"
                    }
                }
            },
            "PUT /api/chats/<chat_id>/status": {
                "description": "Обновить статус пользователя",
                "parameters": {
                    "chat_id": "ID чата (integer)"
                },
                "request_body": {
                    "status": "string (обязательно) - один из: student, applicant, parent_student, parent_applicant"
                },
                "example": {
                    "status": "student"
                },
                "response": {
                    "success": "boolean",
                    "message": "string",
                    "status_name": "string"
                }
            },
            "GET /api/statuses": {
                "description": "Получить список всех доступных статусов",
                "response": {
                    "success": "boolean",
                    "data": "array of status objects"
                }
            },
            "GET /api/stats": {
                "description": "Получить общую статистику",
                "response": {
                    "success": "boolean",
                    "data": {
                        "total_chats": "integer",
                        "total_unread_messages": "integer",
                        "status_distribution": "object"
                    }
                }
            },
            "GET /api/health": {
                "description": "Проверка состояния API",
                "response": {
                    "success": "boolean",
                    "message": "string",
                    "timestamp": "string"
                }
            }
        },
        "Available Statuses": "GET /api/config/statuses для получения актуального списка"
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

import logging
from datetime import datetime
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, CLIENT_STATUSES
from database import db

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд и сообщений"""
        # ВАЖНО: CallbackQueryHandler ПЕРВЫМ!!! Иначе MessageHandler может перехватить
        self.application.add_handler(CallbackQueryHandler(self.handle_status_selection))
        
        # Обработчик команды /start
        self.application.add_handler(CommandHandler("start", self.start_command))
        
        # Обработчик текстовых сообщений
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        # Обработчик всех остальных типов сообщений (фото, видео, голосовые и т.д.)
        self.application.add_handler(MessageHandler(
            filters.PHOTO | filters.VIDEO | filters.VOICE | filters.Document.ALL | filters.VIDEO_NOTE,
            self.handle_unsupported_message
        ))
    
    def create_status_keyboard(self):
        """Создать клавиатуру для выбора статуса"""
        keyboard = [
            [
                InlineKeyboardButton("👨‍🎓 Студент", callback_data="status_student"),
                InlineKeyboardButton("🎓 Абитуриент", callback_data="status_applicant")
            ],
            [
                InlineKeyboardButton("👨‍👦 Родитель студента", callback_data="status_parent_student"),
                InlineKeyboardButton("👨‍👧 Родитель абитуриента", callback_data="status_parent_applicant")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Проверяем, есть ли уже пользователь в БД
        existing_user = db.get_user(chat_id)
        
        if existing_user and existing_user.get("status"):
            # Пользователь уже выбрал статус
            welcome_message = (
                f"С возвращением, {user.first_name}! 👋\n\n"
                f"Ваш статус: {CLIENT_STATUSES.get(existing_user['status'], 'не указан')}\n\n"
                f"Отправляйте мне текстовые сообщения, и я передам их администратору."
            )
            await update.message.reply_text(welcome_message)
        else:
            # Новый пользователь - сохраняем базовую информацию
            user_info = {
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
            db.save_user(chat_id, user_info, status=None)
            
            # Просим выбрать статус
            welcome_message = (
                f"Привет, {user.first_name}! 👋\n\n"
                f"Я бот для связи с администратором.\n\n"
                f"Пожалуйста, выберите кто вы:"
            )
            keyboard = self.create_status_keyboard()
            await update.message.reply_text(welcome_message, reply_markup=keyboard)
    
    async def handle_status_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка выбора статуса через inline кнопки"""
        query = update.callback_query
        
        if not query:
            return
        
        await query.answer()
        
        chat_id = query.message.chat_id
        callback_data = query.data
        
        # Извлекаем статус из callback_data
        if callback_data.startswith("status_"):
            status = callback_data.replace("status_", "")
            
            # Обновляем статус пользователя
            success = db.update_user_status(chat_id, status)
            
            if not success:
                logger.error(f"Не удалось обновить статус для пользователя {chat_id}")
                await query.edit_message_text(text="❌ Ошибка при сохранении статуса. Попробуйте еще раз с /start")
                return
            
            status_name = CLIENT_STATUSES.get(status, "Неизвестный статус")
            
            confirmation_message = (
                f"✅ Отлично! Вы выбрали статус: {status_name}\n\n"
                f"Теперь можете отправлять мне текстовые сообщения, и я передам их администратору."
            )
            
            await query.edit_message_text(text=confirmation_message)
            
            logger.info(f"Пользователь {chat_id} выбрал статус: {status}")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        message_text = update.message.text
        
        # Проверяем, выбрал ли пользователь статус
        existing_user = db.get_user(chat_id)
        
        if not existing_user or not existing_user.get("status"):
            # Пользователь еще не выбрал статус
            reminder_message = "⚠️ Пожалуйста, сначала выберите ваш статус с помощью кнопок выше."
            keyboard = self.create_status_keyboard()
            await update.message.reply_text(reminder_message, reply_markup=keyboard)
            return
        
        # Сохраняем сообщение в базу данных
        message_data = {
            "message_id": update.message.message_id,
            "text": message_text,
            "timestamp": datetime.now().isoformat(),
            "from_user": True,
            "is_read": False  # Новое сообщение от клиента - непрочитанное
        }
        
        db.save_message(chat_id, message_data)
        
        # Обновляем время последней активности пользователя
        db.users.update_one(
            {"chat_id": chat_id},
            {"$set": {"updated_at": datetime.now().isoformat()}}
        )
        
        # Отправляем подтверждение пользователю
        confirmation_message = "✅ Ваше сообщение получено и передано администратору. Ожидайте ответа!"
        await update.message.reply_text(confirmation_message)
        
        logger.info(f"Получено сообщение от пользователя {chat_id} ({existing_user.get('status')}): {message_text}")
    
    async def handle_unsupported_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка неподдерживаемых типов сообщений"""
        unsupported_message = "❌ Извините, я обрабатываю только текстовые сообщения. Пожалуйста, отправьте текст."
        await update.message.reply_text(unsupported_message)
        
        logger.info(f"Получено неподдерживаемое сообщение от пользователя {update.effective_chat.id}")
    
    def send_message_sync(self, chat_id: int, message_text: str, admin_name: str = "Администратор"):
        """Синхронная отправка сообщения пользователю (для вызова из API)"""
        try:
            # Отправляем сообщение напрямую через Telegram API
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json={
                    "chat_id": chat_id,
                    "text": f"📩 Сообщение от {admin_name}:\n\n{message_text}"
                })
                response.raise_for_status()
            
            # Сохраняем сообщение в базу данных
            message_data = {
                "text": message_text,
                "timestamp": datetime.now().isoformat(),
                "from_user": False,  # Сообщение от администратора
                "admin_name": admin_name,
                "is_read": True  # Сообщения от админа всегда "прочитаны"
            }
            
            db.save_message(chat_id, message_data)
            
            logger.info(f"Отправлено сообщение пользователю {chat_id} от {admin_name}: {message_text}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения пользователю {chat_id}: {e}")
            return False
    
    async def send_message_to_user(self, chat_id: int, message_text: str, admin_name: str = "Администратор"):
        """Асинхронная отправка сообщения пользователю (для внутреннего использования бота)"""
        try:
            # Отправляем сообщение пользователю
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=f"📩 Сообщение от {admin_name}:\n\n{message_text}"
            )
            
            # Сохраняем сообщение в базу данных
            message_data = {
                "text": message_text,
                "timestamp": datetime.now().isoformat(),
                "from_user": False,  # Сообщение от администратора
                "admin_name": admin_name,
                "is_read": True  # Сообщения от админа всегда "прочитаны"
            }
            
            db.save_message(chat_id, message_data)
            
            logger.info(f"Отправлено сообщение пользователю {chat_id} от {admin_name}: {message_text}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения пользователю {chat_id}: {e}")
            return False
    
    def run(self):
        """Запуск бота"""
        logger.info("🤖 Запуск Telegram бота...")
        # ВАЖНО: Явно указываем, что хотим получать callback_query
        self.application.run_polling(allowed_updates=["message", "callback_query"])

# Глобальный экземпляр бота
telegram_bot = TelegramBot()

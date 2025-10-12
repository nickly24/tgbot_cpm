import logging
from datetime import datetime
import httpx
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN
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
    
    def get_message(self, key, **kwargs):
        """Получить сообщение бота из БД и заполнить плейсхолдеры"""
        message = db.get_bot_message(key)
        if message:
            return message.format(**kwargs)
        # Fallback на дефолтные сообщения если что-то пошло не так
        return self._get_default_message(key, **kwargs)
    
    def _get_default_message(self, key, **kwargs):
        """Дефолтные сообщения на случай проблем с БД"""
        defaults = {
            "welcome": "Привет! 👋\n\nЯ бот для связи с администратором.\n\nКак мне вас называть? Напишите ваше имя:",
            "ask_status": "Приятно познакомиться, {name}! 😊\n\nТеперь выберите, кто вы:",
            "status_selected": "✅ Отлично! Вы выбрали статус: {status_name}\n\nТеперь можете отправлять мне текстовые сообщения, и я передам их администратору.",
            "welcome_back": "С возвращением, {name}! 👋\n\nВаш статус: {status_name}\n\nОтправляйте мне текстовые сообщения, и я передам их администратору.",
            "message_received": "✅ Ваше сообщение получено и передано администратору. Ожидайте ответа!",
            "unsupported_message": "❌ Извините, я обрабатываю только текстовые сообщения. Пожалуйста, отправьте текст.",
            "need_status": "⚠️ Пожалуйста, сначала выберите ваш статус с помощью кнопок выше.",
            "admin_message_prefix": "📩 Сообщение от {admin_name}:\n\n"
        }
        message = defaults.get(key, "")
        if message:
            return message.format(**kwargs)
        return ""
    
    def get_client_statuses(self):
        """Получить статусы клиентов из БД"""
        statuses = db.get_client_statuses()
        if statuses:
            # Преобразуем в словарь для совместимости
            return {s['value']: s['label'] for s in statuses}
        # Fallback на дефолтные статусы
        return {
            "student": "Студент",
            "reserve": "Резерв"
        }
    
    def get_client_statuses_list(self):
        """Получить список статусов для клавиатуры"""
        statuses = db.get_client_statuses()
        if statuses:
            # Сортируем по order
            return sorted(statuses, key=lambda x: x.get('order', 999))
        return []
    
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
        statuses_list = self.get_client_statuses_list()
        
        if not statuses_list:
            # Fallback на дефолтные кнопки
            keyboard = [
                [InlineKeyboardButton("👨‍🎓 Студент", callback_data="status_student")],
                [InlineKeyboardButton("📝 Резерв", callback_data="status_reserve")]
            ]
            return InlineKeyboardMarkup(keyboard)
        
        # Создаем кнопки из статусов БД
        keyboard = []
        row = []
        
        for status in statuses_list:
            emoji = status.get('emoji', '')
            label = status.get('label', '')
            value = status.get('value', '')
            
            button_text = f"{emoji} {label}" if emoji else label
            button = InlineKeyboardButton(button_text, callback_data=f"status_{value}")
            
            row.append(button)
            
            # По 2 кнопки в ряд
            if len(row) == 2:
                keyboard.append(row)
                row = []
        
        # Добавляем оставшиеся кнопки
        if row:
            keyboard.append(row)
        
        return InlineKeyboardMarkup(keyboard)
    
    async def validate_student(self, username):
        """Проверка студента по username через внешний API"""
        if not username:
            return None
        
        try:
            url = "https://nickly24-cpm-serv-f15d.twc1.net/api/validate-student-by-tg"
            
            with httpx.Client(timeout=10.0) as client:
                response = client.post(url, json={"tg_name": username})
                response.raise_for_status()
                data = response.json()
                
                if data.get('status') and data.get('student_data'):
                    return data['student_data']
                return None
        except Exception as e:
            logger.error(f"Ошибка проверки студента {username}: {e}")
            return None
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Проверяем, есть ли уже пользователь в БД
        existing_user = db.get_user(chat_id)
        
        if existing_user and existing_user.get("status") and existing_user.get("name"):
            # Пользователь уже прошел регистрацию
            client_statuses = self.get_client_statuses()
            status_name = client_statuses.get(existing_user['status'], 'не указан')
            
            welcome_message = self.get_message(
                "welcome_back", 
                name=existing_user.get('name'),
                status_name=status_name
            )
            await update.message.reply_text(welcome_message)
        else:
            # Новый пользователь или не завершил регистрацию
            # Сохраняем базовую информацию
            user_info = {
                "user_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
            db.save_user(chat_id, user_info, status=None)
            
            # НОВАЯ ЛОГИКА: Сразу показываем выбор роли
            welcome_message = "Привет! 👋\n\nЯ бот для связи с администратором.\n\nВыберите, кто вы:"
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
        user = query.from_user
        
        # Извлекаем статус из callback_data
        if callback_data.startswith("status_"):
            status = callback_data.replace("status_", "")
            
            # Проверяем, системная ли роль (студент или резерв)
            if status in ['student', 'reserve']:
                # Проверяем студента через API
                await query.edit_message_text(text="⏳ Проверяем данные...")
                
                student_data = await self.validate_student(user.username)
                
                if not student_data:
                    # Студент не найден - отказываем
                    error_message = (
                        "❌ К сожалению, вы не найдены в базе студентов.\n\n"
                        "Для регистрации как студент или резерв вы должны быть в базе учебного заведения.\n\n"
                        "Если вы не студент, выберите другую роль:"
                    )
                    keyboard = self.create_status_keyboard()
                    await query.edit_message_text(text=error_message, reply_markup=keyboard)
                    logger.warning(f"Пользователь {chat_id} (@{user.username}) не найден в базе студентов")
                    return
                
                # Студент найден - берём ФИО с сервера
                full_name = student_data.get('full_name', 'Студент')
                
                # Обновляем имя и статус
                db.update_user_name(chat_id, full_name)
                db.update_user_status(chat_id, status)
                
                client_statuses = self.get_client_statuses()
                status_name = client_statuses.get(status, status)
                
                confirmation_message = (
                    f"✅ Добро пожаловать, {full_name}!\n\n"
                    f"Вы успешно зарегистрированы как: {status_name}\n\n"
                    f"Теперь можете отправлять мне текстовые сообщения, и я передам их администратору."
                )
                
                await query.edit_message_text(text=confirmation_message)
                logger.info(f"Студент {chat_id} (@{user.username}) зарегистрирован: {full_name} - {status}")
                
            else:
                # Не системная роль - просим ввести имя
                db.update_user_status(chat_id, status)
                
                client_statuses = self.get_client_statuses()
                status_name = client_statuses.get(status, status)
                
                ask_name_message = (
                    f"✅ Вы выбрали статус: {status_name}\n\n"
                    f"Теперь напишите ваше имя:"
                )
                
                await query.edit_message_text(text=ask_name_message)
                logger.info(f"Пользователь {chat_id} выбрал статус: {status}, ожидает ввода имени")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        message_text = update.message.text
        
        # Проверяем статус пользователя
        existing_user = db.get_user(chat_id)
        
        # Если пользователя нет вообще - редирект на /start
        if not existing_user:
            await update.message.reply_text("⚠️ Пожалуйста, начните с команды /start")
            return
        
        # Если есть статус, но нет имени - значит ожидаем ввод имени (для не системных ролей)
        if existing_user.get("status") and not existing_user.get("name"):
            # Сохраняем введенное имя
            db.update_user_name(chat_id, message_text.strip())
            
            client_statuses = self.get_client_statuses()
            status_name = client_statuses.get(existing_user.get("status"), "")
            
            confirmation_message = (
                f"✅ Отлично, {message_text.strip()}!\n\n"
                f"Вы успешно зарегистрированы как: {status_name}\n\n"
                f"Теперь можете отправлять мне текстовые сообщения, и я передам их администратору."
            )
            
            await update.message.reply_text(confirmation_message)
            logger.info(f"Пользователь {chat_id} завершил регистрацию: {message_text.strip()} - {existing_user.get('status')}")
            return
        
        # Если нет статуса - просим выбрать
        if not existing_user.get("status"):
            reminder_message = "⚠️ Пожалуйста, сначала выберите вашу роль:"
            keyboard = self.create_status_keyboard()
            await update.message.reply_text(reminder_message, reply_markup=keyboard)
            return
        
        # Если нет имени (но есть статус) - что-то пошло не так
        if not existing_user.get("name"):
            await update.message.reply_text("⚠️ Ошибка регистрации. Попробуйте /start")
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
        confirmation_message = self.get_message("message_received")
        await update.message.reply_text(confirmation_message)
        
        logger.info(f"Получено сообщение от пользователя {chat_id} ({existing_user.get('status')}): {message_text}")
    
    async def handle_unsupported_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка неподдерживаемых типов сообщений"""
        unsupported_message = self.get_message("unsupported_message")
        await update.message.reply_text(unsupported_message)
        
        logger.info(f"Получено неподдерживаемое сообщение от пользователя {update.effective_chat.id}")
    
    def send_message_sync(self, chat_id: int, message_text: str, admin_name: str = "Администратор"):
        """Синхронная отправка сообщения пользователю (для вызова из API)"""
        try:
            # Получаем префикс из БД
            prefix = self.get_message("admin_message_prefix", admin_name=admin_name)
            full_message = f"{prefix}{message_text}"
            
            # Отправляем сообщение напрямую через Telegram API
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            
            with httpx.Client(timeout=30.0) as client:
                response = client.post(url, json={
                    "chat_id": chat_id,
                    "text": full_message
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
            # Получаем префикс из БД
            prefix = self.get_message("admin_message_prefix", admin_name=admin_name)
            full_message = f"{prefix}{message_text}"
            
            # Отправляем сообщение пользователю
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=full_message
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

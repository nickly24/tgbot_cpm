import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB конфигурация
MONGO_HOST = os.getenv("MONGO_HOST", "109.73.202.73")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "gen_user")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "77tanufe")
MONGO_AUTH_DB = os.getenv("MONGO_AUTH_DB", "admin")
MONGO_DATABASE = os.getenv("MONGO_DATABASE", "chatbot")

# Telegram Bot конфигурация
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8327908006:AAG-aR5WnP34rwIwwk5cHNOgZJK9GDW4DCA")

# Flask конфигурация
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 80))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# Статусы клиентов
CLIENT_STATUSES = {
    "student": "Студент",
    "applicant": "Абитуриент",
    "parent_student": "Родитель студента",
    "parent_applicant": "Родитель абитуриента"
}

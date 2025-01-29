import os
import sqlite3
import datetime
import base64
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    JobQueue
)
# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI()
client.api_key = OPENAI_API_KEY

# Указываем нужный чат
ALLOWED_CHAT_ID =  -1002370287106

# Логирование в БД
def log_interaction(user_id, chat_id, username, request, response):
    conn = sqlite3.connect('bot_stats.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO interactions (user_id, chat_id, username, request, response)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, chat_id, username, request, response))
    conn.commit()
    conn.close()

# Добавим новый обработчик для фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Ограничиваем сам чат
    # if update.effective_chat.id != ALLOWED_CHAT_ID:
    #     return

    try:
        # Получаем фото с наивысшим разрешением
        photo_file = await update.message.photo[-1].get_file()
        
        # Скачиваем фото в формате bytes
        photo_bytes = await photo_file.download_as_bytearray()
        
        # Конвертируем в base64
        base64_image = base64.b64encode(photo_bytes).decode('utf-8')
        
        # Формируем запрос к GPT-4 с обработкой изображений
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "Придумай смешную подпись или шутку для этого изображения. Будь креативным и остроумным."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Опиши фото в шуточной манере, чтобы было смешно"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        joke = response.choices[0].message.content
        
        # Логируем взаимодействие
        log_interaction(
            update.effective_user.id,
            update.effective_chat.id,
            update.effective_user.username,
            "[PHOTO]",
            joke
        )
        
        await update.message.reply_text(f"📸 Шутка от нейросети:\n\n{joke}")

    except Exception as e:
        await update.message.reply_text(f"⚠️ Не удалось обработать фото: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()


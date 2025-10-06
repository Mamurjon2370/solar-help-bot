import os
import logging
from telegram.ext import Application, CommandHandler

# Token ni environment dan olish
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7977578697:AAF312oDVAMtnLMawaA8Y09HSjFyMVsU3WU')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update, context):
    user_name = update.message.from_user.first_name
    await update.message.reply_text(f"🌞 Assalomu alaykum {user_name}! Bot Render da ishlayapti! 🚀")

def main():
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        
        print("🤖 Bot Render da ishga tushdi!")
        app.run_polling()
    except Exception as e:
        print(f"Xato: {e}")
        # Qayta urinish
        import time
        time.sleep(5)
        main()

if __name__ == '__main__':
    main()

import os
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Token ni environment dan olish
BOT_TOKEN = os.environ['BOT_TOKEN']

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update, context):
    await update.message.reply_text("🚀 Bot Render da ishlayapti!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    port = int(os.environ.get('PORT', 5000))
    print(f"🤖 Bot Render da {port} portda ishga tushdi!")
    
    # Webhook o'rniga polling ishlatamiz
    app.run_polling()

if __name__ == '__main__':
    main()

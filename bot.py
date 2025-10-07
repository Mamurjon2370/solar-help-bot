import os
import logging
import json
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

BOT_TOKEN = os.environ.get('BOT_TOKEN', '7977578697:AAF312oDVAMtnLMawaA8Y09HSjFyMVsU3WU')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

user_data = {}

# Reply Keyboard funksiyalari (oldingi kod)
def get_main_keyboard():
    keyboard = [
        ["🔧 Muammolarni hal qilish", "💎 Premium xizmat"],
        ["📞 Yordam", "👑 Admin panel"],
        ["📊 Mening holatim"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_problems_keyboard():
    keyboard = [
        ["⚡ Panel ishlamay qoldi", "📉 Samaradorlik pasaydi"],
        ["💧 Tozalash masalalari", "🔌 Inverter muammosi"],
        ["⬅️ Bosh menyuga qaytish"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_premium_keyboard():
    keyboard = [
        ["💰 Narxlar va imkoniyatlar", "💳 To'lov usullari"],
        ["📸 Chek yuborish", "📊 Mening holatim"],
        ["⬅️ Bosh menyuga qaytish"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name
    
    if user_id not in user_data:
        user_data[user_id] = {
            'free_questions': 3,
            'is_premium': False,
            'user_name': user_name,
            'joined_date': datetime.now().isoformat()
        }
    
    user = user_data[user_id]
    remaining = user['free_questions']
    premium_status = "💎 Premium" if user.get('is_premium') else "🆓 Bepul"
    
    message = (
        f"🌞 Assalomu alaykum {user_name}!\n\n"
        f"📊 Sizning holatingiz: {premium_status}\n"
        f"❓ Bepul savollar qoldi: {remaining}\n\n"
        "Quyidagi tugmalardan birini tanlang:"
    )
    
    await update.message.reply_text(message, reply_markup=get_main_keyboard())

# Qolgan funksiyalar (handle_message, show_problems_menu, va boshqalar)...
# Oldingi kodni saqlang, faqat handle_photo va yangi funksiyalarni almashtiring

# YANGILANGAN handle_photo
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name
    
    await update.message.reply_text(
        f"📨 **Chek qabul qilindi {user_name}!** ✅\n\nAdminlar tekshirilmoqda...",
        reply_markup=get_main_keyboard()
    )
    
    # ADMIN ga RASM va TUGMALAR
    if user_id != "905366606":
        try:
            photo_file = await update.message.photo[-1].get_file()
            
            keyboard = [
                [
                    InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{user_id}"),
                    InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user_id}")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_photo(
                chat_id=905366606,
                photo=photo_file.file_id,
                caption=f"🆕 Yangi to'lov cheki!\n👤 {user_name}\n🆔 {user_id}",
                reply_markup=reply_markup
            )
            
        except Exception as e:
            print(f"Admin ga xabar yuborishda xatolik: {e}")

# YANGI CALLBACK HANDLER
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    admin_id = str(update.effective_user.id)
    
    if admin_id != "905366606":
        await query.edit_message_text("❌ Ruxsat yo'q")
        return
    
    if data.startswith("confirm_"):
        user_id = data.replace("confirm_", "")
        await confirm_payment(query, user_id)
    
    elif data.startswith("reject_"):
        user_id = data.replace("reject_", "")
        await reject_payment(query, user_id)

async def confirm_payment(query, user_id):
    if user_id in user_data:
        user_data[user_id]['is_premium'] = True
        user_data[user_id]['premium_until'] = (datetime.now() + timedelta(days=30)).isoformat()
        
        try:
            await query.bot.send_message(
                chat_id=int(user_id),
                text="🎉 **To'lov tasdiqlandi!** ✅\n\n💎 Premium faollashtirildi!",
                reply_markup=get_main_keyboard()
            )
        except:
            pass
        
        await query.edit_message_text(f"✅ Foydalanuvchi {user_id} premium qilindi!")
    else:
        await query.edit_message_text("❌ Foydalanuvchi topilmadi")

async def reject_payment(query, user_id):
    if user_id in user_data:
        try:
            await query.bot.send_message(
                chat_id=int(user_id),
                text="❌ **To'lov tasdiqlanmadi**\n\nYangi chek yuboring.",
                reply_markup=get_main_keyboard()
            )
        except:
            pass
        
        await query.edit_message_text(f"❌ Foydalanuvchi {user_id} to'lovi rad etildi!")
    else:
        await query.edit_message_text("❌ Foydalanuvchi topilmadi")

def main():
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
        application.add_handler(CallbackQueryHandler(handle_callback))  # ✅ YANGI
        
        print("✅ Bot yangi funksiyalar bilan ishga tushdi!")
        application.run_polling()
        
    except Exception as e:
        print(f"❌ Xato: {e}")
        import time
        time.sleep(10)
        main()

if __name__ == '__main__':
    main()

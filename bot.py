import os
import logging
import json
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

DATA_FILE = "user_data.json"

# --- Ma'lumotlarni saqlash va yuklash funksiyalari ---
def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_user_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

user_data = load_user_data()

# --- Tugmalar ---
def get_main_keyboard():
    keyboard = [
        ["🔧 Muammolarni hal qilish", "💎 Premium xizmat"],
        ["📞 Yordam", "👑 Admin panel"],
        ["📊 Mening holatim"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_premium_keyboard():
    keyboard = [
        ["💰 Narxlar va imkoniyatlar", "💳 To'lov usullari"],
        ["📸 Chek yuborish", "📊 Mening holatim"],
        ["⬅️ Bosh menyuga qaytish"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- START komandasi ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name or "Foydalanuvchi"

    if user_id not in user_data:
        user_data[user_id] = {
            "free_questions": 3,
            "is_premium": False,
            "user_name": user_name,
            "joined_date": datetime.now().isoformat()
        }
        save_user_data()

    user = user_data[user_id]
    remaining = user.get("free_questions", 0)
    premium_status = "💎 Premium" if user.get("is_premium") else "🆓 Bepul"

    text = (
        f"🌞 Assalomu alaykum, {user_name}!\n\n"
        f"📊 Holatingiz: {premium_status}\n"
        f"❓ Bepul savollar: {remaining}\n\n"
        "Quyidagi menyudan keraklisini tanlang:"
    )
    await update.message.reply_text(text, reply_markup=get_main_keyboard())

# --- FOTO QABUL QILISH ---
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name

    await update.message.reply_text(
        f"📨 Rahmat {user_name}! Chek qabul qilindi ✅\nAdminlar tekshirib chiqadi.",
        reply_markup=get_main_keyboard()
    )

    if user_id != "905366606":  # Admin o‘zi chek yuborsa, qaytarma bo‘lmaydi
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
                chat_id=905366606,  # Admin ID
                photo=photo_file.file_id,
                caption=f"🆕 Yangi to'lov cheki!\n👤 {user_name}\n🆔 {user_id}",
                reply_markup=reply_markup
            )

        except Exception as e:
            logging.error(f"Admin xabar yuborishda xato: {e}")

# --- CALLBACKLAR ---
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    admin_id = str(update.effective_user.id)

    if admin_id != "905366606":
        await query.edit_message_text("❌ Sizda bu amalni bajarish huquqi yo‘q.")
        return

    if data.startswith("confirm_"):
        user_id = data.replace("confirm_", "")
        await confirm_payment(query, user_id)
    elif data.startswith("reject_"):
        user_id = data.replace("reject_", "")
        await reject_payment(query, user_id)

async def confirm_payment(query, user_id):
    if user_id in user_data:
        user_data[user_id]["is_premium"] = True
        user_data[user_id]["premium_until"] = (datetime.now() + timedelta(days=30)).isoformat()
        save_user_data()

        await query.bot.send_message(
            chat_id=int(user_id),
            text="🎉 To'lov tasdiqlandi! Siz endi 💎 *Premium* foydalanuvchisiz!",
            reply_markup=get_main_keyboard()
        )
        await query.edit_message_text(f"✅ {user_id} Premium holatga o‘tkazildi!")
    else:
        await query.edit_message_text("❌ Foydalanuvchi topilmadi!")

async def reject_payment(query, user_id):
    if user_id in user_data:
        await query.bot.send_message(
            chat_id=int(user_id),
            text="❌ To‘lov rad etildi.\nIltimos, to‘lov chekingizni qayta yuboring.",
            reply_markup=get_main_keyboard()
        )
        await query.edit_message_text(f"🚫 {user_id} to‘lovi rad etildi!")
    else:
        await query.edit_message_text("❌ Foydalanuvchi topilmadi!")

# --- Xabarlarni ushlash (oddiy matn) ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Premium" in text:
        await update.message.reply_text("💎 Premium xizmat haqida ma’lumot...", reply_markup=get_premium_keyboard())
    else:
        await update.message.reply_text("🪄 Tugmalardan birini tanlang.", reply_markup=get_main_keyboard())

# --- Asosiy funksiyani ishga tushirish ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("✅ Bot ishga tushdi va Premium tizim tayyor!")
    app.run_polling()

if __name__ == "__main__":
    main()

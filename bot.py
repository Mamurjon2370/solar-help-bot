import os
import logging
import json
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext

# Token ni environment dan olish
BOT_TOKEN = os.environ.get('BOT_TOKEN', '7977578697:AAF312oDVAMtnLMawaA8Y09HSjFyMVsU3WU')

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Foydalanuvchi ma'lumotlari
user_data = {}

# Reply Keyboard
def get_main_keyboard():
    keyboard = [
        ["🔧 Muammolarni hal qilish", "💎 Premium xizmat"],
        ["📞 Yordam", "👑 Admin panel"],
        ["📊 Mening holatim"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="Quyidagilardan birini tanlang...")

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

# Start command
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
        "Quyosh panellari muammolari bo'yicha professional yordam!\n\n"
        "Quyidagi tugmalardan birini tanlang:"
    )
    
    await update.message.reply_text(message, reply_markup=get_main_keyboard())

# Handle messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    text = update.message.text
    user_name = update.effective_user.first_name
    
    # Asosiy menyu
    if text == "🔧 Muammolarni hal qilish":
        await show_problems_menu(update)
    
    elif text == "💎 Premium xizmat":
        await show_premium_menu(update)
    
    elif text == "📞 Yordam":
        await show_help(update)
    
    elif text == "👑 Admin panel":
        await show_admin_panel(update, user_id)
    
    elif text == "📊 Mening holatim":
        await show_user_status(update, user_id)
    
    # Muammolar menyusi
    elif text == "⚡ Panel ishlamay qoldi":
        await handle_problem(update, user_id, "ishlamay", user_name)
    
    elif text == "📉 Samaradorlik pasaydi":
        await handle_problem(update, user_id, "samaradorlik", user_name)
    
    elif text == "💧 Tozalash masalalari":
        await handle_problem(update, user_id, "tozalash", user_name)
    
    elif text == "🔌 Inverter muammosi":
        await handle_problem(update, user_id, "inverter", user_name)
    
    # Premium menyusi
    elif text == "💰 Narxlar va imkoniyatlar":
        await show_premium_info(update)
    
    elif text == "💳 To'lov usullari":
        await show_payment_methods(update)
    
    elif text == "📸 Chek yuborish":
        await request_receipt(update)
    
    # Orqaga qaytish
    elif text == "⬅️ Bosh menyuga qaytish":
        await start(update, context)
    
    else:
        await update.message.reply_text(
            "Iltimos, quyidagi tugmalardan foydalaning:",
            reply_markup=get_main_keyboard()
        )

async def show_problems_menu(update: Update):
    message = "🔧 **Quyosh panellari muammolari**\n\nQuyidagi muammolardan birini tanlang:"
    await update.message.reply_text(message, reply_markup=get_problems_keyboard())

async def show_premium_menu(update: Update):
    message = "💎 **Premium Xizmat**\n\nPremium obuna bilan cheksiz yordam oling!"
    await update.message.reply_text(message, reply_markup=get_premium_keyboard())

async def handle_problem(update: Update, user_id: str, problem_type: str, user_name: str):
    user = user_data.get(user_id, {})
    
    # Tekin savollar soni tugagan bo'lsa
    if user.get('free_questions', 3) <= 0 and not user.get('is_premium', False):
        message = (
            "❌ **Bepul savollar tugadi!**\n\n"
            "💎 **Premium xizmatga o'ting:**\n"
            "✅ Cheksiz savollar\n" 
            "✅ Batafsil tahlil\n"
            "✅ Mutaxassis yordami\n\n"
            "💰 **Narx: 10,000 so'm / oy**"
        )
        await update.message.reply_text(message, reply_markup=get_premium_keyboard())
        return
    
    # Savol hisobini kamaytirish
    if not user.get('is_premium', False):
        user_data[user_id]['free_questions'] = user.get('free_questions', 3) - 1
    
    remaining = user_data[user_id].get('free_questions', 3) if not user.get('is_premium', False) else "♾️ Cheksiz"
    
    solutions = {
        "ishlamay": (
            "🔧 **Panel ishlamay qoldi:**\n\n"
            "1. 🔌 Asosiy elektr ta'minotini tekshiring\n"
            "2. 🔗 Kabel ulanishlarini qayta tekshiring\n"
            "3. 💡 Inverter indikator lampochkalarini ko'rib chiqing\n"
            "4. ⚡ Sigortalarni tekshiring\n\n"
            f"📊 Savollar qoldi: {remaining}"
        ),
        "samaradorlik": (
            "📊 **Samaradorlik pasaydi:**\n\n"
            "1. 💧 Panellarni tozalang\n"
            "2. 🌳 Soyaning tushishini tekshiring\n"
            "3. ☁️ Ob-havo sharoitini hisobga oling\n"
            "4. 📅 Panel yoshi va eskirish darajasi\n\n"
            f"📊 Savollar qoldi: {remaining}"
        ),
        "tozalash": (
            "💧 **Tozalash masalalari:**\n\n"
            "1. 🧴 Maxsus quyosh paneli tozalash vositasidan foydalaning\n"
            "2. 💦 Sifatli suv ishlating\n"
            "3. 🌅 Ertalab yoki kechqurun tozalang\n"
            "4. 🚫 Abraziv materiallardan foydalanmang\n\n"
            f"📊 Savollar qoldi: {remaining}"
        ),
        "inverter": (
            "⚡ **Inverter muammolari:**\n\n"
            "1. 📟 Inverter ekranidagi xabarlarni o'qing\n"
            "2. 💨 Havo o'tkazuvchanligini tekshiring\n"
            "3. 👨‍💼 Mutaxassis bilan bog'laning\n"
            "4. 🔢 Model va seriya raqamini yozib oling\n\n"
            f"📊 Savollar qoldi: {remaining}"
        )
    }
    
    solution = solutions.get(problem_type, "❌ Muammo aniqlanmadi")
    await update.message.reply_text(solution, reply_markup=get_problems_keyboard())

async def show_premium_info(update: Update):
    message = (
        "💎 **Premium Xizmat Narxlari**\n\n"
        "✅ **Cheksiz savollar** - chegarasiz maslahat\n"
        "✅ **Batafsil tahlil** - chuqur diagnostika\n"
        "✅ **Mutaxassis bilan bog'lanish** - shaxsiy yordam\n"
        "✅ **Video ko'rsatmalar** - vizual qo'llanma\n\n"
        "💰 **Narx: 10,000 so'm / 30 kun**\n\n"
        "To'lov usullarini ko'rish uchun 'To'lov usullari' tugmasini bosing"
    )
    await update.message.reply_text(message, reply_markup=get_premium_keyboard())

async def show_payment_methods(update: Update):
    message = (
        "💳 **To'lov Usullari**\n\n"
        "🔹 **Click:** `8600 1234 5678 9012`\n"
        "🔹 **Payme:** @solar_premium_bot\n"
        "🔹 **Uzumbank:** `9860 1234 5678 9012`\n\n"
        "📸 **To'lov qilgach:**\n"
        "1. To'lov chekining skreenhotini yuboring\n"
        "2. 'Chek yuborish' tugmasini bosing\n"
        "3. Rasmni yuboring\n"
        "4. Adminlar tekshiradi (24 soat ichida)"
    )
    await update.message.reply_text(message, reply_markup=get_premium_keyboard())

async def request_receipt(update: Update):
    message = "📸 **Chek yuborish**\n\nIltimos, to'lov cheki rasmini yuboring. Adminlar 24 soat ichida tekshiradi."
    await update.message.reply_text(message)

async def show_help(update: Update):
    message = (
        "📞 **Yordam va Qo'llab-quvvatlash**\n\n"
        "💬 Telegram: @solar_support\n"
        "📱 Telefon: +998 90 123 45 67\n"
        "🕐 Ish vaqti: 09:00 - 18:00\n\n"
        "Agar muammo bo'lsa, biz bilan bog'laning!"
    )
    await update.message.reply_text(message, reply_markup=get_main_keyboard())

async def show_admin_panel(update: Update, user_id: str):
    # Faqat adminlar uchun (sizning ID'ingiz 905366606)
    if user_id != "905366606":
        await update.message.reply_text("❌ Sizda admin huquqlari yo'q", reply_markup=get_main_keyboard())
        return
    
    premium_users = len([uid for uid, data in user_data.items() if data.get('is_premium')])
    total_users = len(user_data)
    
    message = (
        "👑 **Admin Panel**\n\n"
        f"💎 Premium foydalanuvchilar: {premium_users}\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"📈 Daromad: {premium_users * 10000} so'm\n\n"
        "Bot to'g'ri ishlayapti! 🚀"
    )
    await update.message.reply_text(message, reply_markup=get_main_keyboard())

async def show_user_status(update: Update, user_id: str):
    user = user_data.get(user_id, {})
    
    if user.get('is_premium'):
        message = "💎 **Siz Premium foydalanuvchisiz!**\n\nCheksiz savollar va barcha imkoniyatlar faol!"
    else:
        remaining = user.get('free_questions', 3)
        message = f"🆓 **Siz bepul foydalanuvchisiz**\n\nBepul savollar qoldi: {remaining}"
    
    await update.message.reply_text(message, reply_markup=get_main_keyboard())

# Rasm qabul qilish (chek uchun)
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name
    
    await update.message.reply_text(
        f"📨 **Chek qabul qilindi {user_name}!** ✅\n\n"
        "Adminlar tomonidan tekshirilmoqda...\n"
        "24 soat ichida javob beramiz!",
        reply_markup=get_main_keyboard()
    )
    
    # Admin ga xabar (sizga)
    if user_id != "905366606":  # O'zingizga xabar yubormaslik uchun
        try:
            await context.bot.send_message(
                chat_id=905366606,  # Sizning ID'ingiz
                text=f"🆕 Yangi chek!\n👤 {user_name}\n🆔 {user_id}"
            )
        except:
            pass

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("🤖 Mukammal bot Render da ishga tushdi! 🚀")
    application.run_polling()

if __name__ == '__main__':
    main()

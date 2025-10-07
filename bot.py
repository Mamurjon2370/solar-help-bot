from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import logging
import os
from datetime import datetime, timedelta
import json

# Logging ni yoqish
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

BOT_TOKEN = "7977578697:AAF312oDVAMtnLMawaA8Y09HSjFyMVsU3WU"
ADMINS = [905366606]

user_data = {}
os.makedirs("receipts", exist_ok=True)

# Ma'lumotlarni saqlash
def save_data():
    try:
        with open("user_data.json", "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Saqlash xatosi: {e}")

def load_data():
    global user_data
    try:
        with open("user_data.json", "r", encoding="utf-8") as f:
            user_data = json.load(f)
    except:
        user_data = {}

# REPLY KEYBOARD (PASTKI KLAVIATURA)
def get_main_reply_keyboard():
    keyboard = [
        ["🔧 Muammolarni hal qilish", "💎 Premium xizmat"],
        ["📞 Yordam", "👑 Admin panel"],
        ["📊 Mening holatim"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, input_field_placeholder="Quyidagilardan birini tanlang...")

def get_problems_reply_keyboard():
    keyboard = [
        ["⚡ Panel ishlamay qoldi", "📉 Samaradorlik pasaydi"],
        ["💧 Tozalash masalalari", "🔌 Inverter muammosi"],
        ["⬅️ Bosh menyuga qaytish"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_premium_reply_keyboard():
    keyboard = [
        ["💰 Narxlar va imkoniyatlar", "💳 To'lov usullari"],
        ["📸 Chek yuborish", "📊 Mening holatim"],
        ["⬅️ Bosh menyuga qaytish"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_admin_reply_keyboard():
    keyboard = [
        ["⏳ Kutayotgan to'lovlar", "💎 Premium foydalanuvchilar"],
        ["📊 Statistika", "📢 Xabar yuborish"],
        ["⬅️ Bosh menyuga qaytish"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_support_reply_keyboard():
    keyboard = [
        ["📞 Aloqa", "❓ Ko'p so'raladigan savollar"],
        ["ℹ️ Bot haqida", "⬅️ Bosh menyuga qaytish"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# INLINE TUGMALAR (Admin tasdiqlash uchun)
def get_approval_inline_buttons(user_id):
    keyboard = [
        [
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{user_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"reject_{user_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name
    
    if user_id not in user_data:
        user_data[user_id] = {
            'free_questions': 3,
            'is_premium': False,
            'user_name': user_name,
            'joined_date': datetime.now().isoformat()
        }
        save_data()
    
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
    
    await update.message.reply_text(
        message, 
        reply_markup=get_main_reply_keyboard()
    )

# Text message handler - reply keyboard tugmalarini boshqarish
async def handle_text_message(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    text = update.message.text
    
    # Asosiy menyu
    if text == "🔧 Muammolarni hal qilish":
        await show_problems_menu(update)
    
    elif text == "💎 Premium xizmat":
        await show_premium_menu(update)
    
    elif text == "📞 Yordam":
        await show_support_menu(update)
    
    elif text == "👑 Admin panel":
        await show_admin_menu(update, user_id)
    
    elif text == "📊 Mening holatim":
        await show_user_status(update, user_id)
    
    # Muammolar menyusi
    elif text == "⚡ Panel ishlamay qoldi":
        await handle_problem(update, user_id, "ishlamay")
    
    elif text == "📉 Samaradorlik pasaydi":
        await handle_problem(update, user_id, "samaradorlik")
    
    elif text == "💧 Tozalash masalalari":
        await handle_problem(update, user_id, "tozalash")
    
    elif text == "🔌 Inverter muammosi":
        await handle_problem(update, user_id, "inverter")
    
    # Premium menyusi
    elif text == "💰 Narxlar va imkoniyatlar":
        await show_premium_info(update)
    
    elif text == "💳 To'lov usullari":
        await show_payment_methods(update)
    
    elif text == "📸 Chek yuborish":
        await request_receipt(update)
    
    # Yordam menyusi
    elif text == "📞 Aloqa":
        await show_contact_info(update)
    
    elif text == "❓ Ko'p so'raladigan savollar":
        await show_faq(update)
    
    elif text == "ℹ️ Bot haqida":
        await show_about_bot(update)
    
    # Admin menyusi
    elif text == "⏳ Kutayotgan to'lovlar":
        await show_pending_payments(update, user_id)
    
    elif text == "💎 Premium foydalanuvchilar":
        await show_premium_users(update, user_id)
    
    elif text == "📊 Statistika":
        await show_stats(update, user_id)
    
    elif text == "📢 Xabar yuborish":
        await request_broadcast(update, user_id)
    
    # Orqaga qaytish
    elif text == "⬅️ Bosh menyuga qaytish":
        await start(update, context)
    
    # Boshqa xabarlar
    else:
        await update.message.reply_text(
            "Iltimos, quyidagi tugmalardan foydalaning:",
            reply_markup=get_main_reply_keyboard()
        )

async def show_problems_menu(update: Update):
    message = "🔧 **Quyosh panellari muammolari**\n\nQuyidagi muammolardan birini tanlang:"
    await update.message.reply_text(message, reply_markup=get_problems_reply_keyboard())

async def show_premium_menu(update: Update):
    message = "💎 **Premium Xizmat**\n\nPremium obuna bilan cheksiz yordam oling!"
    await update.message.reply_text(message, reply_markup=get_premium_reply_keyboard())

async def show_support_menu(update: Update):
    message = "📞 **Yordam va Qo'llab-quvvatlash**\n\nKerakli bo'limni tanlang:"
    await update.message.reply_text(message, reply_markup=get_support_reply_keyboard())

async def show_admin_menu(update: Update, user_id: str):
    if int(user_id) not in ADMINS:
        await update.message.reply_text(
            "❌ Sizda admin huquqlari yo'q",
            reply_markup=get_main_reply_keyboard()
        )
        return
    
    message = "👑 **Admin Panel**\n\nBotni boshqarish uchun kerakli bo'limni tanlang:"
    await update.message.reply_text(message, reply_markup=get_admin_reply_keyboard())

async def handle_problem(update: Update, user_id: str, problem_type: str):
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
        await update.message.reply_text(message, reply_markup=get_premium_reply_keyboard())
        return
    
    # Savol hisobini kamaytirish
    if not user.get('is_premium', False):
        user_data[user_id]['free_questions'] = user.get('free_questions', 3) - 1
        save_data()
    
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
    await update.message.reply_text(solution, reply_markup=get_problems_reply_keyboard())

async def show_user_status(update: Update, user_id: str):
    user = user_data.get(user_id, {})
    
    if user.get('status') == 'pending':
        message = "⏳ **Sizning to'lovingiz tekshirilmoqda**\n\nAdminlar tomonidan tekshirilmoqda..."
    elif user.get('is_premium'):
        message = "💎 **Siz Premium foydalanuvchisiz!**\n\nCheksiz savollar va barcha imkoniyatlar faol!"
    else:
        remaining = user.get('free_questions', 3)
        message = f"🆓 **Siz bepul foydalanuvchisiz**\n\nBepul savollar qoldi: {remaining}"
    
    await update.message.reply_text(message, reply_markup=get_main_reply_keyboard())

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
    await update.message.reply_text(message, reply_markup=get_premium_reply_keyboard())

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
    await update.message.reply_text(message, reply_markup=get_premium_reply_keyboard())

async def request_receipt(update: Update):
    message = "📸 **Chek yuborish**\n\nIltimos, to'lov cheki rasmini yuboring:"
    await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())

async def show_contact_info(update: Update):
    message = (
        "📞 **Aloqa Ma'lumotlari**\n\n"
        "💬 Telegram: @solar_support\n"
        "📱 Telefon: +998 90 123 45 67\n"
        "🕐 Ish vaqti: 09:00 - 18:00\n"
        "📧 Email: support@solarhelp.uz\n\n"
        "Biz sizga 24 soat ichida javob beramiz!"
    )
    await update.message.reply_text(message, reply_markup=get_support_reply_keyboard())

async def show_faq(update: Update):
    message = (
        "❓ **Ko'p So'raladigan Savollar**\n\n"
        "❓ **Necha marta bepul maslahat olaman?**\n"
        "✅ 3 marta bepul, keyin premium kerak\n\n"
        "❓ **Premium qancha turadi?**\n"
        "✅ 10,000 so'm / 30 kun\n\n"
        "❓ **To'lovni qanday tasdiqlayman?**\n"
        "✅ Chek rasmni yuboring, admin tekshiradi\n\n"
        "❓ **Qancha kunda javob olaman?**\n"
        "✅ To'lov 24 soat, maslahat darhol"
    )
    await update.message.reply_text(message, reply_markup=get_support_reply_keyboard())

async def show_about_bot(update: Update):
    message = (
        "ℹ️ **Bot Haqida**\n\n"
        "🤖 **Solar Help Bot**\n"
        "Quyosh panellari muammolari bo'yicha\n"
        "professional yordam platformasi\n\n"
        "⚡ Tez va aniq diagnostika\n"
        "💎 Premium mutaxassis yordami\n"
        "🔧 Barcha turdagi panellar uchun\n"
        "🕐 24/7 qo'llab-quvvatlash\n\n"
        "✨ Ishlab chiqaruvchi: @Mamurjon_Saidov"
    )
    await update.message.reply_text(message, reply_markup=get_support_reply_keyboard())

# Admin funksiyalari
async def show_pending_payments(update: Update, user_id: str):
    if int(user_id) not in ADMINS:
        return
    
    pending_payments = [uid for uid, data in user_data.items() if data.get('status') == 'pending']
    
    if not pending_payments:
        await update.message.reply_text("✅ Kutayotgan to'lovlar yo'q", reply_markup=get_admin_reply_keyboard())
        return
    
    message = "⏳ **Kutayotgan To'lovlar:**\n\n"
    for user_id in pending_payments[:5]:
        user = user_data[user_id]
        message += f"👤 {user['user_name']} (ID: {user_id})\n"
    
    message += "\nTo'lovlarni tasdiqlash uchun inline tugmalardan foydalaning"
    await update.message.reply_text(message, reply_markup=get_admin_reply_keyboard())

async def show_premium_users(update: Update, user_id: str):
    if int(user_id) not in ADMINS:
        return
    
    premium_users = [uid for uid, data in user_data.items() if data.get('is_premium')]
    
    if not premium_users:
        await update.message.reply_text("💎 Premium foydalanuvchilar yo'q", reply_markup=get_admin_reply_keyboard())
        return
    
    message = "💎 **Premium Foydalanuvchilar:**\n\n"
    for user_id in premium_users[:5]:
        user = user_data[user_id]
        message += f"👤 {user['user_name']} (ID: {user_id})\n"
    
    await update.message.reply_text(message, reply_markup=get_admin_reply_keyboard())

async def show_stats(update: Update, user_id: str):
    if int(user_id) not in ADMINS:
        return
    
    total_users = len(user_data)
    premium_users = len([uid for uid, data in user_data.items() if data.get('is_premium')])
    pending_payments = len([uid for uid, data in user_data.items() if data.get('status') == 'pending'])
    
    message = (
        "📊 **Bot Statistikasi:**\n\n"
        f"👥 Jami foydalanuvchilar: {total_users}\n"
        f"💎 Premium foydalanuvchilar: {premium_users}\n"
        f"⏳ Kutayotgan to'lovlar: {pending_payments}\n"
        f"📈 Premium daromad: {premium_users * 10000} so'm"
    )
    
    await update.message.reply_text(message, reply_markup=get_admin_reply_keyboard())

async def request_broadcast(update: Update, user_id: str):
    if int(user_id) not in ADMINS:
        return
    
    context.user_data['awaiting_broadcast'] = True
    await update.message.reply_text(
        "📢 **Xabar yuborish**\n\nBarcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring:",
        reply_markup=ReplyKeyboardRemove()
    )

# Rasm qabul qilish
async def handle_receipt(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    user_name = update.effective_user.first_name
    
    if update.message.photo:
        # Rasmni saqlash
        photo_file = await update.message.photo[-1].get_file()
        file_name = f"receipts/{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        await photo_file.download_to_drive(file_name)
        
        # Foydalanuvchi ma'lumotlarini yangilash
        user_data[user_id] = {
            'receipt_sent': True,
            'receipt_file': file_name,
            'receipt_time': datetime.now().isoformat(),
            'status': 'pending',
            'user_name': user_name,
            'free_questions': user_data.get(user_id, {}).get('free_questions', 3),
            'is_premium': False
        }
        save_data()
        
        # Adminlarga xabar berish
        for admin_id in ADMINS:
            try:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=photo_file.file_id,
                    caption=f"🆕 Yangi to'lov cheki!\n👤 {user_name}\n🆔 {user_id}",
                    reply_markup=get_approval_inline_buttons(user_id)
                )
            except Exception as e:
                print(f"Adminga xabar yuborishda xatolik: {e}")
        
        await update.message.reply_text(
            "📨 **Chek qabul qilindi!** ✅\n\nAdminlar tekshirilmoqda...",
            reply_markup=get_main_reply_keyboard()
        )
    else:
        await update.message.reply_text(
            "❌ Iltimos, chek rasmini yuboring!",
            reply_markup=get_premium_reply_keyboard()
        )

# Inline callback handler (faqat admin tasdiqlash uchun)
async def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    
    user_id = str(update.effective_user.id)
    data = query.data
    
    if data.startswith("confirm_") and int(user_id) in ADMINS:
        target_user_id = data.replace("confirm_", "")
        await confirm_payment_admin(query, target_user_id)
    
    elif data.startswith("reject_") and int(user_id) in ADMINS:
        target_user_id = data.replace("reject_", "")
        await reject_payment_admin(query, target_user_id)

async def confirm_payment_admin(query, target_user_id):
    if target_user_id in user_data:
        user_data[target_user_id]['is_premium'] = True
        user_data[target_user_id]['status'] = 'confirmed'
        user_data[target_user_id]['premium_until'] = (datetime.now() + timedelta(days=30)).isoformat()
        save_data()
        
        # Foydalanuvchiga xabar
        try:
            await query.bot.send_message(
                chat_id=int(target_user_id),
                text="🎉 **Tabriklaymiz! To'lov tasdiqlandi!**\n\nPremium xizmat faollashtirildi! Endi cheksiz savollar berishingiz mumkin.",
                reply_markup=get_main_reply_keyboard()
            )
        except:
            pass
        
        await query.edit_message_text(
            f"✅ Foydalanuvchi {target_user_id} premium qilindi!"
        )
    else:
        await query.edit_message_text("❌ Foydalanuvchi topilmadi")

async def reject_payment_admin(query, target_user_id):
    if target_user_id in user_data:
        user_data[target_user_id]['status'] = 'rejected'
        save_data()
        
        await query.edit_message_text(
            f"❌ Foydalanuvchi {target_user_id} to'lovi rad etildi!"
        )
    else:
        await query.edit_message_text("❌ Foydalanuvchi topilmadi")

def main():
    print("🤖 Bot ishga tushmoqda...")
    print("⌨️ Reply Keyboard bilan interfeys faollashtirildi!")
    
    load_data()
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Handlerlarni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(MessageHandler(filters.PHOTO, handle_receipt))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    print("✅ Bot ishga tushdi! Reply Keyboard bilan ishlaydi")
    print("🔗 Bot manzili: t.me/SSS_SolarHelp_bot")
    print("⏹️ To'xtatish uchun: Ctrl+C")
    
    application.run_polling()

if __name__ == '__main__':
    main()

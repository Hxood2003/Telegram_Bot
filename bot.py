from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# 🔑 التوكن الخاص بالبوت
TOKEN = '7998479930:AAFcADgQdzsBf7PAUm0o5GLfXYpQje5XIaU'

# 👑 معرفات الإدمن (ID الأرقام)
ADMINS = [5459308678, 7908967919, 1801986367]

# 🟢 أمر /start
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 أهلاً بك في بوت التواصل مع الإدارة.\n"
        "✉️ أرسل رسالتك هنا، وسيتم إرسالها للإدارة مباشرة."
    )

# ✉️ استقبال رسائل الأعضاء وإرسالها للإدمنز
def handle_user_message(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    username = f"@{user.username}" if user.username else "بدون معرف"
    name = user.first_name

    # محتوى الرسالة
    caption = f"""📩 رسالة جديدة:

👤 الاسم: {name} ({username})
🆔 ID: {user_id}
"""

    for admin_id in ADMINS:
        try:
            sent_message = None

            # التعامل مع أنواع الوسائط
            if update.message.text:
                sent_message = context.bot.send_message(
                    chat_id=admin_id,
                    text=caption + f"\n💬 {update.message.text}"
                )
            elif update.message.photo:
                sent_message = context.bot.send_photo(
                    chat_id=admin_id,
                    photo=update.message.photo[-1].file_id,
                    caption=caption
                )
            elif update.message.document:
                sent_message = context.bot.send_document(
                    chat_id=admin_id,
                    document=update.message.document.file_id,
                    caption=caption
                )
            elif update.message.audio:
                sent_message = context.bot.send_audio(
                    chat_id=admin_id,
                    audio=update.message.audio.file_id,
                    caption=caption
                )
            elif update.message.voice:
                sent_message = context.bot.send_voice(
                    chat_id=admin_id,
                    voice=update.message.voice.file_id,
                    caption=caption
                )
            elif update.message.video:
                sent_message = context.bot.send_video(
                    chat_id=admin_id,
                    video=update.message.video.file_id,
                    caption=caption
                )
            elif update.message.sticker:
                sent_message = context.bot.send_sticker(
                    chat_id=admin_id,
                    sticker=update.message.sticker.file_id
                )

            # إضافة رسالة للرد على العضو
            if sent_message:
                sent_message.reply_text(f"🔁 للرد على العضو اضغط رد على هذه الرسالة.\n🆔 ID: {user_id}")

        except Exception as e:
            print(f"❌ خطأ عند إرسال الرسالة للإدمن {admin_id}: {e}")

    # رسالة تأكيد للعضو
    update.message.reply_text("✅ تم إرسال رسالتك للإدارة.\n📬 سيتم الرد عليك بأقرب وقت.")

# 🔁 استقبال رد الإدمن وإرساله للعضو
def handle_admin_reply(update: Update, context: CallbackContext):
    reply_to = update.message.reply_to_message

    if not reply_to or not reply_to.text:
        return

    # استخراج ID المستخدم من الرسالة الأصلية
    lines = reply_to.text.splitlines()
    user_id_line = next((line for line in lines if line.startswith("🆔 ID: ")), None)

    if not user_id_line:
        update.message.reply_text("❌ لم يتم العثور على رقم ID المستخدم للرد عليه.")
        return

    try:
        user_id = int(user_id_line.replace("🆔 ID: ", "").strip())
    except:
        update.message.reply_text("❌ رقم ID غير صالح.")
        return

    try:
        if update.message.text:
            context.bot.send_message(chat_id=user_id, text=f"💌 رسالة من الإدارة:\n{update.message.text}")
        elif update.message.photo:
            context.bot.send_photo(chat_id=user_id, photo=update.message.photo[-1].file_id)
        elif update.message.document:
            context.bot.send_document(chat_id=user_id, document=update.message.document.file_id)
        elif update.message.audio:
            context.bot.send_audio(chat_id=user_id, audio=update.message.audio.file_id)
        elif update.message.voice:
            context.bot.send_voice(chat_id=user_id, voice=update.message.voice.file_id)
        elif update.message.video:
            context.bot.send_video(chat_id=user_id, video=update.message.video.file_id)
        elif update.message.sticker:
            context.bot.send_sticker(chat_id=user_id, sticker=update.message.sticker.file_id)

        update.message.reply_text("✅ تم إرسال الرد للعضو.")

    except Exception as e:
        print(f"❌ فشل إرسال الرد إلى {user_id}: {e}")
        update.message.reply_text("❌ فشل إرسال الرسالة للعضو.")

# 🚀 تشغيل البوت
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # أوامر
    dp.add_handler(CommandHandler("start", start))

    # استقبال الرسائل من الأعضاء
    dp.add_handler(MessageHandler(Filters.private & ~Filters.command & ~Filters.reply, handle_user_message))

    # استقبال الردود من الإدمن
    dp.add_handler(MessageHandler(Filters.private & Filters.reply, handle_admin_reply))

    # تشغيل البوت
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

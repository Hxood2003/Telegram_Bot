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
                sent_message.reply_text(f"�� للرد على العضو اضغط رد على هذه الرسالة.\n🆔 ID: {user_id}")

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

# =========================
# 💾 إدارة المبيعات والمنتجات (SQLite)
# =========================
import sqlite3
from datetime import datetime, date
from typing import List, Tuple

DB_PATH = 'sales.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            price REAL NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            product_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            line_total REAL NOT NULL,
            FOREIGN KEY(sale_id) REFERENCES sales(id),
            FOREIGN KEY(product_id) REFERENCES products(id)
        )
        """
    )
    conn.commit()
    conn.close()

def is_admin(update: Update) -> bool:
    user = update.effective_user
    return user and user.id in ADMINS

def parse_float(value: str):
    try:
        return float(value)
    except Exception:
        return None

def parse_int(value: str):
    try:
        return int(value)
    except Exception:
        return None

# 🆘 مساعدة
def help_command(update: Update, context: CallbackContext):
    text = (
        "ℹ️ أوامر البوت:\n\n"
        "— للأعضاء: \n"
        "  /start — رسالة ترحيبية\n\n"
        "— للإدمن: \n"
        "  /add_product <الاسم> <السعر> <المخزون> — إضافة منتج\n"
        "  /list_products — عرض المنتجات\n"
        "  /set_price <id> <السعر> — تعديل السعر\n"
        "  /set_stock <id> <الكمية> — تعديل المخزون\n"
        "  /sale <id> <الكمية> — تسجيل بيع عنصر واحد\n"
        "  /sale <id1>:<q1>,<id2>:<q2> — تسجيل بيع متعدد العناصر\n"
        "  /today_sales — تقرير مبيعات اليوم\n"
        "  /report <YYYY-MM-DD> <YYYY-MM-DD> — تقرير فترة\n"
    )
    update.message.reply_text(text)

# 🧱 أوامر المنتجات (Admins)
def add_product(update: Update, context: CallbackContext):
    if not is_admin(update):
        update.message.reply_text("❌ هذا الأمر للإدمن فقط.")
        return
    args = context.args
    if len(args) < 3:
        update.message.reply_text("⚠️ الاستخدام: /add_product <الاسم> <السعر> <المخزون>")
        return
    name = " ".join(args[:-2])
    price = parse_float(args[-2])
    stock = parse_int(args[-1])
    if price is None or stock is None or stock < 0 or price < 0:
        update.message.reply_text("❌ قيم غير صحيحة للسعر/المخزون.")
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO products(name, price, stock, created_at) VALUES (?, ?, ?, ?)",
            (name, price, stock, datetime.utcnow().isoformat())
        )
        conn.commit()
        product_id = cur.lastrowid
        conn.close()
        update.message.reply_text(f"✅ تمت إضافة المنتج #{product_id}: {name} — السعر {price}, المخزون {stock}")
    except sqlite3.IntegrityError:
        update.message.reply_text("❌ اسم المنتج موجود مسبقًا.")
    except Exception as e:
        print(e)
        update.message.reply_text("❌ فشل إضافة المنتج.")

def list_products(update: Update, context: CallbackContext):
    if not is_admin(update):
        update.message.reply_text("❌ هذا الأمر للإدمن فقط.")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, name, price, stock FROM products ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    if not rows:
        update.message.reply_text("📦 لا توجد منتجات.")
        return
    lines = ["📦 قائمة المنتجات:"]
    for pid, name, price, stock in rows:
        lines.append(f"#{pid} — {name} | 💵 {price} | 🗳️ {stock}")
    update.message.reply_text("\n".join(lines))

def set_price(update: Update, context: CallbackContext):
    if not is_admin(update):
        update.message.reply_text("❌ هذا الأمر للإدمن فقط.")
        return
    args = context.args
    if len(args) != 2:
        update.message.reply_text("⚠️ الاستخدام: /set_price <id> <السعر>")
        return
    pid = parse_int(args[0])
    price = parse_float(args[1])
    if pid is None or price is None or price < 0:
        update.message.reply_text("❌ قيم غير صحيحة.")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE products SET price = ? WHERE id = ?", (price, pid))
    conn.commit()
    if cur.rowcount == 0:
        update.message.reply_text("❌ منتج غير موجود.")
    else:
        update.message.reply_text("✅ تم تحديث السعر.")
    conn.close()

def set_stock(update: Update, context: CallbackContext):
    if not is_admin(update):
        update.message.reply_text("❌ هذا الأمر للإدمن فقط.")
        return
    args = context.args
    if len(args) != 2:
        update.message.reply_text("⚠️ الاستخدام: /set_stock <id> <الكمية>")
        return
    pid = parse_int(args[0])
    stock = parse_int(args[1])
    if pid is None or stock is None or stock < 0:
        update.message.reply_text("❌ قيم غير صحيحة.")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE products SET stock = ? WHERE id = ?", (stock, pid))
    conn.commit()
    if cur.rowcount == 0:
        update.message.reply_text("❌ منتج غير موجود.")
    else:
        update.message.reply_text("✅ تم تحديث المخزون.")
    conn.close()

# 🧾 تسجيل بيع
def _parse_sale_args(tokens: List[str]) -> List[Tuple[int, int]]:
    # يدعم: [id qty] أو [id1:qty1,id2:qty2]
    if len(tokens) == 2 and ":" not in tokens[0] and ":" not in tokens[1]:
        pid = parse_int(tokens[0])
        qty = parse_int(tokens[1])
        if pid is None or qty is None or qty <= 0:
            return []
        return [(pid, qty)]
    # صيغة متعددة العناصر بفاصلة
    joined = " ".join(tokens).replace(" ", "")
    items = []
    for part in joined.split(','):
        if not part:
            continue
        if ':' not in part:
            return []
        a, b = part.split(':', 1)
        pid = parse_int(a)
        qty = parse_int(b)
        if pid is None or qty is None or qty <= 0:
            return []
        items.append((pid, qty))
    return items

def sale_command(update: Update, context: CallbackContext):
    if not is_admin(update):
        update.message.reply_text("❌ هذا الأمر للإدمن فقط.")
        return
    if not context.args:
        update.message.reply_text(
            "⚠️ الاستخدام: /sale <id> <الكمية> أو /sale <id1>:<q1>,<id2>:<q2>"
        )
        return
    items = _parse_sale_args(context.args)
    if not items:
        update.message.reply_text("❌ صيغة غير صحيحة للطلب.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        # التحقق من التوفر والأسعار
        product_map = {}
        for pid, qty in items:
            cur.execute("SELECT name, price, stock FROM products WHERE id = ?", (pid,))
            row = cur.fetchone()
            if not row:
                update.message.reply_text(f"❌ المنتج #{pid} غير موجود.")
                conn.close()
                return
            name, price, stock = row
            if stock < qty:
                update.message.reply_text(f"❌ مخزون غير كافٍ للمنتج #{pid} ({name}). المتاح: {stock}")
                conn.close()
                return
            product_map[pid] = (name, price, stock)

        # إنشاء السيل
        now = datetime.utcnow().isoformat()
        cur.execute("INSERT INTO sales(created_at) VALUES (?)", (now,))
        sale_id = cur.lastrowid

        subtotal = 0.0
        lines = [f"🧾 فاتورة #{sale_id}", f"🗓️ {now}", ""]
        for pid, qty in items:
            name, price, stock = product_map[pid]
            line_total = price * qty
            subtotal += line_total
            # حفظ العناصر
            cur.execute(
                "INSERT INTO sale_items(sale_id, product_id, quantity, unit_price, line_total) VALUES (?, ?, ?, ?, ?)",
                (sale_id, pid, qty, price, line_total)
            )
            # تحديث المخزون
            cur.execute("UPDATE products SET stock = stock - ? WHERE id = ?", (qty, pid))
            lines.append(f"#{pid} {name} — {qty} × {price} = {line_total}")

        total = subtotal
        lines.append("")
        lines.append(f"الإجمالي: {total}")
        conn.commit()
        update.message.reply_text("\n".join(lines))
    except Exception as e:
        conn.rollback()
        print(e)
        update.message.reply_text("❌ حدث خطأ أثناء تسجيل البيع.")
    finally:
        conn.close()

# 📊 التقارير
def today_sales(update: Update, context: CallbackContext):
    if not is_admin(update):
        update.message.reply_text("❌ هذا الأمر للإدمن فقط.")
        return
    start = date.today().isoformat()
    end = date.today().isoformat()
    _report(update, start, end)

def report_command(update: Update, context: CallbackContext):
    if not is_admin(update):
        update.message.reply_text("❌ هذا الأمر للإدمن فقط.")
        return
    args = context.args
    if len(args) != 2:
        update.message.reply_text("⚠️ الاستخدام: /report <YYYY-MM-DD> <YYYY-MM-DD>")
        return
    start, end = args[0], args[1]
    _report(update, start, end)

def _report(update: Update, start_date: str, end_date: str):
    # يشمل كلا اليومين
    try:
        start_iso = datetime.fromisoformat(start_date).date()
        end_iso = datetime.fromisoformat(end_date).date()
        if end_iso < start_iso:
            update.message.reply_text("❌ نهاية الفترة قبل بدايتها.")
            return
    except Exception:
        update.message.reply_text("❌ تواريخ غير صالحة. استخدم YYYY-MM-DD")
        return
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    # نجلب الإجمالي وعدد الفواتير وعناصرها
    cur.execute(
        """
        SELECT s.id, s.created_at, SUM(si.line_total)
        FROM sales s
        JOIN sale_items si ON si.sale_id = s.id
        WHERE date(s.created_at) BETWEEN date(?) AND date(?)
        GROUP BY s.id, s.created_at
        ORDER BY s.id ASC
        """,
        (start_date, end_date)
    )
    sales_rows = cur.fetchall()
    total_sum = sum(r[2] for r in sales_rows) if sales_rows else 0.0
    # عدد العناصر المباعة
    cur.execute(
        """
        SELECT SUM(quantity) FROM sale_items si
        JOIN sales s ON s.id = si.sale_id
        WHERE date(s.created_at) BETWEEN date(?) AND date(?)
        """,
        (start_date, end_date)
    )
    qty_row = cur.fetchone()
    total_qty = qty_row[0] if qty_row and qty_row[0] is not None else 0
    conn.close()
    if not sales_rows:
        update.message.reply_text("📊 لا توجد مبيعات في هذه الفترة.")
        return
    lines = [f"📊 تقرير المبيعات من {start_date} إلى {end_date}", ""]
    for sid, created_at, sum_total in sales_rows:
        lines.append(f"#فاتورة {sid} — {created_at} — الإجمالي {sum_total}")
    lines.append("")
    lines.append(f"إجمالي المبيعات: {total_sum}")
    lines.append(f"إجمالي الكميات المباعة: {total_qty}")
    update.message.reply_text("\n".join(lines))

# 🚀 تشغيل البوت
def main():
    init_db()
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # أوامر
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help_command))

    # استقبال الرسائل من الأعضاء
    dp.add_handler(MessageHandler(Filters.private & ~Filters.command & ~Filters.reply, handle_user_message))

    # استقبال الردود من الإدمن
    dp.add_handler(MessageHandler(Filters.private & Filters.reply, handle_admin_reply))

    # منتجات
    dp.add_handler(CommandHandler("add_product", add_product))
    dp.add_handler(CommandHandler("list_products", list_products))
    dp.add_handler(CommandHandler("set_price", set_price))
    dp.add_handler(CommandHandler("set_stock", set_stock))

    # مبيعات
    dp.add_handler(CommandHandler("sale", sale_command))
    dp.add_handler(CommandHandler("today_sales", today_sales))
    dp.add_handler(CommandHandler("report", report_command))

    # تشغيل البوت
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

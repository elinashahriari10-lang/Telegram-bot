from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os

# 🔐 امن‌تر برای Render
TOKEN = os.getenv("8587610117:AAGF0-43mGPIK8VvcmIEPa85KFX_eQ-wgN4")
ADMIN_ID = 1619270337

message_map = {}
waiting = set()
users = set()
user_lang = {}

texts = {
    "fa": {
        "welcome": "سلام 🤍\nبرای ارسال پیام دکمه رو بزن:",
        "type": "پیامتو بنویس 👋",
        "sent": "پیام شما ارسال شد 🩷",
        "admin": "🔧 پنل ادمین"
    },
    "en": {
        "welcome": "Welcome 🤍\nTap to send message:",
        "type": "Type your message 👋",
        "sent": "Your message has been sent 🩷",
        "admin": "🔧 Admin panel"
    }
}

def get_lang(uid):
    return user_lang.get(uid, "fa")

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    users.add(uid)

    lang = get_lang(uid)

    keyboard = [["✉️ Send Message"], ["🌐 Change Language"]]

    if uid == ADMIN_ID:
        keyboard.append(["🔧 Admin Panel"])

    await update.message.reply_text(
        texts[lang]["welcome"],
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ---------------- ADMIN PANEL ----------------
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    keyboard = [
        ["📨 View Messages"],
        ["📊 Stats"],
        ["📢 Broadcast"],
        ["🔙 Back"]
    ]

    await update.message.reply_text(
        texts["fa"]["admin"],
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ---------------- LANGUAGE ----------------
async def change_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🇮🇷 فارسی", "🇬🇧 English"],
        ["🇸🇦 العربية", "🇷🇺 Русский"]
    ]

    await update.message.reply_text(
        "🌐 Choose language",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ---------------- HANDLE ----------------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text
    uid = user.id

    lang = get_lang(uid)

    if text == "🌐 Change Language":
        await change_lang(update, context)
        return

    if text in ["🇮🇷 فارسی", "🇬🇧 English", "🇸🇦 العربية", "🇷🇺 Русский"]:
        mapping = {
            "🇮🇷 فارسی": "fa",
            "🇬🇧 English": "en",
            "🇸🇦 العربية": "ar",
            "🇷🇺 Русский": "ru"
        }
        user_lang[uid] = mapping[text]
        await start(update, context)
        return

    if text == "🔧 Admin Panel":
        await admin_panel(update, context)
        return

    if text == "🔙 Back":
        await start(update, context)
        return

    if text == "📨 View Messages" and uid == ADMIN_ID:
        if not message_map:
            await update.message.reply_text("No messages yet.")
            return

        msg = "📨 Messages:\n\n"
        for mid, u in list(message_map.items())[-10:]:
            msg += f"User: {u} | MsgID: {mid}\n"

        await update.message.reply_text(msg)
        return

    if text == "📊 Stats" and uid == ADMIN_ID:
        await update.message.reply_text(
            f"Users: {len(users)}\nMessages: {len(message_map)}"
        )
        return

    if text == "📢 Broadcast" and uid == ADMIN_ID:
        waiting.add(uid)
        await update.message.reply_text("Send message for all users 👇")
        return

    if uid in waiting and uid == ADMIN_ID:
        waiting.remove(uid)

        for u in users:
            try:
                await context.bot.send_message(chat_id=u, text=f"📢 {text}")
            except:
                pass

        await update.message.reply_text("Sent ✔️")
        return

    if text == "✉️ Send Message":
        waiting.add(uid)
        await update.message.reply_text(texts[lang]["type"])
        return

    if uid in waiting and uid != ADMIN_ID:
        waiting.remove(uid)

        sent = await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 New message from {uid}:\n\n{text}"
        )

        message_map[sent.message_id] = uid

        await update.message.reply_text(texts[lang]["sent"])
        return

# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    app.run_polling()

if __name__ == "__main__":
    main()

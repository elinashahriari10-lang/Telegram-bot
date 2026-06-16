from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

import os
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1619270337

users = set()
messages = []
user_lang = {}

# ---------------- LANGS ----------------
texts = {
    "fa": {
        "welcome": "سلام 🤍\nپیامت رو بفرست:",
        "sent": "پیام شما ارسال شد 🩷"
    },
    "en": {
        "welcome": "Hi 🤍\nSend your message:",
        "sent": "Your message was sent 🩷"
    },
    "ar": {
        "welcome": "مرحبا 🤍\nأرسل رسالتك:",
        "sent": "تم إرسال رسالتك 🩷"
    },
    "ru": {
        "welcome": "Привет 🤍\nОтправь сообщение:",
        "sent": "Сообщение отправлено 🩷"
    }
}

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.add(user_id)

    keyboard = [
        ["🇮🇷 فارسی", "🇬🇧 English"],
        ["🇸🇦 العربية", "🇷🇺 Русский"],
        ["👮 Admin Panel"]
    ]

    await update.message.reply_text(
        "Choose language 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# ---------------- HANDLE ----------------
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    users.add(user_id)

    # ---------------- LANGUAGE ----------------
    if text == "🇮🇷 فارسی":
        user_lang[user_id] = "fa"
        await update.message.reply_text(texts["fa"]["welcome"])

    elif text == "🇬🇧 English":
        user_lang[user_id] = "en"
        await update.message.reply_text(texts["en"]["welcome"])

    elif text == "🇸🇦 العربية":
        user_lang[user_id] = "ar"
        await update.message.reply_text(texts["ar"]["welcome"])

    elif text == "🇷🇺 Русский":
        user_lang[user_id] = "ru"
        await update.message.reply_text(texts["ru"]["welcome"])

    # ---------------- ADMIN PANEL ----------------
    elif text == "👮 Admin Panel" and user_id == ADMIN_ID:
        keyboard = [
            ["📨 View Messages"],
            ["📊 Stats"],
            ["📢 Broadcast"],
            ["🔙 Back"]
        ]
        await update.message.reply_text(
            "Admin Panel 👇",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        )

    # ---------------- VIEW MESSAGES ----------------
    elif text == "📨 View Messages" and user_id == ADMIN_ID:
        if not messages:
            await update.message.reply_text("No messages yet.")
        else:
            for msg in messages[-10:]:
                await update.message.reply_text(
                    f"👤 ID: {msg['user_id']}\n💬 {msg['text']}"
                )

    # ---------------- STATS ----------------
    elif text == "📊 Stats" and user_id == ADMIN_ID:
        await update.message.reply_text(f"👥 Users: {len(users)}")

    # ---------------- BROADCAST ----------------
    elif text.startswith("/broadcast") and user_id == ADMIN_ID:
        msg = text.replace("/broadcast", "").strip()

        for uid in users:
            try:
                await context.bot.send_message(uid, msg)
            except:
                pass

        await update.message.reply_text("Broadcast sent ✔️")

    # ---------------- BACK ----------------
    elif text == "🔙 Back" and user_id == ADMIN_ID:
        await start(update, context)

    # ---------------- NORMAL USER MESSAGE ----------------
    else:
        messages.append({
            "user_id": user_id,
            "text": text
        })

        lang = user_lang.get(user_id, "fa")

        await update.message.reply_text(
            texts[lang]["sent"],
            reply_to_message_id=update.message.message_id
        )

# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle))

    print("Bot started...")
    app.run_polling()

if name == "__main__": main()

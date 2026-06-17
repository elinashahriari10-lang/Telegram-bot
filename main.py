from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 1619270337

users = set()
messages = []
user_lang = {}

# ---------------- TEXTS ----------------
texts = {
    "fa": {"welcome": "سلام 🤍\nپیامت رو بفرست:", "sent": "پیام شما ارسال شد 🩷"},
    "en": {"welcome": "Hi 🤍\nSend your message:", "sent": "Sent 🩷"},
    "ar": {"welcome": "مرحبا 🤍\nأرسل رسالتك:", "sent": "تم الإرسال 🩷"},
    "ru": {"welcome": "Привет 🤍\nОтправь сообщение:", "sent": "Отправлено 🩷"}
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
    if text in ["🇮🇷 فارسی", "🇬🇧 English", "🇸🇦 العربية", "🇷🇺 Русский"]:
        lang_map = {
            "🇮🇷 فارسی": "fa",
            "🇬🇧 English": "en",
            "🇸🇦 العربية": "ar",
            "🇷🇺 Русский": "ru"
        }
        user_lang[user_id] = lang_map[text]
        await update.message.reply_text(texts[lang_map[text]]["welcome"])
        return

    # ---------------- ADMIN PANEL ----------------
    if text == "👮 Admin Panel" and user_id == ADMIN_ID:
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
        return

    # ---------------- VIEW MESSAGES ----------------
    if text == "📨 View Messages" and user_id == ADMIN_ID:
        if not messages:
            await update.message.reply_text("No messages yet.")
            return

        for msg in messages[-10:]:
            await update.message.reply_text(
                f"👤 ID: {msg['user_id']}\n💬 {msg['text']}"
            )
        return

    # ---------------- STATS ----------------
    if text == "📊 Stats" and user_id == ADMIN_ID:
        await update.message.reply_text(f"👥 Users: {len(users)}")
        return

    # ---------------- BROADCAST START ----------------
    if text == "📢 Broadcast" and user_id == ADMIN_ID:
        context.user_data["broadcast"] = True
        await update.message.reply_text("📢 پیام را ارسال کنید:")
        return

    # ---------------- BROADCAST SEND ----------------
    if context.user_data.get("broadcast") and user_id == ADMIN_ID:
        context.user_data["broadcast"] = False

        for uid in users:
            try:
                await context.bot.send_message(chat_id=uid, text=text)
            except:
                pass

        await update.message.reply_text("✅ Broadcast sent")
        return

    # ---------------- REPLY SYSTEM (FIXED) ----------------
    if user_id == ADMIN_ID and update.message.reply_to_message:
        replied = update.message.reply_to_message

        # فقط اگر پیام واقعی کاربر باشد
        for msg in messages:
            if str(msg["text"]) == str(replied.text):
                try:
                    await context.bot.send_message(
                        chat_id=msg["user_id"],
                        text=text
                    )
                    await update.message.reply_text("✅ پاسخ ارسال شد")
                except:
                    await update.message.reply_text("❌ ارسال نشد")
                return

    # ---------------- USER MESSAGE ----------------
    if user_id not in user_lang:
        user_lang[user_id] = "fa"

    messages.append({
        "user_id": user_id,
        "text": text
    })

    await update.message.reply_text(
        texts[user_lang[user_id]]["sent"]
    )

# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()

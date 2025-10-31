import telebot
import json
import time
from telebot import types
from flask import Flask, request

# === Replace with your bot token ===
TOKEN = "8413347608:AAEaq5dFwwCqNSU0iq78B91TXHD3ZU-mcTo"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# ===== Store welcome/goodbye messages =====
try:
    with open("messages.json", "r") as f:
        messages = json.load(f)
except:
    messages = {
        "welcome": "စောက်ချောကြီးအဖွဲ့မှကြိုဆိုပါတယ်💘",
        "goodbye": "ပြန်ထွက်လို့ဂိမ်းရှုံးပါစေ🫤🫤🫤"
    }

def save_messages():
    with open("messages.json", "w") as f:
        json.dump(messages, f)

# ===== Warns storage =====
warns = {}

# ===============================
# Command Handlers
# ===============================

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to the user's message to ban them.")
        return
    user_id = message.reply_to_message.from_user.id
    username = message.reply_to_message.from_user.username or user_id
    chat_id = message.chat.id
    try:
        bot.ban_chat_member(chat_id, user_id)
        bot.send_message(chat_id, f"🚫 @{username} has been banned.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {e}")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to the user's message to unban them.")
        return
    user_id = message.reply_to_message.from_user.id
    username = message.reply_to_message.from_user.username or user_id
    chat_id = message.chat.id
    try:
        bot.unban_chat_member(chat_id, user_id)
        bot.send_message(chat_id, f"✅ @{username} has been unbanned.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {e}")

@bot.message_handler(commands=['mute'])
def mute_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to the user's message to mute them.")
        return

    args = message.text.split()
    duration = 0
    if len(args) > 1:
        time_str = args[1]
        try:
            if time_str.endswith('s'):
                duration = int(time_str[:-1])
            elif time_str.endswith('m'):
                duration = int(time_str[:-1]) * 60
            elif time_str.endswith('h'):
                duration = int(time_str[:-1]) * 3600
            else:
                duration = int(time_str)
        except:
            bot.reply_to(message, "⚠️ Invalid time format! Use /mute <duration> (e.g., 5m, 30s, 1h)")
            return

    user_id = message.reply_to_message.from_user.id
    username = message.reply_to_message.from_user.username or user_id
    chat_id = message.chat.id
    until_date = int(time.time() + duration) if duration > 0 else None

    try:
        bot.restrict_chat_member(
            chat_id, user_id,
            can_send_messages=False,
            can_send_media_messages=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
            until_date=until_date
        )
        if duration > 0:
            bot.send_message(chat_id, f"🔇 @{username} has been muted for {args[1]}.")
        else:
            bot.send_message(chat_id, f"🔇 @{username} has been muted indefinitely.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {e}")

@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to the user's message to unmute them.")
        return
    user_id = message.reply_to_message.from_user.id
    username = message.reply_to_message.from_user.username or user_id
    chat_id = message.chat.id
    try:
        bot.restrict_chat_member(
            chat_id, user_id,
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        )
        bot.send_message(chat_id, f"🔊 @{username} has been unmuted.")
    except Exception as e:
        bot.send_message(chat_id, f"❌ Error: {e}")

@bot.message_handler(commands=['warn'])
def warn_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to the user's message to warn them.")
        return
    user_id = message.reply_to_message.from_user.id
    username = message.reply_to_message.from_user.username or user_id
    chat_id = message.chat.id

    warns[user_id] = warns.get(user_id, 0) + 1
    bot.send_message(chat_id, f"⚠️ @{username} has been warned ({warns[user_id]}/3).")

    if warns[user_id] >= 3:
        bot.ban_chat_member(chat_id, user_id)
        bot.send_message(chat_id, f"🚫 @{username} has been banned due to 3 warnings.")

@bot.message_handler(commands=['unwarn'])
def unwarn_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to the user's message to remove a warning.")
        return
    user_id = message.reply_to_message.from_user.id
    username = message.reply_to_message.from_user.username or user_id
    chat_id = message.chat.id

    if user_id in warns and warns[user_id] > 0:
        warns[user_id] -= 1
        bot.send_message(chat_id, f"✅ Warning removed for @{username} ({warns[user_id]}/3).")
    else:
        bot.send_message(chat_id, f"ℹ️ @{username} has no warnings.")

@bot.message_handler(content_types=['new_chat_members'])
def new_member(message):
    for member in message.new_chat_members:
        user_info = f"""
🎉 {messages['welcome']} 🎉

User ID:🆔 {member.id}
Username:⚠️ @{member.username if member.username else 'No Set'}
First Name:⚠️ {member.first_name}
Last Name:⚠️ {member.last_name if member.last_name else 'No Set'}
"""
        bot.send_message(message.chat.id, user_info)

@bot.message_handler(content_types=['left_chat_member'])
def member_left(message):
    member = message.left_chat_member
    user_info = f"""
🔯 {messages['goodbye']} 🔯

User ID:🆔 {member.id}
Username:⚠️ @{member.username if member.username else 'No Set'}
First Name:⚠️ {member.first_name}
Last Name:⚠️ {member.last_name if member.last_name else 'No Set'}
"""
    bot.send_message(message.chat.id, user_info)

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if not message.text:
        return
    text = message.text.lower()

    if "http://" in text or "https://" in text or "t.me/" in text or "+t.me" in text:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, "⚠️ Link not allowed!")
        except Exception as e:
            print(f"Error deleting message: {e}")
        return

    if message.text.startswith("/"):
        return

    # simple auto reply example
    if "hi" in text:
        bot.reply_to(message, "Hello there 👋")
    elif "gn" in text:
        bot.reply_to(message, "Good night 🌙")

# ===============================
# Flask Webhook Setup
# ===============================

@app.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def index():
    return "Bot is running via Webhook.", 200

if __name__ == "__main__":
    import os
    # Replace YOUR_DOMAIN with your actual hosting URL
    WEBHOOK_URL = f"https://YOUR_DOMAIN/{TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

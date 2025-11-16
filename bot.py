import telebot
from flask import Flask, request
import requests
import json
import time
import datetime
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# === Replace with your bot token ===
TOKEN = "8253001112:AAE51vOORcdJCYMWz6L340goOu9ElpkhtuM"
bot = telebot.TeleBot(TOKEN)

# ===== Flask App for Webhook =====
app = Flask(__name__)

# ===== Store welcome/goodbye messages =====
try:
    with open("messages.json", "r") as f:
        messages = json.load(f)
except:
    messages = {
        "welcome":"⭐️ ｢ɴᴇᴡ ᴜꜱᴇʀ ɴᴏᴛᴛɪꜰɪᴄᴀᴛɪᴏɴ 」⭐️",
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
def handle_commands(message):
    chat_id = message.chat.id

    # /ban
    if message.text.startswith("/ban"):
        if not message.reply_to_message:
            bot.reply_to(message, "⚠️ Reply to the user's message to ban them.")
            return
        user_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username or user_id
        try:
            bot.ban_chat_member(chat_id, user_id)
            bot.send_message(chat_id, f"🚫 @{username} has been banned.")
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {e}")

    # /unban
    elif message.text.startswith("/unban"):
        if not message.reply_to_message:
            bot.reply_to(message, "⚠️ Reply to the user's message to unban them.")
            return
        user_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username or user_id
        try:
            bot.unban_chat_member(chat_id, user_id)
            bot.send_message(chat_id, f"✅ @{username} has been unbanned.")
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {e}")

    # /mute
    elif message.text.startswith("/mute"):
        if not message.reply_to_message:
            bot.reply_to(message, "⚠️ Reply to the user's message to mute them.")
            return
        args = message.text.split()
        duration = 0
        if len(args) > 1:
            time_str = args[1]
            try:
                if time_str.endswith('s'): duration = int(time_str[:-1])
                elif time_str.endswith('m'): duration = int(time_str[:-1])*60
                elif time_str.endswith('h'): duration = int(time_str[:-1])*3600
                else: duration = int(time_str)
            except:
                bot.reply_to(message, "⚠️ Invalid time format! Use /mute <duration> (e.g., 5m, 30s, 1h)")
                return
        user_id = message.reply_to_message.from_user.id
        username = message.reply_to_message.from_user.username or user_id
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
            if duration>0:
                bot.send_message(chat_id, f"🔇 @{username} has been muted for {args[1]}.")
            else:
                bot.send_message(chat_id, f"🔇 @{username} has been muted indefinitely.")
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {e}")

    # /unmute
    elif message.text.startswith("/unmute"):
        if not message.reply_to_message:
            bot.reply_to(message, "⚠️ Reply to the user's message to unmute them.")
            return
        user_id = message.reply_to_message.from_user.id
        try:
            bot.restrict_chat_member(
                chat_id, user_id,
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True
            )
            bot.send_message(chat_id, f"🔊 User unmuted successfully.")
        except Exception as e:
            bot.send_message(chat_id, f"❌ Error: {e}")

    # /warn
    elif message.text.startswith("/warn"):
        if not message.reply_to_message:
            bot.reply_to(message, "⚠️ Reply to the user's message to warn them.")
            return
        user_id = message.reply_to_message.from_user.id
        warns[user_id] = warns.get(user_id,0)+1
        bot.send_message(chat_id, f"⚠️ User warned ({warns[user_id]}/3).")
        if warns[user_id]>=3:
            bot.ban_chat_member(chat_id, user_id)
            bot.send_message(chat_id, f"🚫 User banned due to 3 warnings.")

    # /unwarn
    elif message.text.startswith("/unwarn"):
        if not message.reply_to_message:
            bot.reply_to(message, "⚠️ Reply to remove warning.")
            return
        user_id = message.reply_to_message.from_user.id
        if user_id in warns and warns[user_id]>0:
            warns[user_id]-=1
            bot.send_message(chat_id, f"✅ Warning removed ({warns[user_id]}/3).")
        else:
            bot.send_message(chat_id, "ℹ️ User has no warnings.")

# ===============================
# Welcome / Goodbye Handlers
# ===============================
def welcome_member(message):
    for member in message.new_chat_members:
        user_id = member.id
        username = member.username or "No Set"
        first_name = member.first_name or "No Set"
        last_name = member.last_name or "No Set"
        clickable_name = f"<a href='tg://user?id={user_id}'>{first_name}</a>"

        photos = bot.get_user_profile_photos(user_id)
        if photos.total_count>0:
            file_info = bot.get_file(photos.photos[0][-1].file_id)
            photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
            response = requests.get(photo_url)
            profile_img = Image.open(BytesIO(response.content)).convert("RGBA")
        else:
            profile_img = Image.open("default.jpg").convert("RGBA")

        mask = Image.new("L", profile_img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0,0,profile_img.size[0], profile_img.size[1]), fill=255)
        profile_img.putalpha(mask)
        profile_img = profile_img.resize((400,400))

        bg = Image.open("welcome.jpg").convert("RGBA")
        bg = bg.resize((2000,1500))
        bg.paste(profile_img,(1480,1000),profile_img)

        draw = ImageDraw.Draw(bg)
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        font_info = ImageFont.truetype(font_path,100)

        join_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((60,400), f"🆔 User ID: {user_id}", fill="yellow", font=font_info)
        draw.text((60,800), f"🔗 Username: {username}", fill="yellow", font=font_info)
        draw.text((60,1200), f"⏰ Joined: {join_time}", fill="yellow", font=font_info)

        final = BytesIO()
        bg.save(final,"PNG")
        final.seek(0)

        welcome_text = (
            f" {messages['welcome']} \n"
            f"━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━\n"
            f"👤 Name: {clickable_name}\n"
            f"Username: @{username}\n"
            f"First Name: {first_name}\n"
            f"Last Name: {last_name}\n"
            f"🆔 User ID: {user_id}\n"
            f"🤖 Bot: @{bot.get_me().username}"
        )

        bot.send_photo(message.chat.id, final, caption=welcome_text, parse_mode="HTML")

def goodbye_member(message):
    member = message.left_chat_member
    user_id = member.id
    username = member.username or "No Set"
    first_name = member.first_name or "No Set"
    last_name = member.last_name or "No Set"
    clickable_name = f"<a href='tg://user?id={user_id}'>{first_name}</a>"
    goodbye_text = (
        f" {messages['goodbye']} \n"
        f"━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━\n"
        f"👤 Name: {clickable_name}\n"
        f"Username: @{username}\n"
        f"First Name: {first_name}\n"
        f"Last Name: {last_name}\n"
        f"🆔 User ID: {user_id}\n"
        f"🤖 Bot: @{bot.get_me().username}"
    )
    bot.send_message(message.chat.id, goodbye_text, parse_mode="HTML")

# ===============================
# Auto Reply + Link Filter
# ===============================
def auto_reply(message):
    if not message.text:
        return
    text = message.text.lower()
    chat_id = message.chat.id

    if any(x in text for x in ["http://","https://","t.me/","+t.me"]):
        try:
            bot.delete_message(chat_id,message.message_id)
            bot.send_message(chat_id,"⚠️ Links are not allowed!")
        except: pass
        return

    if message.text.startswith("/"): return

    replies = {
        "hi":"ဘာကူညီပေးရမလဲ",
        "ကောင်းလား":"ကောင်းတယ်",
        "ပျင်းတယ်":"ရေရောလိုက်ပါ",
        "မောနင်း":"မောနင်းပါသဲလေး🤖",
        "gn":"ကောင်းသောညပါ",
        "night":"GoodNightပါသဲလေး😘😘😘",
        "morning":"Goodmorning သာယာသောနေ့လေးဖြစ်ပါစေ😍😍😍",
        # add all sticker triggers if needed
    }

    stickers = {
        "win":"CAACAgUAAxkBAAICFmj348VPRDJGonl1OmTpB_jkxwbsAAISGAACZSPoVij3kkk-qYD6NgQ",
        "lose":"CAACAgQAAxkBAAICV2j39CBUhKl91twKSitUCc_c4NapAALsFQAC3XowU7yjO8fCQjfgNgQ",
        "အေးဆေး":"CAACAgUAAxkBAAICW2j39ELiDEUzG_5kPiAxZRw6SpKiAAJOHQACXoURV9kmXOQOlnALNgQ"
    }

    for k,v in replies.items():
        if k in text:
            bot.reply_to(message,v)
            return
    for k,v in stickers.items():
        if k in text:
            bot.send_sticker(chat_id,v)
            return

# ===============================
# Webhook Route
# ===============================
@app.route('/bot', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    message = update.message

    if message:
        handle_commands(message)
        welcome_member(message) if message.new_chat_members else None
        goodbye_member(message) if message.left_chat_member else None
        auto_reply(message)
    return "OK",200

# ===============================
# Start Flask App
# ===============================
if __name__ == "__main__":
    WEBHOOK_URL = "https://https://electronic-dona-shinelinaung-57trey.koyeb.app/bot"  # Change this
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=8000)

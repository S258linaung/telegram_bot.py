import telebot
import requests
import json
import time
import datetime
from flask import Flask, request, abort
from telebot import types
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

TOKEN = "8253001112:AAE51vOORcdJCYMWz6L340goOu9ElpkhtuM"
bot = telebot.TeleBot(TOKEN)

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

warns = {}

# ===== Webhook route =====
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_str = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)

@app.route("/")
def index():
    return "Bot is running!"

# ===========================
# Bot Handlers (mutes/ban/warn/welcome/left/auto reply)
# ===========================

# /ban
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

# /unban
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

# /mute
@bot.message_handler(commands=['mute'])
def mute_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to the user's message to mute them.")
        return
    args = message.text.split()
    duration = 0
    if len(args) > 1:
        try:
            if args[1].endswith('s'):
                duration = int(args[1][:-1])
            elif args[1].endswith('m'):
                duration = int(args[1][:-1])*60
            elif args[1].endswith('h'):
                duration = int(args[1][:-1])*3600
            else:
                duration = int(args[1])
        except:
            bot.reply_to(message, "⚠️ Invalid time format!")
            return
    user_id = message.reply_to_message.from_user.id
    username = message.reply_to_message.from_user.username or user_id
    chat_id = message.chat.id
    until_date = int(time.time() + duration) if duration>0 else None
    try:
        bot.restrict_chat_member(chat_id, user_id,
                                can_send_messages=False,
                                can_send_media_messages=False,
                                can_send_other_messages=False,
                                can_add_web_page_previews=False,
                                until_date=until_date)
        if duration>0:
            bot.send_message(chat_id,f"🔇 @{username} muted for {args[1]}")
        else:
            bot.send_message(chat_id,f"🔇 @{username} muted indefinitely")
    except Exception as e:
        bot.send_message(chat_id,f"❌ Error: {e}")

# /unmute
@bot.message_handler(commands=['unmute'])
def unmute_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to the user's message to unmute them.")
        return
    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    try:
        bot.restrict_chat_member(chat_id, user_id,
                                can_send_messages=True,
                                can_send_media_messages=True,
                                can_send_other_messages=True,
                                can_add_web_page_previews=True)
        bot.send_message(chat_id,f"🔊 User unmuted")
    except Exception as e:
        bot.send_message(chat_id,f"❌ Error: {e}")

# /warn
@bot.message_handler(commands=['warn'])
def warn_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to the user's message to warn them.")
        return
    user_id = message.reply_to_message.from_user.id
    username = message.reply_to_message.from_user.username or user_id
    chat_id = message.chat.id
    warns[user_id] = warns.get(user_id,0)+1
    bot.send_message(chat_id,f"⚠️ @{username} warned ({warns[user_id]}/3)")
    if warns[user_id]>=3:
        bot.ban_chat_member(chat_id,user_id)
        bot.send_message(chat_id,f"🚫 @{username} banned due to 3 warns")

# /unwarn
@bot.message_handler(commands=['unwarn'])
def unwarn_user(message):
    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to the user's message to remove a warning.")
        return
    user_id = message.reply_to_message.from_user.id
    chat_id = message.chat.id
    if warns.get(user_id,0)>0:
        warns[user_id]-=1
        bot.send_message(chat_id,f"✅ Warning removed ({warns[user_id]}/3)")
    else:
        bot.send_message(chat_id,f"ℹ️ No warnings")

# ===========================
# Welcome & Left member
# ===========================
@bot.message_handler(content_types=['new_chat_members'])
def new_member(message):
    for member in message.new_chat_members:
        user_id = member.id
        username = member.username or "No Set"
        first_name = member.first_name or "No Set"
        clickable_name = f"<a href='tg://user?id={user_id}'>{first_name}</a>"

        try:
            photos = bot.get_user_profile_photos(user_id)
            if photos.total_count > 0:
                file_info = bot.get_file(photos.photos[0][-1].file_id)
                photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
                response = requests.get(photo_url)
                profile_img = Image.open(BytesIO(response.content)).convert("RGBA")
            else:
                profile_img = Image.open("default.jpg").convert("RGBA")
        except:
            profile_img = Image.open("default.jpg").convert("RGBA")

        mask = Image.new("L", profile_img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, profile_img.size[0], profile_img.size[1]), fill=255)
        profile_img.putalpha(mask)
        profile_img = profile_img.resize((400, 400))

        bg = Image.open("welcome.jpg").convert("RGBA")
        bg = bg.resize((2000,1500))
        bg.paste(profile_img, (1480,1000), profile_img)

        draw = ImageDraw.Draw(bg)
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        font_name = ImageFont.truetype(font_path, 100)
        font_info = ImageFont.truetype(font_path, 100)

        join_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        draw.text((60,400), f"🆔 User ID: {user_id}", fill="yellow", font=font_info)
        draw.text((60,800), f"🔗 Username: {username}", fill="yellow", font=font_info)
        draw.text((60,1200), f"⏰ Joined: {join_time}", fill="yellow", font=font_info)

        final = BytesIO()
        bg.save(final, "PNG")
        final.seek(0)

        welcome_text = (
            f" {messages['welcome']} \n"
            f"━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━\n"
            f"👤 Name: {clickable_name}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Username: @{username}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🆔 User ID: {user_id}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🤖 Bot: @{bot.get_me().username}"
        )

        bot.send_photo(
            message.chat.id,
            final,
            caption=welcome_text,
            parse_mode="HTML") 

@bot.message_handler(content_types=['left_chat_member'])
def left_member(message):
    member = message.left_chat_member
    user_id = member.id
    username = member.username or "No Set"
    first_name = member.first_name or "No Set"
    clickable_name = f"<a href='tg://user?id={user_id}'>{first_name}</a>"
    goodbye_text = (
        f" {messages['goodbye']} \n"
        f"━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━\n"
        f"👤 Name: {clickable_name}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Username: @{username}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 User ID: {user_id}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 Bot: @{bot.get_me().username}"
    )
    bot.send_message(message.chat.id, goodbye_text, parse_mode="HTML")

# ===========================
# Message filter + auto replies + stickers
# ===========================
@bot.message_handler(func=lambda message: True)
def handle_all(message):
    if not message.text:
        return
    text = message.text.lower()

    # Delete links
    if "http://" in text or "https://" in text or "t.me/" in text:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, "⚠️ Link not allowed!")
        except: pass
        return

    # Ignore commands
    if message.text.startswith("/"):
        return

    # Auto replies
    auto_replies = {
        "မောနင်း":"မောနင်းပါသဲလေး🤖",
        "hi":"ဘာကူညီပေးရမလဲ",
        "ကောင်းလား":"ကောင်းတယ်",
        "ပျင်းတယ်":"ရေရောလိုက်ပါ",
        "gn":"ကောင်းသောညပါ",
        "night":"GoodNightပါသဲလေး😘",
        "morning":"Goodmorning သာယာသောနေ့လေးဖြစ်ပါစေ😍"
    }
    for key, reply in auto_replies.items():
        if key in text:
            bot.reply_to(message, reply)
            return

    # Stickers
    if "win" in text:
        bot.send_sticker(message.chat.id, "CAACAgUAAxkBAAICFmj348VPRDJGonl1OmTpB_jkxwbsAAISGAACZSPoVij3kkk-qYD6NgQ")

# ===========================
# Set webhook (run once)
# ===========================
WEBHOOK_URL = "https://electronic-dona.koyeb.app/" + TOKEN
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8000)


import telebot
import requests
import json
import time
import datetime
from flash import Flash,request
from telebot import types
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


# === Replace with your bot token ===
TOKEN = "8253001112:AAE51vOORcdJCYMWz6L340goOu9ElpkhtuM"
bot = telebot.TeleBot(TOKEN)
#=== Flash App for Webhook ===
app = Flash(__name__)

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

# /ban command

def handle_commands(message):
    chat_id = message.chat.id
    # /ban command
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

def handle_commands(message):
    chat_id = message.chat.id
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

# /mute command with duration
def handle_commands(message):

    if not message.reply_to_message:
        bot.reply_to(message, "⚠️ Reply to the user's message to mute them.")
        return

    args = message.text.split()
    duration = 0  # default = 0 → indefinite mute

    if len(args) > 1:
        time_str = args[1]
        try:
            if time_str.endswith('s'):  # seconds
                duration = int(time_str[:-1])
            elif time_str.endswith('m'):  # minutes
                duration = int(time_str[:-1]) * 60
            elif time_str.endswith('h'):  # hours
                duration = int(time_str[:-1]) * 3600
            else:
                duration = int(time_str)  # assume seconds if no suffix
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

# /unmute command

def handle_commands(message):
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

# /warn command

def handle_commands(message):
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

# /unwarn command

def handle_commands(message):
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

# ===============================
# Welcome / Goodbye Handlers
# ===============================

# New member with clickable name & styled message

def handle_commands(message):
    for member in message.new_chat_members:
        user_id = member.id
        username = member.username or "No Set"
        first_name = member.first_name or "No Set"
        last_name = member.last_name or "No Set"
        clickable_name = f"<a href='tg://user?id={user_id}'>{first_name}</a>"
             # Download user profile photo
        photos = bot.get_user_profile_photos(user_id)
        if photos.total_count > 0:
            file_info = bot.get_file(photos.photos[0][-1].file_id)
            photo_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
            response = requests.get(photo_url)
            profile_img = Image.open(BytesIO(response.content)).convert("RGBA")
        else:
            # default if no photo
            profile_img = Image.open("default.jpg").convert("RGBA")

        # Make it circle
        mask = Image.new("L", profile_img.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, profile_img.size[0], profile_img.size[1]), fill=255)
        profile_img.putalpha(mask)
        profile_img = profile_img.resize((400, 400))

        # Load background
        bg = Image.open("welcome.jpg").convert("RGBA")
        bg = bg.resize((2000,1500))
        bg.paste(profile_img, (1480,1000), profile_img)


        # Windows arial.ttf → Linux-safe font
        draw = ImageDraw.Draw(bg)
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # PythonAnywhere တွင်ရှိပြီး safe
        font_name = ImageFont.truetype(font_path, 100)
        font_info = ImageFont.truetype(font_path, 100)


        join_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        draw.text((60,400), f"🆔 User ID: {user_id}", fill="yellow", font=font_info)
        draw.text((60,800), f"🔗 Username: {username}", fill="yellow", font=font_info)
        draw.text((60,1200), f"⏰ Joined: {join_time}", fill="yellow", font=font_info)

        # Save result
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
            f"First Name: {first_name}\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"Last Name: {last_name}\n"
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

# Left member with clickable name & styled message

def handle_commands(message):
    member = message.left_chat_member  # <-- only one member leaves at a time
    user_id = member.id
    username = member.username or "No Set"
    first_name = member.first_name or "No Set"
    last_name = member.last_name or "No Set"
    clickable_name = f"<a href='tg://user?id={user_id}'>{first_name}</a>"

    goodbye_text = (
        f" {messages['goodbye']} \n"
        f"━━━━━━━━•❅•°•❈•°•❅•━━━━━━━━\n"
        f"👤 Name: {clickable_name}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Username: @{username}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"First Name: {first_name}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Last Name: {last_name}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 User ID: {user_id}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🤖 Bot: @{bot.get_me().username}"
    )

    bot.send_message(
        message.chat.id,
        goodbye_text,   # ✅ fixed: send goodbye_text, not welcome_text
        parse_mode="HTML"
    )

# ===============================
# Combined Link Filter + Auto Reply
# ===============================

def handle_all(message):
    if not message.text:
        return
    text = message.text.lower()

    # === 1. Delete links ===
    if "http://" in text or "https://" in text or "t.me/" in text or "+t.me" in text:
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(
                message.chat.id,
                "⚠️ @shinereact1_bot ဘာတေပို့နေတာလဲတောသားလေး🤣🤣🤣!"
            )
        except Exception as e:
            print(f"Error deleting message: {e}")
        return

    # === 2. Ignore commands ===
    if message.text.startswith("/"):
        return

    # === 3. Auto Replies & sticker ===

    if "မောနင်း" in text:
        bot.reply_to(message, "မောနင်းပါသဲလေး🤖")
    elif "hi" in text:
        bot.reply_to(message, "ဘာကူညီပေးရမလဲ")
    elif "သတိရ" in text:
        bot.reply_to(message, "တစ်စုံတစ်ယောက်ကိုမေ့ဖို့ဆိုတာ....ဘုရားတစ်ဆူနဲ့နောက်တစ်ဆူပွင့်ဖို့ကြားကာလလည်းဖြစ်နိုင်ပါတယ်")
    elif "ကောင်းလား" in text:
        bot.reply_to(message, "ကောင်းတယ်")
    elif "ပျင်းတယ်" in text:
        bot.reply_to(message, "ရေရောလိုက်ပါ")
    elif "gn" in text or "Gn" in text:
        bot.reply_to(message, "ကောင်းသောညပါ")
    elif "နာမည်" in text:
        bot.reply_to(message, "ကျွန်တော်ကကိုလူချောပါ")
    elif "ရှိုင်း" in text:
        bot.reply_to(message, "ကိုရှိုင်းသူ့မမနဲ့နပ်နေတယ်မအားဘူး🙂‍↔️🙂‍↔️🙂‍↔️")
    elif "သီချင်း" in text:
        bot.reply_to(message, "ကိုစိုးကြီးရဲ့တယ်လီဖုန်းလား😝😝😝")
    elif "ကြမ်း" in text:
        bot.reply_to(message, "ခက်ကြမ်းကြမ်းပဲ😝😝😝")
    elif "လဉ" in text:
        bot.reply_to(message, "မင်းစားလေ")
    elif "ko" in text or "ကိုကို" in text:
        bot.reply_to(message, "သဲလေးပြော")
    elif "ဘာဆိုင်" in text:
        bot.reply_to(message, "မင်းနဲ့သူမလိုပဲလေ")
    elif "ရှုံး" in text:
        bot.reply_to(message, "မနိုင်ရင်အိပ်တော့အိပ်ရေးဝတယ်")
    elif "night" in text or "Night" in text:
        bot.reply_to(message, "GoodNightပါသဲလေး😘😘😘")
    elif "ထီး" in text:
        bot.reply_to(message, "ရဲရဲပြောစမ်း")
    elif "Morning" in text or "morning" in text:
        bot.reply_to(message, "Goodmorning သာယာသောနေ့လေးဖြစ်ပါစေ😍😍😍")
    elif "ရတယ်" in text:
        bot.reply_to(message, "ရရင်အေးဆေးနေ🤣🤣🤣")
    elif "သူမ" in text:
        bot.reply_to(message, "အဲ့စကားမိုက်ရိုင်းတယ်နော်...")
    elif "ဘာကျ" in text:
        bot.reply_to(message, "နေသားကျတယ်😒😒😒")
    elif "နားပြီ" in text:
        bot.reply_to(message, "နောက်မှတွေ့ကြမယ် 👋")
    elif "မမ" in text:
        bot.reply_to(message, "မမတေကချစ်ဖို့ကောင်းတယ်")
    elif "ဟုတ်လ" in text:
        bot.reply_to(message, "သူနဲ့ကသူငယ်ချင်းတေပါမောင်ရယ်ဆိုတာမျိုးလား🥺🥺🥺")
    elif "lee" in text:
        bot.reply_to(message, "fuckerပဲရောင်ကျေနပ်လား🖕")
    elif "မကျေ" in text:
        bot.reply_to(message, "မကျေနပ်ရင်လဲfuckerပဲ")
    elif "လီး" in text:
        bot.reply_to(message, "အဲကောင်ကိုဘမ်း🤣🤣🤣")
    elif "ဆွေး" in text:
        bot.reply_to(message, "အေးကွာရေစက်တေလဲကုန်ပြီထင်ပါတယ်😭😭😭")
    elif "စမ"  in text:
        bot.reply_to(message, "ပြန်စလိုက်လို့")
    elif "ပြေး" in text:
        bot.reply_to(message, "လိုက်မယ်နော်")
    elif "ဖင်" in text:
        bot.reply_to(message, "ဆီဗူးယူခဲ့")
    elif "win" in text:
        bot.send_sticker(message.chat.id, "CAACAgUAAxkBAAICFmj348VPRDJGonl1OmTpB_jkxwbsAAISGAACZSPoVij3kkk-qYD6NgQ")
    elif "ထုတ်လိုက်"  in text:
        bot.send_sticker(message.chat.id, "CAACAgUAAxkBAAICFWj347QV_9U8Yp9oO_nkaHyyQmK9AAJSHAACibABV_SCc5l5RzYnNgQ")
    elif "ပျော်တော"  in text:
        bot.send_sticker(message.chat.id, "CAACAgUAAxkBAAICG2j35IMIc0XhS4R4AoZBepycrPCtAAKoGgACP8iQV7-R-rUxpklqNgQ")
    elif "အေးဆေး"  in text:
        bot.send_sticker(message.chat.id, "CAACAgUAAxkBAAICW2j39ELiDEUzG_5kPiAxZRw6SpKiAAJOHQACXoURV9kmXOQOlnALNgQ")
    elif "ချစ်စ"  in text:
        bot.send_sticker(message.chat.id, "CAACAgUAAxkBAAICdGj3-Tfit6vj-IToqGrmD75dbKjSAAINGwACz1rpVnEjtpQHRY8_NgQ")
    elif "စပ"  in text:
        bot.send_sticker(message.chat.id, "CAACAgUAAxkBAAICdmj3-lGGWb2hpVNgGv6E0g9CBVbDAAIQGwACcu1hV4k9cNgML5msNgQ")
    elif "lose"  in text:
        bot.send_sticker(message.chat.id, "CAACAgQAAxkBAAICV2j39CBUhKl91twKSitUCc_c4NapAALsFQAC3XowU7yjO8fCQjfgNgQ")
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
    WEBHOOK_URL = "https://electronic-dona.koyeb.app/webhook/bot"  # Change this
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=5000)


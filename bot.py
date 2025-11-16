import telebot
from flask import Flask, request
import os

# ==============================
# CONFIG (Fill only 2 things)
# ==============================
TOKEN = "8253001112:AAE51vOORcdJCYMWz6L340goOu9ElpkhtuM"
CHAT_ID = "@shine49034000"
APP_URL = "https://electronic-dona.koyeb.app/webhook"
# ==============================

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)


# ==============================
# BOT HANDLERS
# ==============================
@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, "🔥 Bot is now running on Koyeb Webhook!\nSend JSON API to /send_bot")


# ==============================
# API (Your HTML/JS will POST here)
# ==============================
@app.route('/send_bot', methods=['POST'])
def send_bot():
    data = request.json

    # Incoming data from your prediction script
    period = data.get("period", "Unknown")
    prediction = data.get("prediction", "No Prediction")
    next_result = data.get("next_result", "No Result Yet")
    status = data.get("status", "-")

    # Final message format
    msg = (
        f"🎯 Period: {period}\n"
        f"📌 Prediction: {prediction}\n"
        f"📊 Next Round Result: {next_result}\n"
        f"🏆 Status: {status}"
    )

    bot.send_message(CHAT_ID, msg)
    return {"status": "sent"}


# ==============================
# WEBHOOK ENDPOINT
# ==============================
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.data.decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200


# ==============================
# HEALTH CHECK
# ==============================
@app.route('/')
def home():
    return "BOT OK", 200


# ==============================
# START
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))

    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)

    app.run(host="0.0.0.0", port=port)


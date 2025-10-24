import telebot
import time
from datetime import datetime

TOKEN = "8253001112:AAE51vOORcdJCYMWz6L340goOu9ElpkhtuM"
CHAT_ID = "@sla222299008"
bot = telebot.TeleBot(TOKEN)

pattern = ["Big","Big","Small","Big","Big","Big","Small","Small","Small","Small",
           "Big","Small","Big","Big","Small","Big","Small","Big","Small"]

step = 0

def wait_until_next_minute():
    # စက္ကန့် ၆၀ ပြည့်အောင် စောင့်
    now = datetime.now()
    wait_time = 60 - now.second
    time.sleep(wait_time)

def send_formula():
    global step
    while True:
        current = pattern[step % len(pattern)]
        message = f"💎 FORMULA: {current}\n⏱ Next in 60s"
        try:
            bot.send_message(CHAT_ID, message)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent: {current}")
        except Exception as e:
            print("Error:", e)
        step += 1
        wait_until_next_minute()  # မိနစ်ပြည့်တိုင်းပို့

if __name__ == "__main__":
    bot.send_message(CHAT_ID, "✅ TRX VIP SIGNAL Bot Started! 🔥")
    print("Bot started.")
    wait_until_next_minute()
    send_formula()

import telebot
import requests
import threading
import time
import schedule
import os
from dotenv import load_dotenv

load_dotenv()

# === LINE-BY-LINE EXPLANATION BELOW ===
TOKEN = os.getenv("TELEGRAM_TOKEN")      # ← Replace with your real token
bot = telebot.TeleBot(TOKEN)       # Creates the bot object that knows how to talk to Telegram

@bot.message_handler(commands=['start'])   
def send_welcome(message):
    bot.reply_to(message, "Hello! I'm Lucy,your Web3 price bot. Type /price to get Bitcoin price or /help for commands.")

@bot.message_handler(commands=['price'])
def send_price(message):
    parts = message.text.split()
    coin_id = parts[1].lower() if len(parts) > 1 else "bitcoin"

    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids":coin_id,
            "vs_currencies":"usd",
            "include_24hr_change":"true"
        }
        response = requests.get(url,params = params)
        data = response.json()

        if coin_id in data:
            price = data[coin_id]["usd"]
            change = data[coin_id].get("usd_24h_change",0)
            emoji =  "🟢" if change > 0 else "🔴"
            reply = f"{emoji} {coin_id.upper()} Price:${price:,.2f}\n24h change:{change:.2f}%"
        else:
            reply = f"Coin {coin_id} not found. Use CoinGeckoo ID"
    
    except Exception as e:
        reply = "API error."
    
    bot.reply_to(message,reply)

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Commands:\n/start\n/price\n/price ethereum\n/myid (for push later)")


subscribers = []

@bot.message_handler(commands=['subscribe'])
def subscribe(message):
    chat_id = message.chat.id
    if chat_id not in subscribers:
        subscribers.append(chat_id)
        bot.reply_to(message, "You are now subscribed to 5 minutes BTC price pushes!")
    else:
        bot.reply_to(message,"You are already subscribed.")
    
@bot.message_handler(commands=['myid'])
def show_id(message):
    bot.reply_to(message,f"Your chat ID:{message.chat.id} (copy this if needed)")

def price_push_job():
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd")
        price = r.json()["bitcoin"]["usd"]
        for chat_id in subscribers:
            bot.send_message(chat_id,f"BTC Price Push: ${price:,.2f}")
    except:
        pass

def run_scheduler():
    schedule.every(5).minutes.do(price_push_job)
    while True:
        schedule.run_pending()
        time.sleep(1)

threading.Thread(target=run_scheduler, daemon=True).start()

# This line starts the bot listening forever
bot.polling()



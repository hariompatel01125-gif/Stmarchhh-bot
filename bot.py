import os
import asyncio
import requests
import logging
from flask import Flask
from threading import Thread
from urllib.parse import urlparse, parse_qs
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Logging setup
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# --- CONFIG ---
TOKEN = "8625643695:AAE7aQf1cNFaY3EKj07eQqM4e-26d-ZA12Q"
POSTBACK_BASE = "https://tracker.o18a.com/p?o=21906348&m=25824&a=749661"

# Flask Server
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT LOGIC ---
async def fire_hit(url):
    try:
        # requests.get block kar sakta hai, isliye chhota timeout rakha hai
        res = requests.get(url, timeout=5)
        return res.status_code
    except:
        return "Error"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    logging.info(f"Received URL: {user_msg}")
    
    parsed_url = urlparse(user_msg)
    params = parse_qs(parsed_url.query)
    click_id = params.get('clickid', [None])[0]

    if not click_id:
        await update.message.reply_text("❌ ClickID nahi mila!")
        return

    await update.message.reply_text(f"🚀 ClickID: {click_id}\nInitial hit bhej raha hoon...")
    
    # 1. Initial Hit
    await fire_hit(f"{POSTBACK_BASE}&tid={click_id}")
    
    # 2. 4 Minute Wait
    logging.info(f"Waiting 4 mins for {click_id}")
    await asyncio.sleep(240)

    # 3. Final Events
    e1 = f"{POSTBACK_BASE}&tid={click_id}&event=login_successful"
    e2 = f"{POSTBACK_BASE}&tid={click_id}&event=trial_payment_successful"
    
    await fire_hit(e1)
    await fire_hit(e2)

    await update.message.reply_text(f"✅ Done! Events sent for {click_id}")

if __name__ == '__main__':
    # Start Flask in background
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

    # Start Telegram Bot
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot starting polling...")
    application.run_polling()

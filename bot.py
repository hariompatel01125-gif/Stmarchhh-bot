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

# Flask server Render ki port binding ke liye
app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive!"

def run_flask():
    # Render hamesha PORT environment variable deta hai
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- BOT LOGIC ---
async def fire_hit(url):
    try:
        res = requests.get(url, timeout=10)
        return res.status_code
    except Exception as e:
        return str(e)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    parsed_url = urlparse(user_msg)
    params = parse_qs(parsed_url.query)
    click_id = params.get('clickid', [None])[0]

    if not click_id:
        await update.message.reply_text("❌ Link mein clickid nahi mila!")
        return

    await update.message.reply_text(f"🚀 ID: {click_id}\nInitial hit bhej raha hoon...")
    
    # 1. Initial Hit
    await fire_hit(f"{POSTBACK_BASE}&tid={click_id}")
    
    # 2. Wait 4 Minutes
    await asyncio.sleep(240)

    # 3. Final Events
    e1 = f"{POSTBACK_BASE}&tid={click_id}&event=login_successful"
    e2 = f"{POSTBACK_BASE}&tid={click_id}&event=trial_payment_successful"
    
    await fire_hit(e1)
    await fire_hit(e2)

    await update.message.reply_text(f"✅ Done for: {click_id}\nEvents: Login & Trial Sent.")

if __name__ == '__main__':
    # Flask ko alag thread mein chalayein
    t = Thread(target=run_flask)
    t.start()

    # Telegram Bot start karein
    bot_app = ApplicationBuilder().token(TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    bot_app.run_polling()
  

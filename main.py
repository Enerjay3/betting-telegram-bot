import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from supabase import create_client, Client

# Environment Variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Initialize Flask
app = Flask(__name__)

# Initialize Supabase
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Telegram App
telegram_app = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context):
    await update.message.reply_text("Welcome! Your bot is alive on PythonAnywhere!")

telegram_app.add_handler(CommandHandler("start", start))

# Helper function to initialize and process updates cleanly
async def process_telegram_update(update_json):
    async with telegram_app:
        await telegram_app.initialize()
        update = Update.de_json(update_json, telegram_app.bot)
        await telegram_app.process_update(update)

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        update_json = request.get_json(force=True)
        asyncio.run(process_telegram_update(update_json))
        return "ok", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot server is active!", 200

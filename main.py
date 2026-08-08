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

# Initialize Supabase (Optional)
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Telegram App
telegram_app = ApplicationBuilder().token(TOKEN).build()

async def start(update: Update, context):
    user = update.effective_user
    await update.message.reply_text(f"Welcome {user.first_name}! Your bot is alive on PythonAnywhere!")

telegram_app.add_handler(CommandHandler("start", start))

@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == "POST":
        asyncio.run(telegram_app.process_update(
            Update.de_json(request.get_json(force=True), telegram_app.bot)
        ))
        return "ok", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot server is active!", 200

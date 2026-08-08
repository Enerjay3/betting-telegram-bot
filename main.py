import os
import asyncio
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler
from supabase import create_client, Client

# Environment Variables
TOKEN = os.environ.get("TELEGRAM_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

app = Flask(__name__)

# Initialize Supabase
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Telegram App
telegram_app = ApplicationBuilder().token(TOKEN).build()

# Helper: Save/Update User in Supabase
def sync_user(user):
    if not supabase:
        return
    try:
        # Insert user if new, keep existing balance if already registered
        data = {
            "telegram_id": user.id,
            "first_name": user.first_name,
            "username": user.username or ""
        }
        supabase.table("users").upsert(data, on_conflict="telegram_id").execute()
    except Exception as e:
        print(f"Supabase Sync Error: {e}")

# Helper: Get User Balance
def get_balance(telegram_id):
    if not supabase:
        return 100.00
    try:
        res = supabase.table("users").select("balance").eq("telegram_id", telegram_id).execute()
        if res.data:
            return res.data[0]["balance"]
    except Exception as e:
        print(f"Fetch Balance Error: {e}")
    return 100.00

# /start Command
async def start(update: Update, context):
    user = update.effective_user
    sync_user(user)
    
    keyboard = [
        [InlineKeyboardButton("⚽ View Matches", callback_data="matches")],
        [InlineKeyboardButton("💰 Check Balance", callback_data="balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🔥 Welcome {user.first_name}! Your account is active.\n\nChoose an option below:",
        reply_markup=reply_markup
    )

# Inline Button Click Handlers
async def button_handler(update: Update, context):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "balance":
        bal = get_balance(user_id)
        await query.message.reply_text(f"💰 Your current balance is: ${bal:.2f}")
    elif query.data == "matches":
        await query.message.reply_text("⚽ Available Matches:\n\n1. Man City vs Arsenal (1.85 / 2.10)\n2. Real Madrid vs Barcelona (1.95 / 1.95)")

telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CallbackQueryHandler(button_handler))

# Webhook Processing
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

import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from supabase import create_client, Client

# Logging setup
logging.basicConfig(level=logging.INFO)

# Environment Variables
TOKEN = os.environ.get'8739563374:AAH0rwMiRn43jntdN3P6f27fyMp_ONtVfk0'
SUPABASE_URL = os.environ.get'https://vsdkhczvjrrnjbmtjhxx.supabase.co'
SUPABASE_KEY = os.environ.get'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZzZGtoY3p2anJybmpibXRqaHh4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI5NDM2MjYsImV4cCI6MjA5ODUxOTYyNn0.6P2aMs7jCm71GNKkfHBCC_QOi5_YBqfQoNNfoZTwqQ8'

# Initialize Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(f"Welcome {user.first_name}! Your betting bot is officially alive.")

if __name__ == "__main__":
    if not TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable is missing!")
    
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    print("Bot is polling...")
    app.run_polling()

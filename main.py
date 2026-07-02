import os
import requests
from flask import Flask, request, jsonify
from supabase import create_client, Client

app = Flask(__name__)

TOKEN = os.environ.get("TELEGRAM_TOKEN")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/", methods=["GET"])
def home():
    return "Bot server is fully awake!", 200

@app.route("/webhook", methods=["POST"])
def telegram_webhook():
    update = request.get_json(force=True)
    
    # 1. HANDLE CONVERSATIONS / MESSAGES
    if "message" in update and "text" in update["message"]:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        username = message["chat"].get("username", "Unknown")

        if text == "/start":
            get_or_create_user(chat_id, username)
            msg = "⚽ Welcome to the AI Betting Predictor!\n\n👉 Use /predict to get value tips.\n👉 Use /upgrade to unlock Premium tier."
            send_message(chat_id, msg)
            return jsonify({"status": "ok"})

        elif text == "/upgrade":
            invoice_url = f"{BASE_URL}/sendInvoice"
            payload = {
                "chat_id": chat_id,
                "title": "👑 Premium Pass",
                "description": "Unlock unlimited daily algorithmic value betting tips for 30 days.",
                "payload": f"premium_user_{chat_id}",
                "currency": "XTR", 
                "prices": [{"label": "30 Days Premium Access", "amount": 50}] 
            }
            requests.post(invoice_url, json=payload)
            return jsonify({"status": "ok"})

        elif text == "/predict":
            user = get_or_create_user(chat_id, username)
            
            if user["is_premium"]:
                send_prediction(chat_id, premium=True)
                return jsonify({"status": "ok"})
            else:
                if user["free_uses_today"] >= 2:
                    msg = "❌ Limit reached! You used your 2 free daily tips.\n\nUnlock unlimited predictions instantly via /upgrade"
                    send_message(chat_id, msg)
                    return jsonify({"status": "ok"})
                else:
                    new_count = user["free_uses_today"] + 1
                    supabase.table("users").update({"free_uses_today": new_count}).eq("user_id", chat_id).execute()
                    send_prediction(chat_id, premium=False)
                    return jsonify({"status": "ok"})

    # 2. APPROVE CHECKOUT COMMAND FROM TELEGRAM
    elif "pre_checkout_query" in update:
        query_id = update["pre_checkout_query"]["id"]
        requests.post(f"{BASE_URL}/answerPrecheckoutQuery", json={"pre_checkout_query_id": query_id, "ok": True})
        return jsonify({"status": "ok"})

    # 3. VERIFY SUCCESSFUL PAYMENT (TELEGRAM STARS)
    elif "message" in update and "successful_payment" in update["message"]:
        chat_id = update["message"]["chat"]["id"]
        supabase.table("users").update({"is_premium": True}).eq("user_id", chat_id).execute()
        send_message(chat_id, "👑 Profile upgraded to Premium! You now have unlimited server predictions.")
        return jsonify({"status": "ok"})

    return jsonify({"status": "ignored"})

def get_or_create_user(user_id, username):
    response = supabase.table("users").select("*").eq("user_id", user_id).execute()
    if len(response.data) == 0:
        new_user = {"user_id": user_id, "username": username, "is_premium": False, "free_uses_today": 0}
        supabase.table("users").insert(new_user).execute()
        return new_user
    return response.data[0]

def send_message(chat_id, text):
    requests.post(f"{BASE_URL}/sendMessage", json={"chat_id": chat_id, "text": text})

def send_prediction(chat_id, premium):
    tier = "👑 [PREMIUM TIP]" if premium else "⚽ [FREE SELECTION]"
    msg = f"{tier}\nMatch: Real Madrid vs Man City\nPrediction: Over 2.5 Goals\nOdds: 1.80"
    send_message(chat_id, msg)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

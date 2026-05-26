import os
import requests
import logging

from dotenv import load_dotenv
import os

load_dotenv()

token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(text):
    try:
        requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=5
        )
    except Exception:
        logging.exception("[TELEGRAM ERROR] failed to send alert")



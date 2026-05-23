import os
import requests
from dotenv import load_dotenv
import logging
load_dotenv()
import httpx

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID")


def send_whatsapp_message(number: str, text: str):
    url = f"https://graph.facebook.com/v20.0/{META_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    body = {
        "messaging_product": "whatsapp",
        "to": number,
        "type": "text",
        "text": {
            "body": text
        }
    }

    response = requests.post(url, headers=headers, json=body)

    print("WHATSAPP STATUS:", response.status_code)
    print("WHATSAPP RESPONSE:", response.text)

    return response




def send_whatsapp_buttons(to, body, buttons):
    url = f"https://graph.facebook.com/v20.0/{META_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": body
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": btn["id"],
                            "title": btn["title"]
                        }
                    }
                    for btn in buttons
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print("WHATSAPP BUTTON STATUS:", response.status_code, flush=True)
    print("WHATSAPP BUTTON RESPONSE:", response.text, flush=True)

    return response




def send_whatsapp_list(to, body, button_label, sections):
    url = f"https://graph.facebook.com/v20.0/{META_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": body
            },
            "action": {
                "button": button_label,
                "sections": [
                    {
                        # מייצרים קטגוריה אחת רציפה ללא כותרת, ולוקחים את הנתונים ישירות מהמערך שלך
                        "rows": [
                            {
                                "id": item["id"],
                                "title": item["title"]
                            }
                            for item in sections
                        ]
                    }
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print("WHATSAPP LIST STATUS:", response.status_code, flush=True)
    print("WHATSAPP LIST RESPONSE:", response.text, flush=True)

    return response





async def send_typing_indicator(message_id: str, phone: str):
    url = f"https://graph.facebook.com/v19.0/{META_PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    
    payload_read = {
        "messaging_product": "whatsapp",
        "status": "read",
        "message_id": message_id
    }
    
    # 2. בקשה שנייה - הפעלת אינדיקטור ההקלדה
    payload_typing = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,  # בוואטסאפ של מטא, שליחת ה-typing מתבצעת מול ה-message_id או ה-Phone בהתאם לגרסת ה-API, בקוד המקורי השתמשת ב-message_id ולכן נשאר איתו
        "typing_indicator": {"type": "text"}
    }
    
    async with httpx.AsyncClient() as client:
        # שולחים קודם את ה-Read ומחכים שיסתיים
        await client.post(url, headers=headers, json=payload_read)
        # רק אחרי שה-Read הסתיים, שולחים את ה-Typing
        response = await client.post(url, headers=headers, json=payload_typing)











def extract_whatsapp_message_data(body):
    remote_jid = body["data"]["key"].get("remoteJidAlt") or body["data"]["key"].get("remoteJid")
    phone = remote_jid.split("@")[0]

    name = body["data"]["pushName"]

    message = body["data"].get("message", {})
    text = message.get("conversation") or message.get("extendedTextMessage", {}).get("text", "")

    message_id = body["data"]["key"]["id"]

    from_me = body["data"]["key"]["fromMe"]

    message_type = body["data"]["messageType"]

    return {
        "phone" : phone , 
        "name" : name , 
        "text" : text , 
        "message_id" : message_id , 
        "from_me" : from_me ,
        "message_type" : message_type
    }







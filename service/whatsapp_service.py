import os
import requests
from dotenv import load_dotenv

load_dotenv()

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
                        "title": section["title"],
                        "rows": [
                            {
                                "id": row["id"],
                                "title": row["title"],
                                "description": row.get("description", "")
                            }
                            for row in section["rows"]
                        ]
                    }
                    for section in sections
                ]
            }
        }
    }

    response = requests.post(url, headers=headers, json=payload)

    print("WHATSAPP LIST STATUS:", response.status_code, flush=True)
    print("WHATSAPP LIST RESPONSE:", response.text, flush=True)

    return response
















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







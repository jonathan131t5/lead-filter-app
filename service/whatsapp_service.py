import os
import requests
from dotenv import load_dotenv

load_dotenv()

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")


def send_whatsapp_message(number: str, text: str):
    number = number.replace("@s.whatsapp.net", "")
    
    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE_NAME}"

    headers = {
        "apikey": EVOLUTION_API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "number": number,
        "text": text
    }

    response = requests.post(url, headers=headers, json=body)

    print("WHATSAPP STATUS:", response.status_code)
    print("WHATSAPP RESPONSE:", response.text)

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







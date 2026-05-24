from fastapi import FastAPI, Request, BackgroundTasks , Response
from pydantic import BaseModel
from service.service_english_w import ServiceLayer
from data_access.slots_repository import BookingSlotRepository
import time
import asyncio

import uuid
import sqlite3
import logging
from fastapi.middleware.cors import CORSMiddleware

from service.whatsapp_service import send_whatsapp_message , send_whatsapp_buttons , send_whatsapp_list , send_typing_indicator
from data_access.lead_booking_dashboard_repository import BookingDashDataRepository

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

service_layer = ServiceLayer()
booking_dashboard = BookingDashDataRepository()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://192.168.1.36:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def serve_chat():
    return FileResponse("chat_english.html")


@app.get("/dashboard")
def serve_dashboard():
    return FileResponse("dashboard-v2.html")

class MessageRequirements(BaseModel):
    name: str | None = None
    content: dict | str | None = None
    

@app.post("/message")
def run_message_flow(
    data: MessageRequirements,
    request: Request,
    response: Response
):

    session_id = request.cookies.get("session_id")

    if session_id is None:
        session_id = str(uuid.uuid4())
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            samesite="lax"
        )

    result = service_layer.process_lead_message(
        session_id=session_id,
        name=data.name,
        content=data.content
    )

    return {
        "content": result.get("message") or result.get("content"),
        "message": result.get("message") or result.get("content"),
        "status": result.get("status", "error")
        }


    


@app.get("/api/dashboard/leads")
def get_dashboard_leads():
    return service_layer.leads_data.get_all_leads_data()


@app.get("/api/dashboard/leads/{lead_id}/messages")
def get_dasboard_messages(lead_id: int):
    return service_layer.messages.get_lead_messages(lead_id=lead_id)


@app.get("/api/dashboard/appointments")
def get_dashboard_appointments():
    return service_layer.booking_dashboard.get_all_appointments()


class AppointmentUpdateRequest(BaseModel):
    name: str
    phone: str
    email: str
    slot_date: str
    booking_status: str

@app.put("/api/dashboard/appointments/{appointment_id}")
def update_dashboard_appointment(appointment_id: int, data: AppointmentUpdateRequest):
    result = service_layer.update_appointment(
        appointment_id=appointment_id,
        name=data.name,
        phone=data.phone,
        email=data.email,
        slot_date=data.slot_date,
        booking_status=data.booking_status
    )

    return {
        "message": result.get("message"),
        "status": result.get("status", "error")
    }


@app.get("/privacy")
def privacy():
    return FileResponse("privacy.html")



@app.get("/dev/create-test-slots")
def create_test_slots():
    booking_repo = service_layer.booking_flow.booking_slots
    booking_repo.create_booking_table()
    booking_repo.create_booking_slot("2026-05-10 18:00")
    booking_repo.create_booking_slot("2026-05-10 19:00")
    booking_repo.create_booking_slot("2026-05-11 10:00")
    service_layer.booking_flow.db.commit()
    return {"status": "ok", "message": "test slots created"}



VERIFY_TOKEN = "lead_filter_verify_123"



@app.get("/webhook/whatsapp")
async def verify_whatsapp_webhook(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)

    return {"status": "verification_failed"}






@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request, background_tasks: BackgroundTasks):
    try:
        webhook_start = time.time()
        body = await request.json()
        
        value = body["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return {"status": "ignored"}
        
        logging.info(f"[WEBHOOK] received timestamp={body['entry'][0]['changes'][0]['value']['messages'][0].get('timestamp')}_server={int(time.time())}")
        
        if value["messages"][0].get("from") is None:
            return {"status": "ignored"}

        message = value["messages"][0]
        phone = message["from"]

        # 1. שליחה מיידית וסינכרונית (חובה שזה יקרה לפני ה-return)
        # זה מבטיח שוואטסאפ תקבל את פקודת ההקלדה לפני שהחיבור נסגר
        
        typing_start = time.time()
        await send_typing_indicator(message_id=message["id"], phone=phone)
        logging.info(f"[TIMER] typing_send={time.time()-typing_start:.2f}s")
        background_tasks.add_task(run_ai_logic, message)
        
        logging.info(f"[TIMER] webhook_total={time.time()-webhook_start:.2f}s")
        return {"status": "ok"}
        
    except Exception:
        logging.exception("WEBHOOK ERROR")
        return {"status": "error"}


processed_messages = set()

async def run_ai_logic(message: dict):
    try:

        phone = message["from"]
        message_id = message["id"]

        if message_id in processed_messages:
            return
        processed_messages.add(message_id)



        
        
        # עיבוד סוג ההודעה
        if message.get("type") == "text":
            text = message["text"]["body"]
        elif message.get("type") == "interactive":
            int_data = message["interactive"]
            text = {"id": int_data.get("button_reply", {}).get("id") or int_data.get("list_reply", {}).get("id")}
        else:
            return
        
        if text == "testfast":
            await send_whatsapp_message(phone, "test")
            return

        start = time.time()

        result = await asyncio.to_thread(
            service_layer.process_lead_message,
            session_id=phone,
            content=text,
            external_message_id=message_id
        )


        logging.info(f"[TIMER] total={time.time()-start:.2f}s")
        # שליחת התשובה
        reply_text = result.get("message") or result.get("content")
        reply_status = result.get("status")
        
        if reply_text:
            send_start = time.time()
            if reply_status in ["booking_interest", "booking_selection"]:
                if len(reply_text.get("buttons", [])) < 3:
                    await send_whatsapp_buttons(body=reply_text["body"], buttons=reply_text["buttons"], to=phone)
                else:
                    await send_whatsapp_list(body=reply_text["body"], button_label=reply_text["button_label"], sections=reply_text["buttons"], to=phone)
            else:
               await send_whatsapp_message(phone, reply_text)
            
            logging.info(f"[TIMER] whatsapp_reply_send={time.time()-send_start:.2f}s")
    except Exception:
        logging.exception("AI PROCESSING ERROR")










@app.get("/business")
def home():
    return FileResponse("business-web.html")
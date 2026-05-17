from fastapi import FastAPI
from pydantic import BaseModel
from service.service_english import ServiceLayer
from data_access.slots_repository import BookingSlotRepository
from fastapi import Request, Response
import uuid
import sqlite3
import logging
from fastapi.middleware.cors import CORSMiddleware

from service.whatsapp_service import send_whatsapp_message , extract_whatsapp_message_data

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

service_layer = ServiceLayer()

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


@app.get("/dev/create-test-slots")
def create_test_slots():
    booking_repo = service_layer.booking_flow.booking_slots
    booking_repo.create_booking_table()
    booking_repo.create_booking_slot("2026-05-10 18:00")
    booking_repo.create_booking_slot("2026-05-10 19:00")
    booking_repo.create_booking_slot("2026-05-11 10:00")
    service_layer.booking_flow.db.commit()
    return {"status": "ok", "message": "test slots created"}



@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    body = await request.json()

    if body.get("event") != "messages.upsert":
        return {"status": "ignored"}

    logging.info("WHATSAPP WEBHOOK BODY:")
    logging.info(body)

    message_data = extract_whatsapp_message_data(body)

    if message_data["from_me"]:
        return {"status": "ignored"}

    if message_data["message_type"] != "conversation":
        send_whatsapp_message(
            message_data["phone"],
            "I can only read text messages here. Please type your message and I’ll help you from there."
        )
        return {"status": "ok"}
    
    
    result = service_layer.process_lead_message(
        session_id=message_data["phone"],
        content=message_data["text"] , 
        external_message_id=message_data["message_type"]
    )

    send_whatsapp_message(
        message_data["phone"],
        result.get("message") or result.get("content")
    )

    return {"status": "ok"}



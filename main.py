from fastapi import FastAPI, Request, BackgroundTasks , Response
from pydantic import BaseModel
from service.service_english_w import ServiceLayer

import time
import asyncio

import uuid
import sqlite3
import logging
from fastapi.middleware.cors import CORSMiddleware

from service.whatsapp_service import send_whatsapp_message , send_whatsapp_buttons , send_whatsapp_list , send_typing_indicator

from integrations.telegram_bot import send_telegram_alert

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
    return FileResponse("dashboard_english.html")

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
    slot_date: str
    booking_status: str

@app.put("/api/dashboard/appointments/{appointment_id}")
def update_dashboard_appointment(appointment_id: int, data: AppointmentUpdateRequest):
    result = service_layer.appointments.update_appointment(
        appointment_id=appointment_id,
        name=data.name,
        phone=data.phone,
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



@app.get("/dev/create-demo-data")
def create_demo_data():
    db = service_layer.booking_flow.db
    cursor = db.cursor

    demo_slots = [
        "2026-05-25 10:00",
        "2026-05-25 14:00",
        "2026-05-26 11:00",
        "2026-05-27 16:00",
        "2026-05-28 09:30",
    ]

    created_slots = []

    for slot_date in demo_slots:
        cursor.execute(
            "INSERT INTO booking_slot (date, is_taken) VALUES (?, ?)",
            (slot_date, 0)
        )
        created_slots.append(cursor.lastrowid)
    db.commit()
    return {"status": "ok", "created_slots": created_slots}
    


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
        phone = None

        webhook_start = time.time()
        body = await request.json()
        
        value = body["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            logging.info(f"[WHATSAPP VALUE] {value}")
            return {"status": "ignored"}
        
        logging.info(f"[WEBHOOK] received timestamp={body['entry'][0]['changes'][0]['value']['messages'][0].get('timestamp')}_server={int(time.time())}")
        
        if value["messages"][0].get("from") is None:
            return {"status": "ignored"}

        message = value["messages"][0]
        phone = message["from"]

        processing_check = service_layer.leads_states.get_lead_is_processing_param(session_id=phone)
        logging.info(f"[PROCESSING CHECK] phone={phone} value={processing_check}")
        if processing_check == 1:
            return {"status" : "ok"}
        
        if processing_check is None or processing_check == 0:
            service_layer.leads_states.update_lead_is_processing(session_id=phone , value=1)
            typing_start = time.time()
            await send_typing_indicator(message_id=message["id"], phone=phone)
            logging.info(f"[TIMER] typing_send={time.time()-typing_start:.2f}s")
            background_tasks.add_task(run_ai_logic, message)
            
            logging.info(f"[TIMER] webhook_total={time.time()-webhook_start:.2f}s")
            return {"status": "ok"}
        
    except Exception as e:  
        logging.exception("WEBHOOK ERROR")
        
        send_telegram_alert(
        f"🚨 WEBHOOK ERROR\n"
        f"phone={phone}\n"
        f"error={type(e).__name__}: {e}"
        )
        
        if phone:
            send_whatsapp_message(number=phone , text="Something went wrong. Please try again in a moment.")
        
        return {"status": "error"}


processed_messages = set()

async def run_ai_logic(message: dict):
    phone = None
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
            if reply_status in ["pre_flow" , "booking_interest", "booking_selection"]:
                if len(reply_text.get("buttons", [])) < 3:
                    await send_whatsapp_buttons(body=reply_text["body"], buttons=reply_text["buttons"], to=phone)
                else:
                    await send_whatsapp_list(body=reply_text["body"], button_label=reply_text["button_label"], sections=reply_text["buttons"], to=phone)
            else:
               await send_whatsapp_message(phone, reply_text)

            logging.info(f"[TIMER] whatsapp_reply_send={time.time()-send_start:.2f}s")
    except Exception as e:
        logging.exception(f"[WHATSAPP PROCESSING ERROR] phone={phone}")

        send_telegram_alert(
            f"🚨 WHATSAPP PROCESSING ERROR\n"
            f"phone={phone}\n"
            f"error={type(e).__name__}: {e}"
            )
    
    finally:
        if phone:
            service_layer.leads_states.update_lead_is_processing(session_id=phone , value=0)










@app.get("/business")
def home():
    return FileResponse("business-web.html")














#def backup():
    demo_leads = [
            ("Jake", "0521111111", "I want to be fit", "like 2 months", "Cold Lead", 3),
            ("Brandon", "0525586823", "I want more clients", "In a few months", "Cold Lead", 4),
            ("Michael", "0523687333", "I want to scale my online coaching business", "Next week", "Hot Lead", 6),
            ("Emily", "0524423644", "I want better lead follow-up", "As soon as possible", "Hot Lead", 7),
            ("Jason", "0525551255", "Still checking options", "Not sure yet", "pending", 2),
        ]

    created_leads = []

    for name, phone, goal, urgency, final_status, total_score in demo_leads:
        cursor.execute("""
            INSERT INTO leads_data (
                session_id,
                name,
                phone_number,
                final_status,
                summary,
                last_interaction_at
            )
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            None,
            name,
            phone,
            final_status,
            f"{name} — {final_status}\n\nGoal: {goal}\nTimeline: {urgency}\n\nScore: {total_score}\nPhone: {phone}"
        ))

        lead_id = cursor.lastrowid
        created_leads.append(lead_id)

        cursor.execute("""
            INSERT INTO leads_fields_data (
                lead_id,
                goal_user,
                urgency_user,
                phone_user,
                updated_at
            )
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (
            lead_id,
            goal,
            urgency,
            phone
        ))

        cursor.execute("""
            INSERT INTO leads_scores (
                lead_id,
                goal_score,
                phone_score,
                urgency_score,
                goal_status,
                urgency_status,
                score_count,
                total_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lead_id,
            0,
            1,
            0,
            "found",
            "found",
            2,
            total_score
        ))

        cursor.execute("""
            INSERT INTO lead_conversation_states (
                lead_id,
                current_field,
                last_interaction_at
            )
            VALUES (?, ?, CURRENT_TIMESTAMP)
        """, (
            lead_id,
            "done"
        ))

        cursor.execute("""
            INSERT INTO leads_booking (
                lead_id,
                booking_eligible,
                has_booking,
                booking_state
            )
            VALUES (?, ?, ?, ?)
        """, (
            lead_id,
            1 if final_status == "Hot Lead" else 0,
            0,
            "booking_interest"
        ))

    demo_appointments = [
        (created_leads[2], created_slots[0], "confirmed"),
        (created_leads[3], created_slots[1], "completed"),
        (created_leads[0], created_slots[2], "cancelled"),
    ]

    for lead_id, slot_id, status in demo_appointments:
        cursor.execute("""
            INSERT INTO appointment (
                lead_id,
                slot_id,
                status
            )
            VALUES (?, ?, ?)
        """, (
            lead_id,
            slot_id,
            status
        ))

        cursor.execute("""
            UPDATE booking_slot
            SET is_taken = 1
            WHERE slot_id = ?
        """, (slot_id,))

        cursor.execute("""
            UPDATE leads_booking
            SET has_booking = 1
            WHERE lead_id = ?
        """, (lead_id,))

    db.commit()

    return {
        "status": "ok",
        "message": "demo data created",
        "leads_created": len(created_leads),
        "slots_created": len(created_slots),
        "appointments_created": len(demo_appointments)
    }

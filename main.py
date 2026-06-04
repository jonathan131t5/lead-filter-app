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

@app.get("/j")
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

@app.get("/api/dashboard/slots")
def get_dashboard_slots():
    return service_layer.booking_flow.booking_slots.get_all_slots()


@app.put("/api/dashboard/slots/{slot_id}/cancel")
def cancel_slot(slot_id: int):
    service_layer.booking_flow.booking_slots.cancel_booking_slot(slot_id=slot_id)


@app.put("/api/dashboard/slots/{slot_id}/restore")
def restore_slot(slot_id: int):
    service_layer.booking_flow.booking_slots.restore_slot(slot_id=slot_id)


class SlotRequest(BaseModel):
    date: str

@app.post("/api/dashboard/slots/create")
def create_dashboard_slot(data: SlotRequest):
    result = service_layer.booking_flow.booking_slots.create_booking_slot(
        date=data.date
        )
    
    return {
        "message" : result.get("message") , 
        "status" : result.get("status" , "error")
    }


@app.put("/api/dashboard/slots/{slot_id}/update")
def update_dashboard_slot(slot_id: int, data: SlotRequest):
    result = service_layer.booking_flow.booking_slots.update_slot_date(
        slot_id=slot_id,
        date=data.date
    )

    return {
        "message" : result.get("message") , 
        "status" : result.get("status" , "error")
    }


class SlotWeeklyCreateRequest(BaseModel):
    slots_data: list[dict]
    weeks_num: int

@app.post("/api/dashboard/slots/create-weekly")
def create_weekly_slots(data: SlotWeeklyCreateRequest):
    result = service_layer.booking_flow.booking_slots.create_weekly_booking_slots(
        weeks_num=data.weeks_num , 
        slots_data=data.slots_data
    )

    
    return {
        "message" : result.get("message") , 
        "status" : result.get("status" , "error")
    }


class AppointmentUpdateRequest(BaseModel):
    name: str
    phone: str
    booking_status: str

@app.put("/api/dashboard/appointments/{appointment_id}")
def update_dashboard_appointment(appointment_id: int, data: AppointmentUpdateRequest):
    result = service_layer.appointments.update_appointment(
        appointment_id=appointment_id,
        name=data.name,
        phone=data.phone,
        booking_status=data.booking_status
    )

    return {
        "message": result.get("message"),
        "status": result.get("status", "error")
    }






@app.get("/privacy")
def privacy():
    return FileResponse("privacy.html")


@app.get("/dev/db-check")
def db_check():
    service_layer.db.cursor.execute("SELECT version()")
    return {"db": service_layer.db.cursor.fetchone()[0]}



@app.get("/dev/reset-session/{session_id}")
def reset_session(session_id: str):
    db = service_layer.db
    cursor = db.cursor

    cursor.execute("""
        SELECT lead_id
        FROM leads_data
        WHERE session_id = %s
    """, (session_id,))

    result = cursor.fetchone()

    if result is None:
        cursor.execute("""
            DELETE FROM lead_conversation_states
            WHERE session_id = %s
        """, (session_id,))

        db.commit()

        return {
            "status": "no_lead_found_but_state_deleted",
            "session_id": session_id
        }

    lead_id = result[0]

    cursor.execute("DELETE FROM appointment WHERE lead_id = %s", (lead_id,))
    cursor.execute("DELETE FROM leads_booking WHERE lead_id = %s", (lead_id,))
    cursor.execute("DELETE FROM leads_messages WHERE lead_id = %s", (lead_id,))
    cursor.execute("DELETE FROM leads_fields_data WHERE lead_id = %s", (lead_id,))
    cursor.execute("DELETE FROM leads_scores WHERE lead_id = %s", (lead_id,))

    cursor.execute("""
        DELETE FROM lead_conversation_states
        WHERE session_id = %s
    """, (session_id,))

    cursor.execute("""
        DELETE FROM leads_data
        WHERE session_id = %s
    """, (session_id,))

    db.commit()

    return {
        "status": "reset_done",
        "session_id": session_id,
        "lead_id": lead_id
    }


@app.get("/dev/create-demo-data3")
def create_demo_data():
    try:
        db = service_layer.booking_flow.db
        cursor = db.cursor

        demo_slots = [
            "2026-12-28 10:00",
            "2026-07-15 14:00",
            "2026-05-21 11:00",
            "2026-06-27 16:00",
            "2026-08-28 09:30",
        ]

        created_slots = []

        for slot_date in demo_slots:
            cursor.execute(
                "INSERT INTO booking_slot (date, is_taken) VALUES (%s , %s) RETURNING slot_id",
                (slot_date, 0)
            )
            created_slots.append(cursor.fetchone()[0])
        db.commit()
        return {"status": "ok", "created_slots": created_slots}

    except Exception:
        service_layer.db.rollback()
        raise



@app.get("/dev/clear-slots")
def clear_slots():
    db = service_layer.booking_flow.db
    cursor = db.cursor

    cursor.execute("DELETE FROM booking_slot")
    db.commit()

    return {"status": "ok", "message": "all slots deleted"}
    



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
        service_layer.db.rollback() 
        logging.exception("WEBHOOK ERROR")
        
        send_telegram_alert(
        f"🚨 WEBHOOK ERROR\n"
        f"phone={phone}\n"
        f"error={type(e).__name__}: {e}"
        )
        
        if phone:
            await send_whatsapp_message(number=phone , text="Something went wrong. Please try again in a moment.")
        
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
            send_start = time.time()
            await send_whatsapp_message(phone, "test")
            logging.info(f"[TIMER] testfast_whatsapp_send={time.time()-send_start:.2f}s")
            return

        start = time.time()
        print("TEXT RESULT:", text, flush=True)
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
        service_layer.db.rollback()
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

@app.get("/")
def landing_page():
    return FileResponse("landing_page.html")






@app.get("/api/dashboard/demo-create")
def create_demo_video_data():
    db = service_layer.db
    cursor = db.cursor

    try:
        demo_data = [
           ("John", "4458392016", "Hot Lead", "booked", "2026-07-10 10:00"),
           ("Michael", "4417285930", "Hot Lead", "completed", "2026-07-11 14:00"),
           ("Robert", "4490638172", "Cold Lead", "cancelled", "2026-07-12 09:30"),
           ("William", "4435019286", "Cold Lead", "booked", "2026-07-13 16:00"),
           ("James", "4472946501", "pending", "booked", "2026-07-14 11:00"),
           ]

        for name, phone, final_status, appointment_status, slot_date in demo_data:

            cursor.execute("""
                INSERT INTO leads_data (session_id, phone_number, final_status , name)
                VALUES (%s, %s, %s, %s)
                RETURNING lead_id
            """, (
                phone,
                phone,
                final_status,
                name
            ))

            lead_id = cursor.fetchone()[0]

            is_taken = 1
            if appointment_status == "cancelled":
                is_taken = 0
            
            cursor.execute("""
                INSERT INTO booking_slot (date, is_taken)
                VALUES (%s, %s)
                RETURNING slot_id
            """, (slot_date , is_taken))

            slot_id = cursor.fetchone()[0]

            if name != "James":
                cursor.execute("""
                    INSERT INTO appointment (slot_id, lead_id, status)
                    VALUES (%s, %s, %s)
                """, (
                    slot_id,
                    lead_id,
                    appointment_status
                ))

            db.commit()

        return {"status": True}

    except Exception as e:
        db.rollback()
        return {"status": False, "message": str(e)}
    



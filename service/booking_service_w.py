import random
from datetime import datetime
import logging

from output_builders.booking_questions_english import BookingQuestion

from data_access.postgres.lead_booking_repository import LeadsBookingRepository
from data_access.postgres.slots_repository import BookingSlotRepository
from data_access.postgres.appointment_repository import AppointmentRepository
from data_access.postgres.lead_booking_context_repository import LeadBookingContextRepository
from data_access.postgres.leads_messages_repository import MessagesRepository
from data_access.postgres.lead_booking_dashboard_repository import BookingDashDataRepository



from data_base.connection2 import Connection

class BookingFlow:
    def __init__(self, db):
        self.db = db
        self.booking_dash_data = BookingDashDataRepository(self.db.new_cursor())
        self.messages = MessagesRepository(self.db.new_cursor())
        self.leads_booking = LeadsBookingRepository(self.db.new_cursor())
        self.booking_slots = BookingSlotRepository(self.db.new_cursor())
        self.appointments = AppointmentRepository(self.db.new_cursor())
        self.booking_context = LeadBookingContextRepository(self.db.new_cursor())


    
    def process_booking_flow(self , lead_id , content):
        try:
            logging.info(f"[BOOKING] lead_id={lead_id} step=start content={content}")

            lead_booking_data = self.booking_context.prepare_lead_booking_context(lead_id=lead_id)
            
            check_booking_result = self.check_lead_booking(lead_data=lead_booking_data)
        
            if check_booking_result["status"] == "invaild flow":
                return False
            
            if check_booking_result["status"] == "has booking":
                self.db.commit()
                question = self.generate_booking_question(lead_data=lead_booking_data)
                self.messages.add_lead_message(lead_id=lead_booking_data["lead_id"] , role="assistant" , content=question["message"])
                return question

            
            elif check_booking_result["status"] == "not eligible":
                self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] , param="booking_state" , value="not eligible")
                lead_booking_data["booking_state"] = "not eligible"
                self.db.commit()
                question = self.generate_booking_question(lead_data=lead_booking_data)
                self.messages.add_lead_message(lead_id=lead_booking_data["lead_id"] , role="assistant" , content=question["message"])
                return question
                

            elif check_booking_result["status"] == True:
                logging.info(
                    f"[BOOKING] lead_id={lead_booking_data['lead_id']} "
                    f"step=response_received content={content}"
                    )
                process_result = self.process_booking_response_flow(response_info=content , lead_booking_data=lead_booking_data)
                if process_result and "status" in process_result:
                    self.db.commit()
                    return {"status" : process_result["status"] , "message" : process_result["message"]} 

            self.db.commit()
            question = self.generate_booking_question(lead_data=lead_booking_data)
            if isinstance(question , dict):
                self.messages.add_lead_message(lead_id=lead_booking_data["lead_id"] , role="assistant" , content=question["message"]["body"])
            else:
                self.messages.add_lead_message(lead_id=lead_booking_data["lead_id"] , role="assistant" , content=question["message"])
            return question
        
        except Exception:
            logging.exception(f"[BOOKING ERROR] lead_id={lead_id} step=process_booking_flow")
            self.db.rollback()
            raise
                

    
    def check_lead_booking(self , lead_data):
        if lead_data["final_status"] == "Hot Lead":
            if lead_data["has_booking"] == 0:
                self.leads_booking.set_booking_param(lead_id=lead_data["lead_id"] , param="booking_eligible" , value=1)
                lead_data["booking_eligible"] = 1
                return {"status" : True}
            
            return {"status" : "has booking"}
        
        elif lead_data["final_status"] == "pending":
            return {"status" : "invaild flow"}
        
        return {"status" : "not eligible"}
    


    
    def process_booking_response_flow(self , response_info , lead_booking_data):
        logging.info(
            f"[BOOKING] lead_id={lead_booking_data['lead_id']} "
            f"step=process_booking booking_state={lead_booking_data['booking_state']}"
            )
        booking_interest = self.process_booking_interest_response(response_info=response_info , lead_booking_data=lead_booking_data)
        if booking_interest == False:
            booking_selection = self.process_booking_selection_response(response_info=response_info , lead_booking_data=lead_booking_data)
            if isinstance(booking_selection , dict):
                self.messages.add_lead_message(lead_id=lead_booking_data["lead_id"] , role="assistant" , content=booking_selection["message"])
                return {"status" : booking_selection["status"] , "message" : booking_selection["message"]}

    

    
    def process_booking_interest_response(self , response_info , lead_booking_data):
        if isinstance(response_info , str):
            return
        
        logging.info(
            f"[BOOKING] lead_id={lead_booking_data['lead_id']} "
            f"step=process_booking_interest booking_state={lead_booking_data['booking_state']} "
            f"response={response_info}"
            )
        if lead_booking_data["booking_state"] == "booking_interest":
            if response_info["id"] == "interest_yes":
                self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] , param="booking_state" , value="booking_selection")
                self.messages.add_lead_message(lead_id=lead_booking_data["lead_id"] , role="user" , content="yes")
                lead_booking_data["booking_state"] = "booking_selection"

            elif response_info["id"] == "interest_no":
                self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] ,  param="booking_state" , value="booking_declined_intro")
                self.messages.add_lead_message(lead_id=lead_booking_data["lead_id"] , role="user" , content="no")
                lead_booking_data["booking_state"] = "booking_declined_intro"
            
            return True
        return False
    


    def process_booking_selection_response(self , response_info , lead_booking_data):
        if isinstance(response_info , str):
            return
    
        if lead_booking_data["booking_state"] == "booking_selection":
            if response_info["id"] != "selection_declined":
                slot_status = self.booking_slots.get_booking_slot(slot_id=response_info["id"])
                if slot_status is None:
                    return {"status" : "output" , "message" : "The selected time slot is no longer available. Please choose another one. "}
                elif slot_status == 1:
                    return {"status" : "output" , "message" : "This time slot has already been booked. Please choose another available time."}
                
                self.booking_slots.close_booking_slot(slot_id=response_info["id"])
                self.appointments.create_appointment(slot_id=response_info["id"], lead_id=lead_booking_data["lead_id"])
                self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] , param="booking_state" , value="booking_accepted_options")
                self.messages.add_lead_message(lead_id=lead_booking_data["lead_id"] , role="user" , content=response_info["id"])

                lead_booking_data["booking_state"] = "booking_accepted_options"
            
            elif response_info["id"] == "selection_declined":
                self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] , param="booking_state" , value="booking_declined_options")
                lead_booking_data["booking_state"] = "booking_declined_options"
            
            return True
        return False
    





    def generate_booking_interest(self):
        interest_questions = [
            {"id": "interest_yes", "title": "yes"},
            {"id": "interest_no", "title": "no"}
            ]
        
        questions = [
            "Awesome, sounds like you're ready to get started!\n"
            "Would you like to schedule your first session?"
        ]
        question = random.choice(questions)

        return {"buttons" : interest_questions , "body" : question}
    

    def generate_booking_options(self):
        available_slots = []
        all_booking_slots = self.booking_slots.get_all_slots()

        for slot in all_booking_slots:
            if slot["is_taken"] == 0:
                raw_datetime = slot["date"]

                if isinstance(raw_datetime, datetime):
                    dt = raw_datetime
                else:
                    dt = datetime.fromisoformat(raw_datetime)

                available_slots.append({
                    "id": str(slot["slot_id"]),
                    "title": dt.strftime("%d/%m • %H:%M")
                })
        available_slots.append({"id" : "selection_declined" , "title": "None work"})
        return {"buttons" : available_slots , "body" : "Great — please choose a time that works for you:" , "button_label" : "View slots"}
    

    
    
    def generate_closing_messages(self , closing_type , lead_id):
        if closing_type["booking_state"] == "not eligible":
           return (
               "Thanks for taking the time to answer the questions.\n"
               "Your information has been received successfully."
               )

        elif  closing_type["booking_state"]== "booking_declined_intro":
            return (
                "No problem at all.\n"
                "Your information has been received successfully.\n"
                "The team will reach out to you shortly."
                )
        
        elif  closing_type["booking_state"] == "booking_declined_options":
            return (
                "No worries.\n"
                "Your information has been received successfully.\n"
                "The team will contact you to arrange another time."
                )
        
        elif closing_type["booking_state"] == "booking_accepted_options":
            appointment_data = self.booking_dash_data.get_appointment_by_lead_id(lead_id=lead_id)
            return (
                f"✅ You're all set, {appointment_data['name']}!\n"
                f"Your session is confirmed for {appointment_data['slot_date']}.\n"
                f"See you then!"
            )

        



    def generate_booking_question(self , lead_data):
        logging.info(
            f"[BOOKING] lead_id={lead_data['lead_id']} "
            f"step=generate_question eligible={lead_data['booking_eligible']} "
            f"booking_state={lead_data['booking_state']}"
            )
        
        if lead_data["booking_eligible"] == 0:
            return {"status" : "DONE" , "message" : self.generate_closing_messages(lead_data , lead_data["lead_id"])}
        
        elif lead_data["booking_eligible"] == 1:
            if lead_data["booking_state"] == "booking_interest":
                return {"status" : "booking_interest" , "message" : self.generate_booking_interest()}
            
            elif lead_data["booking_state"] == "booking_selection":
                return {"status" : "booking_selection" , "message" : self.generate_booking_options()}
            
            else:
                return {"status" : "DONE" , "message" : self.generate_closing_messages(lead_data , lead_data["lead_id"])}





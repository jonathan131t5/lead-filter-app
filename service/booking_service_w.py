import random
from datetime import datetime
import logging

from output_builders.booking_questions_english import BookingQuestion

from data_access.lead_booking_repository import LeadsBookingRepository
from data_access.slots_repository import BookingSlotRepository
from data_access.appointment_repository import AppointmentRepository
from data_access.lead_booking_context_repository import LeadBookingContextRepository
from data_access.leads_messages_repository import MessagesRepository

from utils.validators import is_valid_email

from data_base.connection import Connection

class BookingFlow:
    def __init__(self , db):
        self.db = db
        self.messages = MessagesRepository(self.db.cursor)
        self.leads_booking = LeadsBookingRepository(self.db.cursor)
        self.booking_slots = BookingSlotRepository(self.db.cursor)
        self.appointments = AppointmentRepository(self.db.cursor)
        self.booking_context = LeadBookingContextRepository(self.db.cursor)


    
    def process_booking_flow(self , lead_id , content):
        try:
            lead_booking_data = self.booking_context.prepare_lead_booking_context(lead_id=lead_id)
            
            check_booking_result = self.check_lead_booking(lead_data=lead_booking_data)
        
            if check_booking_result["status"] == "invaild flow":
                return False
            
            if check_booking_result["status"] == "has booking":
                self.db.commit()
                return self.generate_booking_question(lead_data=lead_booking_data)
            
            elif check_booking_result["status"] == "not eligible":
                self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] , param="booking_state" , value="not eligible")
                lead_booking_data["booking_state"] = "not eligible"
                self.db.commit()
                return self.generate_booking_question(lead_data=lead_booking_data)


            elif check_booking_result["status"] == True:
                if content is None:
                    self.db.commit()
                    return self.generate_booking_question(lead_data=lead_booking_data)
            
                process_result = self.process_booking_response_flow(response_info=content , lead_booking_data=lead_booking_data)
                if process_result and "status" in process_result:
                    self.db.commit()
                    return {"status" : process_result["status"] , "message" : process_result["message"]} 

            self.db.commit()
            return self.generate_booking_question(lead_data=lead_booking_data)
        
        except Exception:
            self.db.rollback()
            raise
                

    
    def check_lead_booking(self , lead_data):
        if lead_data["final_status"] == "Hot Lead":
            if lead_data["has_booking"] == 0:
                self.leads_booking.set_booking_param(lead_id=lead_data["lead_id"] , param="booking_eligible" , value=1)
                lead_data["booking_eligible"] = 1
                return {"status" : True}
            
            return {"status" : "has booking"}
        
        elif lead_data["current_field"] is not None or lead_data["final_status"] == "pending":
            return {"status" : "invaild flow"}
        
        return {"status" : "not eligible"}
    


    
    def process_booking_response_flow(self , response_info , lead_booking_data):
        booking_interest = self.process_booking_interest_response(response_info=response_info , lead_booking_data=lead_booking_data)
        if booking_interest == False:
            booking_selection = self.process_booking_selection_response(response_info=response_info , lead_booking_data=lead_booking_data)
            if isinstance(booking_selection , dict):
                return {"status" : booking_selection["status"] , "message" : booking_selection["message"]}
            if booking_selection == False:
                self.process_booking_email_response(response_info=response_info , lead_booking_data=lead_booking_data)
    
    
    
    def process_booking_interest_response(self , response_info , lead_booking_data):
        print("BOOKING INTEREST RESPONSE:", response_info, flush=True)
        print("BOOKING STATE:", lead_booking_data["booking_state"], flush=True)
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
        if lead_booking_data["booking_state"] == "booking_selection":
            if response_info["id"] != "selection_declined":
                slot_status = self.booking_slots.get_booking_slot(slot_id=response_info["id"])
                if slot_status is None:
                    return {"status" : "output" , "message" : "The selected time slot is no longer available. Please choose another one. "}
                elif slot_status == 1:
                    return {"status" : "output" , "message" : "This time slot has already been booked. Please choose another available time."}
                
                self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] , param="processing_slot_id" , value=response_info["id"])
                self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] , param="booking_state" , value="email")

                self.messages.add_lead_message(lead_id=lead_booking_data["lead_id"] , role="user" , content=response_info["id"])

                lead_booking_data["processing_slot_id"] = response_info["id"]
                lead_booking_data["booking_state"] = "email"
            
            elif response_info["id"] == "selection_declined":
                self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] , param="booking_state" , value="booking_declined_options")
                lead_booking_data["booking_state"] = "booking_declined_options"
            
            return True
        return False
    


    def process_booking_email_response(self , response_info , lead_booking_data):
        logging.info(
            f"[Process Email] User Email Data: {response_info}"
        )
        if lead_booking_data["booking_state"] == "email":
            self.booking_slots.close_booking_slot(slot_id=lead_booking_data["processing_slot_id"])
            self.appointments.create_appointment(slot_id=lead_booking_data["processing_slot_id"] , lead_id=lead_booking_data["lead_id"] , email=response_info)
            self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] , param="booking_state" , value="booking_accepted_options")

            lead_booking_data["booking_state"] = "booking_accepted_options"

            self.messages.add_lead_message(lead_id=lead_booking_data["lead_id"] , role="user" , content=response_info)

            return True
        return False
            
    
    


    def generate_booking_intro(self):
        interest_questions = [
            {"id": "interest_yes", "title": "yes"},
            {"id": "interest_no", "title": "no"}
            ]
        
        questions = [
            "Would you like to book your first session?" , 
            "Do you want to schedule your first session now?"
        ]
        question = random.choice(questions)

        return {"buttons" : interest_questions , "body" : question}
    

    def generate_booking_options(self):
        available_slots = []
        all_booking_slots = self.booking_slots.get_all_slots()

        for slot in all_booking_slots:
            if slot["is_taken"] == 0:
                raw_datetime = slot["date"]

                dt = datetime.fromisoformat(raw_datetime)

                available_slots.append({
                    "id": str(slot["id"]),
                    "title": dt.strftime("%d/%m • %H:%M")
                })
        available_slots.append({"id" : "selection_declined" , "title" : "I don’t see a time that works"})
        return {"buttons" : available_slots , "body" : "Great — please choose a time that works for you:"}
    


    def generate_email_question(self):
        questions = [
            "What’s the best email to send your meeting details to?" , 
            "What email should we send the meeting confirmation to?"
        ]
        return random.choice(questions)
    
    
    
    
    
    def generate_closing_messages(self , closing_type):
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
            return (
                "Your meeting has been scheduled successfully.\n"
                "A confirmation email has been sent with the meeting details.\n"
                "See you at the meeting."
                )
        



    def generate_booking_question(self , lead_data):
        logging.info(
            f"[BOOKING QUESTION] lead_data: {lead_data}"
        )
        if lead_data["booking_eligible"] == 0:
            return {"status" : "DONE" , "message" : self.generate_closing_messages(lead_data)}
        
        elif lead_data["booking_eligible"] == 1:
            
            if lead_data["booking_state"] == "booking_interest":
                return {"status" : "booking_interest" , "message" : self.generate_booking_intro()}
            
            elif lead_data["booking_state"] == "booking_selection":
                return {"status" : "booking_selection" , "message" : self.generate_booking_options()}
            
            elif lead_data["booking_state"] == "email":
                return {"status" : "email" , "message" : self.generate_email_question()}
            
            else:
                return {"status" : "DONE" , "message" : self.generate_closing_messages(lead_data)}




db = Connection()
bookingflow = BookingFlow(db=db)

bookingflow.leads_booking.create_leads_booking_table()
bookingflow.booking_slots.create_booking_table()
bookingflow.appointments.create_appointment_table()
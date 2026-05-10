import random
from datetime import datetime
import logging


class BookingQuestion:
    def __init__(self):
        pass


    def generate_booking_intro(self):
        questions = [
            "Would you like to book your first session?" , 
            "Do you want to schedule your first session now?"
        ]
        return random.choice(questions)
    

    def generate_booking_options(self):
        available_slots = []
        all_booking_slots = self.slot_repository.get_all_slots()

        for slot in all_booking_slots:
            if slot["is_taken"] == 0:
                raw_datetime = slot["date"]

                dt = datetime.fromisoformat(raw_datetime)

                available_slots.append({
                    "id": slot["id"],
                    "label": dt.strftime("%d/%m • %H:%M")
                })

        return available_slots
    


    def generate_email_question(self):
        questions = [
            "What’s the best email to send your meeting details to?" , 
            "What email should we send the meeting confirmation to?"
        ]
        return random.choice(questions)
    
    
    
    
    
    def generate_closing_messages(self , closing_type):
        if closing_type == "not eligible":
           return (
               "Thanks for taking the time to answer the questions.\n"
               "Your information has been received successfully."
               )

        elif closing_type == "booking_declined_intro":
            return (
                "No problem at all.\n"
                "Your information has been received successfully.\n"
                "The team will reach out to you shortly."
                )
        
        elif closing_type == "booking_declined_options":
            return (
                "No worries.\n"
                "Your information has been received successfully.\n"
                "The team will contact you to arrange another time."
                )
        
        elif closing_type == "booking_accepted_options":
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

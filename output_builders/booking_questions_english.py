import random


class BookingQuestion:
    def __init__(self):
        pass


    def generate_booking_intro(self):
        questions = [
            "Would you like to book your first session?" , 
            "Do you want to schedule your first session now?"
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
        

    def generate_booking_options(self):
        available_slots = []
        all_booking_slots = self.slot_repository.get_all_slots()
        for slot in all_booking_slots:
            if slot["is_taken"] == 0:
                available_slots.append(slot)

        return available_slots




    def generate_booking_question(self , lead_data):
        if lead_data["booking_eligible"] == 0:
            return self.generate_closing_messages(lead_data)
        
        elif lead_data["booking_eligible"] == 1:
            if lead_data["booking_state"] == "booking_interest":
                return self.generate_booking_intro()
            elif lead_data["booking_state"] == "booking_selection":
                return self.generate_booking_options()
            else:
                return self.generate_closing_messages(lead_data)

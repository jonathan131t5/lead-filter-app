import random


class lead_booking:
    def __init__(self):
        pass


    
    def process_booking_flow(self , lead_booking_data , response_info):
        if response_info is None:
            check_booking_result = self.check_lead_booking(lead_data=lead_booking_data)
            if check_booking_result == True:
                return self.generate_booking_question(lead_data=lead_booking_data)

        self.process_booking_response(response_info=response_info , lead_booking_data=lead_booking_data)

    
    def check_lead_booking(self , lead_data):
        if lead_data["final_status"] == "Hot Lead":
            if lead_data["booking_completed"] is None:
                self.lead_booking.set_booking_param(lead_id=lead_data["lead_id"] , param="booking_eligible" , value=1)
                return True
            
            return False
        
        return False
    

    def generate_booking_question(self , lead_data):
        if lead_data["booking_eligible"] == 1:
            if lead_data["booking_state"] == "booking_interest":
                return self.build_booking_intro_question()
            elif lead_data["booking_state"] == "booking_selection":
                return self.fetch_booking_options()


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
                available_slots.append(slot)

        return available_slots
    

    
    def process_booking_response(self , response_info , lead_booking_data):
        if lead_booking_data["booking_state"] == "booking_interest":
            if response_info["status"] == True:
                self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] , param="booking_state" , value="booking_selection")
            
            elif response_info["status"] == False:
                self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] ,  param="booking_state" , value="booking_declined_intro")
                
        
        elif lead_booking_data["booking_state"] == "booking_selection":
            if response_info["status"] == True:
                self.slot_repository.close_booking_slot(slot_id=response_info["slot_id"])
                self.appointment_repository.create_appointment(slot_id=response_info["slot_id"] , lead_id=lead_booking_data["lead_id"] , email=response_info["email"])
                self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] , param="booking_state" , value="booking_accepted_options")

            elif response_info["status"] == False:
                self.leads_booking.set_booking_param(lead_id=lead_booking_data["lead_id"] , param="booking_state" , value="booking_declined_options")
    
    
    

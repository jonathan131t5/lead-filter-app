class LeadBookingContextRepository:
    def __init__(self, cursor):
        self.cursor = cursor



    def prepare_lead_booking_context(self , lead_id):
        self.cursor.execute("""
            SELECT
            li.final_status,
            ls.has_booking , 
            ls.booking_state , 
            ls.booking_eligible,
            lcs.current_field
        FROM leads_data li

        JOIN leads_booking ls 
            ON li.lead_id = ls.lead_id

        JOIN lead_conversation_states lcs
            ON li.lead_id = lcs.lead_id
        
        WHERE li.lead_id = ?
    """ , (lead_id , ))

        row = self.cursor.fetchone()

        if not row:
            return None 
        
        return {
            "lead_id" : lead_id ,
            "final_status" : row[0] , 
            "has_booking" : row[1] , 
            "booking_state" : row[2] , 
            "booking_eligible" : row[3] , 
            "current_field": row[4]
        }
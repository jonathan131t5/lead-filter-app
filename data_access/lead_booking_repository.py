class LeadsBookingRepository:
    def __init__(self , cursor):
        self.cursor = cursor


    def create_leads_booking_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads_booking(
        lead_id INTEGER PRIMARY KEY,
        booking_eligible INTEGER DEFAULT 0 ,
        has_booking INTEGER DEFAULT 0,
        processing_slot_id INTEGER , 
        booking_state TEXT DEFAULT 'booking_interest' 
        )              
        """)


    def create_lead_booking(self , lead_id):
        self.cursor.execute(
        "INSERT INTO leads_booking (lead_id) VALUES = (?)" , 
        (lead_id , )
        )
    
    
    
    
    def get_leads_booking(self , lead_id):
        self.cursor.execute(
        "SELECT booking_eligible , booking_completed FROM leads_booking WHERE lead_id = ?" , 
        (lead_id , )
        )

        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return {
            "lead_id" : lead_id , 
            "booking_eligible" : result[0] , 
            "booking_completed" : result[1]
        }
    
    
    def set_booking_param(self , lead_id , param , value):
        self.cursor.execute(
        f"UPDATE leads_booking SET {param} = ? WHERE lead_id = ?" , 
        (value , lead_id)
        )
    


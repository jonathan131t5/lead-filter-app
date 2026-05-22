class AppointmentRepository:
    def __init__(self , cursor):
        self.cursor = cursor


    
    def create_appointment_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointment(
        id INTEGER PRIMARY KEY AUTOINCREMENT , 
        slot_id INTEGER , 
        lead_id INTEGER , 
        status DEFAULT 'pending'
        )
        """)


    def create_appointment(self , slot_id , lead_id):
        self.cursor.execute(
        "INSERT INTO appointment (slot_id , lead_id) VALUES (? , ?)" , 
        (slot_id , lead_id)
        )



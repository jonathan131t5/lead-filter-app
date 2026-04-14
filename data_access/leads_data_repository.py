class LeadsDataRepository:
    def __init__(self , cursor):
        self.cursor = cursor


    def create_leads_data_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads_data(
        lead_id INTEGER PRIMARY KEY AUTOINCREMENT , 
        name TEXT ,
        phone_number TEXT UNIQUE NOT NULL ,
        final_status TEXT DEFAULT pending ,
        summary TEXT ,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
        updated_at TIMESTAMP,
        last_interaction_at TIMESTAMP                 
        )                   
        """)

    
    def create_new_lead(self , name , phone_number):
        self.cursor.execute(
        "INSERT INTO leads_data (name , phone_number) VALUES(? , ?)" , 
        (name , phone_number)
        )


    def get_lead_base_data(self , phone_number):
        self.cursor.execute(
        "SELECT lead_id , name , final_status , summary FROM leads_data WHERE phone_number = ?" , 
        (phone_number , )
        )
        
        result = self.cursor.fetchone()
        if result is None:
            return None
    
        return {
            "phone_number" : phone_number , 
            "lead_id" : result[0] ,
            "name" : result[1] ,
            "final_status" : result[2] ,
            "summary" : result[3]
        }

    
    def get_lead_final_status(self , lead_id):
        self.cursor.execute(
        "SELECT final_status FROM leads_data WHERE lead_id = ?" ,
        (lead_id , )
        )

        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return result[0]
    
    
    def set_lead_final_status(self , lead_id , status):
        self.cursor.execute(
        "UPDATE leads_data SET final_status = ? WHERE lead_id = ?" ,
        (status , lead_id)
        )
  


    def upload_summary(self , lead_summary , lead_id):
        self.cursor.execute(
        "UPDATE leads_data SET summary = ? WHERE lead_id = ?" , 
        (lead_summary , lead_id)
        )







class LeadsDataRepository:
    def __init__(self , cursor):
        self.cursor = cursor


    def create_leads_data_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads_data(
        lead_id INTEGER PRIMARY KEY AUTOINCREMENT , 
        session_id INTEGER , 
        name TEXT ,
        phone_number TEXT UNIQUE,
        final_status TEXT DEFAULT 'pending' ,
        summary TEXT ,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
        updated_at TIMESTAMP,
        last_interaction_at TIMESTAMP                 
        )                   
        """)

    
    def create_new_lead(self, name , session_id):
        self.cursor.execute("INSERT INTO leads_data (name , session_id) VALUES (? , ?)", 
        (name , session_id))

        return self.cursor.lastrowid
         


    def get_lead_base_data(self , session_id):
        self.cursor.execute(
        "SELECT lead_id , name , final_status , summary FROM leads_data WHERE session_id = ?" , 
        (session_id , )
        )
        
        result = self.cursor.fetchone()
        if result is None:
            return None
    
        return {
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


    def update_lead_last_interaction(self , last_interaction , lead_id):
        self.cursor.execute(
        "UPDATE leads_data SET last_interaction_at = ? WHERE lead_id = ?" ,
        (last_interaction , lead_id)
        )


    def get_lead_last_interaction(self , lead_id):
        self.cursor.execute(
        "SELECT last_interaction_at FROM leads_data WHERE lead_id = ?" ,
        (lead_id , )
        )
        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return result[0]
    

    def update_lead_phone(self , phone , lead_id):
        self.cursor.execute(
        "UPDATE leads_data SET phone_number = ? WHERE lead_id = ?" , 
        (phone , lead_id)
        )



    def get_all_leads_data(self):
        self.cursor.execute("""
            SELECT lead_id, name, phone_number, final_status, summary , last_interaction_at
            FROM leads_data
            ORDER BY 
                CASE 
                    WHEN final_status = 'Hot Lead' THEN 1
                    WHEN final_status = 'pending' THEN 2
                    WHEN final_status = 'Cold Lead' THEN 3
                END,
                last_interaction_at DESC
        """)

        rows = self.cursor.fetchall()

        leads = []
        for row in rows:
            leads.append({
                "lead_id" : row[0],
                "name" : row[1],
                "phone" : row[2],
                "final_status" : row[3],
                "summary" : row[4],
                "last_interaction_at" : row[5]
            })

        return leads
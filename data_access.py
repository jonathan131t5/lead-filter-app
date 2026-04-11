import sqlite3

class DataAccess:
    def __init__(self):
        self.conn = sqlite3.connect("lead_qualification.db", check_same_thread=False)
        self.cursor = self.conn.cursor()


    
    def create_leads_info_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads_info(
        lead_id INTEGER PRIMARY KEY AUTOINCREMENT , 
        name TEXT ,
        phone_number TEXT UNIQUE NOT NULL ,
        status TEXT Default pending ,
        summary TEXT ,
        current_field TEXT DEFAULT goal ,
        regular_attempt_number INTEGER DEFAULT 0 ,
        confuse_attempt_number INTGER DEFAULT 0 ,
        need_fallback INTEGER DEFAULT 0 ,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
        updated_at TIMESTAMP,
        last_interaction_at TIMESTAMP                 
        )                   
        """)
        self.conn.commit()

    
    def create_lead_essential_data(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS lead_essential_data(
        lead_id INTEGER PRIMARY KEY AUTOINCREMENT , 
        name TEXT ,
        phone_number TEXT UNIQUE NOT NULL ,
        status TEXT  ,
        summary TEXT ,         
        )                   
        """)
        self.conn.commit()

    

    def create_leads_scores_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads_scores(
        lead_id INTEGER PRIMARY KEY ,
        goal_score INTEGER DEFAULT 0 ,
        budget_score INTEGER DEFAULT 0 ,
        urgency_score INTEGER DEFAULT 0,
        score_count INTEGER DEFAULT 0 ,
        total_score INTEGER DEFAULT 0
        )                 
        """)
        self.conn.commit()
    
    
    
    def create_leads_messages_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads_messages(
        message_id INTEGER PRIMARY KEY AUTOINCREMENT ,
        lead_id INTEGER ,
        role TEXT ,
        content TEXT ,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )                   
        """)
        self.conn.commit()


    
    def create_leads_fields_data(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads_fields_data(
        lead_id INTEGER PRIMARY KEY , 
        goal_bot TEXT ,
        goal_user TEXT ,
        budget_bot TEXT ,
        budget_user TEXT ,
        urgency_bot TEXT ,
        urgency_user TEXT ,
        updated_at TIMESTAMP
        )
        """)
        self.conn.commit()

    
    
    
    def add_lead_message(self , lead_id , role , content):   
        self.cursor.execute(
        "INSERT INTO leads_messages (lead_id , role , content) VALUES (? , ? , ?)" ,
        (lead_id , role , content)
        )
        self.conn.commit()


    
    def create_new_lead_score(self , lead_id):
        self.cursor.execute(
        "INSERT INTO leads_scores (lead_id) VALUES(?)" , 
        (lead_id , )
        )
        self.conn.commit()
    
    
    
    def create_new_lead(self , name , phone_number):
        self.cursor.execute(
        "INSERT INTO leads_info (name , phone_number) VALUES(? , ?)" , 
        (name , phone_number)
        )
        self.conn.commit()


    def create_new_fields_data(self , lead_id):
        self.cursor.execute(
        "INSERT INTO leads_fields_data (lead_id) VALUES (?)" ,
        (lead_id , )
        )
        self.conn.commit()

    
    def update_lead_score_info(self , lead_id , score_count , total_score , score_field , value):
        self.cursor.execute(
        f"UPDATE leads_scores SET score_count = ? , total_score = ? , {score_field} = ? WHERE lead_id = ?" , 
        (score_count , total_score , value , lead_id)
        )
        self.conn.commit()

    
    
    def set_lead_status(self , lead_id , status):
        self.cursor.execute(
        "UPDATE leads_info SET status = ? WHERE lead_id = ?" ,
        (status , lead_id)
        )
        self.conn.commit()

    
    
    def get_lead_status(self , lead_id):
        self.cursor.execute(
        "SELECT status FROM leads_info WHERE lead_id = ?" ,
        (lead_id , )
        )

        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return result[0]

    
    
    def update_lead_current_field(self , lead_id , updated_field):
        self.cursor.execute(
        "UPDATE leads_info SET current_field = ? WHERE lead_id = ?" , 
        (updated_field , lead_id)
        )
        self.conn.commit()
    
    
    def update_lead_attempt_number(self , lead_id , number):
        self.cursor.execute(
        "UPDATE leads_info SET attempt_number = ? WHERE lead_id = ?" , 
        (number , lead_id)
        )
        self.conn.commit()


    
    def get_lead_base_info(self , phone_number):
        self.cursor.execute(
        "SELECT lead_id , name , current_field , attempt_number , status , summary FROM leads_info WHERE phone_number = ?" , 
        (phone_number , )
        )
        
        result = self.cursor.fetchone()
        if result is None:
            return None
    
        return {
            "phone_number" : phone_number , 
            "lead_id" : result[0] ,
            "name" : result[1] ,
            "current_field" : result[2] ,
            "attempt_number" : result[3] ,
            "status" : result[4] ,
            "summary" : result[5]
        }
    

    def get_lead_score_info(self , lead_id):
        self.cursor.execute(
        "SELECT total_score , score_count , goal_score , budget_score , urgency_score FROM leads_scores WHERE lead_id = ?" ,
        (lead_id , )
        )
        
        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return {
            "lead_id" : lead_id ,
            "total_score" : result[0] , 
            "score_count" : result[1] ,
            "goal_score" : result[2] , 
            "budget_score" : result[3] ,
            "urgency_score" : result [4]
        }
    

    
    def create_lead_fields_data(self , lead_id):
        self.cursor.execute(
        "INSERT INTO leads_fields_data (lead_id) VALUES (?)" ,
        (lead_id , )
        )
        self.conn.commit()


    def update_lead_field_data(self , lead_id , field , value):
        self.cursor.execute(
        f"UPDATE leads_fields_data SET {field} = ? WHERE lead_id = ?" ,
        (value , lead_id)
        )
        self.conn.commit()


    def get_lead_specific_field_data(self , lead_id , field):
        self.cursor.execute(
        f"SELECT {field} FROM leads_fields_data WHERE lead_id = ?" , 
        (lead_id ,)
        )

        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return result[0]
    

    def get_all_lead_field_data(self , lead_id):
        self.cursor.execute(
        "SELECT goal_user , budget_user , urgency_user FROM leads_fields_data WHERE lead_id = ?" , 
        (lead_id , )
        )

        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return {
            "lead_id" : lead_id ,
            "goal_user" : result[0] ,
            "budget_user" : result[1] ,
            "urgency_user" : result[2]
        }
    


    def get_last_exchange(self , lead_id):
        self.cursor.execute(
        "SELECT role , content FROM leads_messages WHERE lead_id = ? ORDER BY message_id DESC LIMIT 3" ,
        (lead_id , )
        )


        raw_messages = self.cursor.fetchall()
        if not raw_messages:
            return []
        
        final_messages = raw_messages[::-1]
        
        ai_input = []
        for role , content in final_messages:
            ai_input.append({"role" : role , "content" : content})

        return ai_input


    def get_lead_total_score(self , lead_id):
        self.cursor.execute(
        "SELECT total_score FROM leads_scores WHERE lead_id = ?" ,
        (lead_id , )
        )
        
        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return result[0]
    

    def upload_summary(self , lead_summary , lead_id):
        self.cursor.execute(
        "UPDATE leads_info SET summary = ? WHERE lead_id = ?" , 
        (lead_summary , lead_id)
        )
        self.conn.commit()
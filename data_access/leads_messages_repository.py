class MessagesRepository:
    def __init__(self , cursor):
        self.cursor = cursor

    
    
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

    
    def add_lead_message(self , lead_id , role , content):   
        self.cursor.execute(
        "INSERT INTO leads_messages (lead_id , role , content) VALUES (? , ? , ?)" ,
        (lead_id , role , content)
        )
 
    
    


    

    
    
    

    
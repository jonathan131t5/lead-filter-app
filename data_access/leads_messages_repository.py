class MessagesRepository:
    def __init__(self , cursor):
        self.cursor = cursor

    
    
    def create_leads_messages_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads_messages(
        message_id INTEGER PRIMARY KEY AUTOINCREMENT ,
        external_message_id INTEGER ,
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
        return self.cursor.lastrowid


    def add_external_message_id(self , message_id , external_message_id):
        self.cursor.execute(
        "UPDATE leads_messages SET external_message_id  = ? WHERE message_id = ?" , 
        (external_message_id , message_id)
        )


    def get_lead_messages(self , lead_id):
        self.cursor.execute(
        "SELECT role , content , created_at FROM leads_messages WHERE lead_id = ? ORDER BY created_at ASC" , 
        (lead_id , )
        )
        rows = self.cursor.fetchall()

        messages = []
        for row in rows:
            messages.append({
                "role": row[0],
                "content": row[1],
                "created_at": row[2]
            })

        return messages
        


    


    

    
    
    

    
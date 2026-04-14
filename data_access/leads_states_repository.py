class LeadsStatesRepository:
    def __init__(self , cursor):
        self.cursor = cursor

    
    def create_lead_conversation_states(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS lead_conversation_states(
        lead_id INTEGER PRIMARY KEY , 
        current_field TEXT DEFAULT goal ,
        regular_attempt_number INTEGER DEFAULT 1 ,
        confuse_attempt_number INTGER DEFAULT 1 ,
        question_state TEXT DEFAULT base,
        question_reason TEXT DEFAULT base ,
        final_status TEXT DEFAULT pending ,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
        updated_at TIMESTAMP,
        last_interaction_at TIMESTAMP                 
        )                   
        """)


    def create_new_lead_conversation_states_data(self , lead_id):
        self.cursor.execute(
        "INSERT INTO lead_conversation_states (lead_id) VALUES (?)" , 
        (lead_id , )
        )

    
    def get_lead_conversation_states(self , lead_id):
        self.cursor.execute(
        "SELECT current_field , regular_attempt_number , confuse_attempt_number , question_state , question_reason , final_status FROM lead_conversation_states WHERE lead_id = ?" ,
        (lead_id , )
        )
        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return {
            "lead_id" : lead_id ,
            "current_field" : result[0] , 
            "regular_attempt_number" : result[1] , 
            "confuse_attempt_number" : result[2] , 
            "question_state" : result[3] , 
            "question_reason" : result[4] , 
            "final_status" : result[5]
        }


    def update_lead_current_field(self , lead_id , updated_field):
        self.cursor.execute(
        "UPDATE lead_conversation_states SET current_field = ? WHERE lead_id = ?" , 
        (updated_field , lead_id)
        )
    
    
    def update_lead_regular_attempt_number(self , lead_id , number):
        self.cursor.execute(
        "UPDATE lead_conversation_states SET regular_attempt_number = ? WHERE lead_id = ?" , 
        (number , lead_id)
        )

    
    def update_lead_confuse_attempt_number(self , lead_id , number):
        self.cursor.execute(
        "UPDATE lead_conversation_states SET confuse_attempt_number = ? WHERE lead_id = ?" ,
        (number , lead_id)
        )

    
    def update_lead_question_state(self , lead_id , value):
        self.cursor.execute(
        "UPDATE lead_conversation_states SET question_state = ? WHERE lead_id = ?" ,
        (value , lead_id)
        )

    
    def update_lead_question_reason(self , lead_id , value):
        self.cursor.execute(
        "UPDATE lead_conversation_states SET question_reason = ? WHERE lead_id = ?" , 
        (value , lead_id)
        )
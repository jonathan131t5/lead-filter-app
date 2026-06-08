class LeadsDataRepository:
    def __init__(self, db):
        self.db = db



    def create_leads_data_table(self):
        cursor = self.db.new_cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads_data (
                lead_id SERIAL PRIMARY KEY,
                session_id TEXT,
                name TEXT,
                phone_number TEXT UNIQUE,
                final_status TEXT DEFAULT 'pending',
                summary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                last_interaction_at TIMESTAMP
            )
        """)



    def create_new_lead(self, session_id):
        cursor = self.db.new_cursor()
        cursor.execute("""
            INSERT INTO leads_data (session_id)
            VALUES (%s)
            RETURNING lead_id
        """, (session_id,))

        return cursor.fetchone()[0]



    def get_lead_base_data(self, session_id):
        cursor = self.db.new_cursor()
        cursor.execute("""
            SELECT lead_id, name, final_status, summary
            FROM leads_data
            WHERE session_id = %s
        """, (session_id,))

        result = cursor.fetchone()

        if result is None:
            return None

        return {
            "lead_id": result[0],
            "name": result[1],
            "final_status": result[2],
            "summary": result[3]
        }



    def get_lead_final_status(self, lead_id):
        cursor = self.db.new_cursor()
        cursor.execute("""
            SELECT final_status
            FROM leads_data
            WHERE lead_id = %s
        """, (lead_id,))

        result = cursor.fetchone()

        if result is None:
            return None

        return result[0]



    def set_lead_final_status(self, lead_id, status):
        cursor = self.db.new_cursor()
        cursor.execute("""
            UPDATE leads_data
            SET final_status = %s
            WHERE lead_id = %s
        """, (status, lead_id))



    def upload_summary(self, lead_summary, lead_id):
        cursor = self.db.new_cursor()
        cursor.execute("""
            UPDATE leads_data
            SET summary = %s
            WHERE lead_id = %s
        """, (lead_summary, lead_id))



    def update_lead_last_interaction(self, last_interaction, lead_id):
        cursor = self.db.new_cursor()
        cursor.execute("""
            UPDATE leads_data
            SET last_interaction_at = %s
            WHERE lead_id = %s
        """, (last_interaction, lead_id))



    def get_lead_last_interaction(self, lead_id):
        cursor = self.db.new_cursor()
        cursor.execute("""
            SELECT last_interaction_at
            FROM leads_data
            WHERE lead_id = %s
        """, (lead_id,))

        result = cursor.fetchone()

        if result is None:
            return None

        return result[0]



    def update_lead_phone(self, phone, lead_id):
        cursor = self.db.new_cursor()
        cursor.execute("""
            UPDATE leads_data
            SET phone_number = %s
            WHERE lead_id = %s
        """, (phone, lead_id))



    def update_lead_name(self, name, lead_id):
        cursor = self.db.new_cursor()
        cursor.execute("""
            UPDATE leads_data
            SET name = %s
            WHERE lead_id = %s
        """, (name, lead_id))



    def get_all_leads_data(self):
        cursor = self.db.new_cursor()
        cursor.execute("""
            SELECT lead_id, name, phone_number, final_status, summary, last_interaction_at
            FROM leads_data
            ORDER BY 
                CASE 
                    WHEN final_status = 'Hot Lead' THEN 1
                    WHEN final_status = 'pending' THEN 2
                    WHEN final_status = 'Cold Lead' THEN 3
                    ELSE 4
                END,
                last_interaction_at DESC
        """)

        rows = cursor.fetchall()

        leads = []

        for row in rows:
            leads.append({
                "lead_id": row[0],
                "name": row[1],
                "phone": row[2],
                "final_status": row[3],
                "summary": row[4],
                "last_interaction_at": row[5]
            })

        return leads
    


    def get_started_leads_last_30_days(self):
        cursor = self.db.new_cursor()
        cursor.execute("""
        SELECT *
        FROM leads_data 
        WHERE created_at >= NOW() - INTERVAL '30 days'
        """)
        
        return len(cursor.fetchall())
    
    

    def get_completed_leads_last_30_days(self):
        cursor = self.db.new_cursor()
        cursor.execute("""
        SELECT *
        FROM leads_data
        WHERE created_at >= NOW() - INTERVAL '30 days'
        AND final_status <> 'pending'
        """)

        return len(cursor.fetchall())
    
    
    
    def get_hot_leads_last_30_days(self):
        cursor = self.db.new_cursor()
        cursor.execute("""
        SELECT *
        FROM leads_data
        WHERE created_at >= NOW() - INTERVAL '30 days'
        AND final_status = 'Hot Lead'
        """)

        return len(cursor.fetchall())
    



    def get_uncompleted_lead_fields_last_30_days(self):
        cursor = self.db.new_cursor()
        cursor.execute("""
        SELECT lead_conversation_states.current_field 
        FROM leads_data
        JOIN lead_conversation_states
        ON leads_data.lead_id = lead_conversation_states.lead_id
        WHERE leads_data.created_at >= NOW() - INTERVAL '30 days'
        AND leads_data.final_status = 'pending'
        """)

        rows = cursor.fetchall()
        uncompleted_fields = []
        
        for row in rows:
            uncompleted_fields.append({"current_field" : row[0]})

        return uncompleted_fields



    def get_dropoff_stats_last_30_days(self , uncompleted_fields):
        fields = {
            "pre_flow" :  0 , 
            "name" : 0 , 
            "goal" : 0 , 
            "urgency" : 0 , 
            "booking_flow" : 0
        }
        
        for field in uncompleted_fields:
            if field["current_field"] == "pre_flow":
                fields["pre_flow"] += 1
            
            elif field["current_field"] == "name":
                fields["name"] += 1
            
            elif field["current_field"] == "goal":
                fields["goal"] += 1
            
            elif field["current_field"] == "urgency":
                fields["urgency"] += 1
            
            else:
                fields["booking_flow"] += 1

        return fields


    def get_completion_rate_last_30_days(self , started_number , completed_number):
        return round((completed_number / started_number) * 100)


    
    def get_all_analytics(self):
        started_number = self.get_started_leads_last_30_days()
        completed_number = self.get_completed_leads_last_30_days()
        hots_number = self.get_hot_leads_last_30_days()
        completion_rate = self.get_completion_rate_last_30_days(started_number=started_number , completed_number=completed_number)
        uncompleted_fields = self.get_uncompleted_lead_fields_last_30_days()
        fields_dropoffs = self.get_dropoff_stats_last_30_days(uncompleted_fields=uncompleted_fields)

        print(fields_dropoffs , flush=True)
        return {
            "entered" :  started_number ,
            "completed" : completed_number , 
            "hot_leads" : hots_number , 
            "complete_rate" : completion_rate , 
            "fields_dropoffs" : fields_dropoffs
        }


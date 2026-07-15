class LeadsFieldsRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    def create_leads_fields_data(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads_fields_data (
                lead_id INTEGER PRIMARY KEY,
                goal_user TEXT,
                phone_user TEXT,
                urgency_user TEXT,
                eligibility_user1 TEXT,
                eligibility_user2 TEXT, 
                eligibility_user3 TEXT, 
                eligibility_user4 TEXT, 
                eligibility_user5 TEXT, 
                updated_at TIMESTAMP
            )
        """)

    def create_new_lead_fields_data(self, lead_id):
        self.cursor.execute("""
            INSERT INTO leads_fields_data (lead_id)
            VALUES (%s)
        """, (lead_id,))

    def get_all_lead_field_data(self, lead_id):
        self.cursor.execute("""
            SELECT goal_user, urgency_user
            FROM leads_fields_data
            WHERE lead_id = %s
        """, (lead_id,))

        result = self.cursor.fetchone()

        if result is None:
            return None

        return {
            "lead_id": lead_id,
            "goal_user": result[0],
            "urgency_user": result[1]
        }

    def update_lead_field_data(self, lead_id, field, value):
        allowed_fields ={
            "goal_user",
            "phone_user",
            "urgency_user",
            "eligibility_user1",
            "eligibility_user2",
            "eligibility_user3",
            "eligibility_user4",
            "eligibility_user5",
            "updated_at"
            }

        if field not in allowed_fields:
            raise ValueError("Invalid field")

        self.cursor.execute(
            f"UPDATE leads_fields_data SET {field} = %s WHERE lead_id = %s",
            (value, lead_id)
        )

    def get_lead_specific_field_data(self, lead_id, field):
        allowed_fields ={
            "goal_user",
            "phone_user",
            "urgency_user",
            "eligibility_user1",
            "eligibility_user2",
            "eligibility_user3",
            "eligibility_user4",
            "eligibility_user5",
            "updated_at"
            }

        if field not in allowed_fields:
            raise ValueError("Invalid field")

        self.cursor.execute(
            f"SELECT {field} FROM leads_fields_data WHERE lead_id = %s",
            (lead_id,)
        )

        result = self.cursor.fetchone()

        if result is None:
            return None

        return result[0]
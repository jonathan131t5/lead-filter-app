class LeadsFieldsRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    def create_leads_fields_data(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads_fields_data (
                lead_id INTEGER PRIMARY KEY,
                goal_bot TEXT,
                goal_user TEXT,
                eligibility_user TEXT, 
                eligibility_bot TEXT,
                phone_user TEXT,
                urgency_bot TEXT,
                urgency_user TEXT,
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
        allowed_fields = {
            "goal_bot",
            "goal_user",
            "phone_user",
            "urgency_bot",
            "urgency_user",
            "eligibility_user" , 
            "eligibility_bot",
            "updated_at"
        }

        if field not in allowed_fields:
            raise ValueError("Invalid field")

        self.cursor.execute(
            f"UPDATE leads_fields_data SET {field} = %s WHERE lead_id = %s",
            (value, lead_id)
        )

    def get_lead_specific_field_data(self, lead_id, field):
        allowed_fields = {
            "goal_bot",
            "goal_user",
            "phone_user",
            "urgency_bot",
            "urgency_user",
            "eligibility_user" , 
            "eligibility_bot",
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
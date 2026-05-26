class MessagesRepository:
    def __init__(self, cursor):
        self.cursor = cursor



    def create_leads_messages_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads_messages (
                message_id SERIAL PRIMARY KEY,
                external_message_id TEXT,
                lead_id INTEGER,
                role TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)



    def add_lead_message(self, lead_id, role, content):
        self.cursor.execute("""
            INSERT INTO leads_messages (lead_id, role, content)
            VALUES (%s, %s, %s)
            RETURNING message_id
        """, (lead_id, role, content))

        return self.cursor.fetchone()[0]



    def add_external_message_id(self, message_id, external_message_id):
        self.cursor.execute("""
            UPDATE leads_messages
            SET external_message_id = %s
            WHERE message_id = %s
        """, (external_message_id, message_id))



    def get_lead_messages(self, lead_id):
        self.cursor.execute("""
            SELECT role, content, created_at
            FROM leads_messages
            WHERE lead_id = %s
            ORDER BY created_at ASC
        """, (lead_id,))

        rows = self.cursor.fetchall()

        messages = []

        for row in rows:
            messages.append({
                "role": row[0],
                "content": row[1],
                "created_at": row[2]
            })

        return messages
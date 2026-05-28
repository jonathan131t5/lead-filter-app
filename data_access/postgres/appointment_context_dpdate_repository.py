class AppointmentsContextRepository:
    def __init__(self, cursor):
        self.cursor = cursor


    def update_appointment(self, appointment_id, name, phone, booking_status):
        self.cursor.execute("""
            SELECT lead_id, slot_id
            FROM appointment
            WHERE id = %s
        """, (appointment_id,))

        row = self.cursor.fetchone()

        if not row:
            return {"status": False, "message": "appointment_not_found"}

        lead_id = row[0]
        slot_id = row[1]

        self.cursor.execute("""
            UPDATE leads_data
            SET name = %s , phone_number = %s
            WHERE lead_id = %s
        """, (name, phone, lead_id))

        self.cursor.execute("""
            UPDATE appointment
            SET status = %s
            WHERE id = %s
        """, (booking_status, appointment_id))

        return {"status": True , "message": "updated successfully"}
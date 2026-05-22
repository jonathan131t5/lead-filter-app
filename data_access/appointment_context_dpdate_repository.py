class AppointmentsContextRepository:
    def __init__(self, cursor):
        self.cursor = cursor


    def update_appointment(self, appointment_id, name, phone, slot_date, booking_status):
        self.cursor.execute("""
            SELECT lead_id, slot_id
            FROM appointment
            WHERE id = ?
        """, (appointment_id,))

        row = self.cursor.fetchone()

        if not row:
            return {"status": False, "message": "appointment_not_found"}

        lead_id = row[0]
        slot_id = row[1]

        self.cursor.execute("""
            UPDATE leads_data
            SET name = ?, phone_number = ?
            WHERE lead_id = ?
        """, (name, phone, lead_id))

        self.cursor.execute("""
            UPDATE appointment
            status = ?
            WHERE id = ?
        """, (booking_status, appointment_id))

        self.cursor.execute("""
            UPDATE booking_slot
            SET date = ?
            WHERE slot_id = ?
        """, (slot_date, slot_id))

        return {"status": True , "message": "updated successfully"}
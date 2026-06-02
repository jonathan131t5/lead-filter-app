class AppointmentsContextRepository:
    def __init__(self, cursor):
        self.cursor = cursor


    def update_appointment(self, appointment_id, name, phone, booking_status):
        if booking_status not in ["booked", "completed", "cancelled"]:
            return {"status": False, "message": "invalid_status"}
        
        elif booking_status == "cancelled":
            slot_status = 0
        
        else:
            slot_status = 1


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


        self.cursor.execute("""
            UPDATE booking_slot
            SET is_taken = %s
            WHERE slot_id = %s
        """, (slot_status , slot_id))

        return {"status": True , "message": "updated successfully"}
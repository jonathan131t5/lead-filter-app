class BookingDashDataRepository:
    def __init__(self, cursor):
        self.cursor = cursor


    def get_all_appointments(self):
        self.cursor.execute("""
            SELECT
                li.lead_id,
                li.final_status,
                li.phone_number,
                li.name,
                lp.id,
                lp.email,
                lp.status,
                lp.slot_id,
                ls.date
            FROM leads_data li

            JOIN appointment lp
                ON li.lead_id = lp.lead_id

            JOIN booking_slot ls
                ON lp.slot_id = ls.id
        """)

        rows = self.cursor.fetchall()

        return [
            {
                "lead_id": row[0],
                "final_status": row[1],
                "phone_number": row[2],
                "name": row[3],
                "booking_id": row[4],
                "email": row[5],
                "booking_status": row[6],
                "slot_id": row[7],
                "slot_date": row[8]
            }
            for row in rows
        ]
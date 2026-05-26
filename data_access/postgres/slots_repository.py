class BookingSlotRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    def create_booking_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS booking_slot (
                slot_id SERIAL PRIMARY KEY,
                date TIMESTAMP,
                is_taken INTEGER DEFAULT 0
            )
        """)

    def create_booking_slot(self, date):
        self.cursor.execute("""
            INSERT INTO booking_slot (date)
            VALUES (%s)
        """, (date,))

    def close_booking_slot(self, slot_id):
        self.cursor.execute("""
            UPDATE booking_slot
            SET is_taken = 1
            WHERE slot_id = %s
        """, (slot_id,))

    def get_booking_slot(self, slot_id):
        self.cursor.execute("""
            SELECT is_taken
            FROM booking_slot
            WHERE slot_id = %s
        """, (slot_id,))

        slot = self.cursor.fetchone()

        if slot is None:
            return None

        return slot[0]

    def get_all_slots(self):
        self.cursor.execute("""
            SELECT *
            FROM booking_slot
        """)

        rows = self.cursor.fetchall()

        slots = []

        for row in rows:
            slots.append({
                "slot_id": row[0],
                "date": row[1],
                "is_taken": row[2]
            })

        return slots
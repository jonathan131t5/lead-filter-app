from datetime import date, datetime, time, timedelta

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


    
    def create_weekly_booking_slots(self , slots_data , weeks_num):
        today_date = date.today()
        day_number = today_date.weekday()
        
        for d in slots_data:
            if day_number > d["day"]:
                days_to_add = day_number - d["day"]
                d["day"] = today_date + timedelta(days= 7 - days_to_add)
            else:
                days_to_add = (d["day"] - day_number)
                d["day"] = today_date + timedelta(days=days_to_add)

            d["day"] = datetime.combine(d["day"], time.fromisoformat(d["time"]))

        for d in slots_data:
            num = weeks_num
            add = 0
            while num > 0:
                self.create_booking_slot(date=d["day"] + timedelta(days=add))
                num -= 1
                add += 7

        

    def close_booking_slot(self, slot_id):
        self.cursor.execute("""
            UPDATE booking_slot
            SET is_taken = 1
            WHERE slot_id = %s
        """, (slot_id,))

        return {"status": True , "message": "updated successfully"}



    def cancel_booking_slot(self, slot_id):
        self.cursor.execute("""
            UPDATE booking_slot
            SET is_taken = 2
            WHERE slot_id = %s
        """, (slot_id,))


    def restore_slot(self , slot_id):
        self.cursor.execute("""
            UPDATE booking_slot
            SET is_taken = 0
            WHERE slot_id = %s
            """, (slot_id,))



    def update_slot(self, slot_id , is_taken):
        self.cursor.execute("""
            UPDATE booking_slot
            SET is_taken = %s
            WHERE slot_id = %s
        """, (slot_id, is_taken))
        
        return {"status": True , "message": "updated successfully"}
    

    def update_slot_date(self, slot_id , date):
        self.cursor.execute("""
            UPDATE booking_slot
            SET date = %s
            WHERE slot_id = %s
        """, (date, slot_id))
        
        return {"status": True , "message": "updated successfully"}
    



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
    


        
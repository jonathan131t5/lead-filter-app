import sqlite3

class Connection:
    def __init__(self):
        self.conn = sqlite3.connect("lead_qualification.db" , timeout=10 , check_same_thread=False)
        self.cursor = self.conn.cursor()

    def commit(self):
        self.conn.commit()


class LeadSummaryContextRepository:
    def __init__(self, cursor):
        self.cursor = cursor

    def prepare_lead_summary_context(self, lead_id):
        self.cursor.execute("""
            SELECT
                li.name,
                li.phone_number,
                li.final_status,

                lfd.goal_user,
                lfd.urgency_user,
                lfd.eligibility_user1,
                lfd.eligibility_user2, 
                lfd.eligibility_user3, 
                lfd.eligibility_user4, 
                lfd.eligibility_user5,

                ls.total_score,
                ls.goal_status,
                ls.urgency_status

            FROM leads_data li

            JOIN leads_scores ls
                ON li.lead_id = ls.lead_id

            JOIN leads_fields_data lfd
                ON li.lead_id = lfd.lead_id

            WHERE li.lead_id = %s
        """, (lead_id,))

        row = self.cursor.fetchone()

        if not row:
            return None

        return {
            "lead_id": lead_id,
            "name": row[0],
            "phone_number": row[1],
            "final_status": row[2],
            "goal_user": row[3],
            "urgency_user": row[4],
            "eligibility_user1": row[5],
            "eligibility_user2": row[6],
            "eligibility_user3": row[7],
            "eligibility_user4": row[8],
            "eligibility_user5": row[9],
            "total_score": row[10],
            "goal_status": row[11],
            "urgency_status": row[12]
        }
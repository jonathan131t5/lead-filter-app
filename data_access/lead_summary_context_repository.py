class LeadSummaryContextRepository:
    def __init__(self, cursor):
        self.cursor = cursor



    def prepare_lead_summary_context(self , lead_id):
        self.cursor.execute("""
            SELECT
            li.name,
            li.phone_number,
            li.final_status,
            
            lfd.goal_user,
            lfd.budget_user,
            lfd.urgency_user,
            
            ls.total_score ,
            ls.goal_status , 
            ls.budget_status ,
            ls.urgency_status

        FROM leads_data li

        JOIN leads_scores ls 
            ON li.lead_id = ls.lead_id

        JOIN leads_fields_data lfd 
            ON li.lead_id = lfd.lead_id
        
        WHERE li.lead_id = ?
    """ , (lead_id , ))

        row = self.cursor.fetchone()

        if not row:
            return None 
        
        return {
            "lead_id" : lead_id ,
            "name" : row[0] , 
            "phone_number" : row[1] , 
            "final_status" : row[2] , 
            "goal_user" : row[3] , 
            "budget_user" : row[4] , 
            "urgency_user" : row[5] , 
            "total_score" : row[6] , 
            "goal_status" : row[7] , 
            "budget_status" : row[8] ,
            "urgency_status" : row[9] 
        }
class LeadScoreManager:
    def __init__(self):
        pass

    
    
    def update_lead_score_info(self , lead_score_info , lead_message_score , message_field):
        if lead_message_score == "unknown":
            lead_score_info["score_count"] += 1
            lead_score_info[message_field] = lead_message_score
            return lead_score_info
        
        
        if lead_message_score > 0:
            lead_score_info["score_count"] += 1
            lead_score_info["total_score"] += lead_message_score
            lead_score_info[message_field] = lead_message_score
            return lead_score_info


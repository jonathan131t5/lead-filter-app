class LeadClassifier:
    def __init__(self):
        pass

    
    
    def classify_lead_score(self , lead_score_info):
        if lead_score_info["score_count"] < 3:
            return None
        
        elif lead_score_info["total_score"] >= 8:
            return "Hot Lead"
        
        elif lead_score_info["total_score"] >= 7:
            if lead_score_info["budget_score"] >= 2 and lead_score_info["urgency_score"] >= 2:
                return "Hot Lead"
            else:
                return "Cold Lead"
        
        else:
            return "Cold Lead"
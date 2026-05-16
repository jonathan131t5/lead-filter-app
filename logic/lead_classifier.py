class LeadClassifier:
    def __init__(self):
        pass

    
    
    def classify_lead_score(self , lead_score_info):
        if lead_score_info["score_count"] < 3:
            return None
        
        elif lead_score_info["total_score"] >= 6:
            return "Hot Lead"
          
        else:
            return "Cold Lead"
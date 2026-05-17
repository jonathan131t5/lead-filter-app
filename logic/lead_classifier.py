class LeadClassifier:
    def __init__(self):
        pass

    
    
    def classify_lead_score(self , lead_score_info):
        if lead_score_info["score_count"] < 2:
            return None
        
        elif lead_score_info["total_score"] >= 4:
            return "Hot Lead"
          
        else:
            return "Cold Lead"
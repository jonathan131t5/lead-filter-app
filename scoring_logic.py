class MessageScorer:
    def __init__(self):
        pass
    
    
    def score_message(self , message_to_rank , field):
        rank_score = 0

        if message_to_rank["status"] == "found":
            if field == "budget":
                if float(message_to_rank["value"]) >= 450:
                    rank_score += 3
                elif 250 <= float(message_to_rank["value"]) <= 449:
                    rank_score += 2
                else:
                    rank_score += 1

            
            
            elif field == "goal":
                if 8 <= float(message_to_rank["value"]) <= 10:
                    rank_score += 3
                elif 5 <= float(message_to_rank["value"]) <= 7:
                    rank_score += 2
                else:
                    rank_score += 1
            
            
            elif field == "urgency":
                if 8 <= float(message_to_rank["value"]) <= 10:
                    rank_score += 3
                elif 5 <= float(message_to_rank["value"])  <= 7:
                    rank_score += 2
                else:
                    rank_score += 1
            

        
            return {"status" : "found" , "rank_score" : rank_score}
        
        return {"status" : "missing" , "rank_score" : rank_score}
    



    def score_follow_up_message(self , follow_up_rank):
        if follow_up_rank["lead_signal"] == "strong":
            return {"status" : "completed process" , "final" : "hot lead"}
        
        elif follow_up_rank["lead_signal"] == "cold":
            return {"status" : "completed process" , "final" : "cold lead"}
        
        else:
            return {"status" : "ongoing process" , "final" : "none"}

    

class LeadScoreManager:
    def __init__(self):
        pass

    
    
    def update_lead_score_info(self , lead_score_info , lead_message_score , message_field):
        if lead_message_score > 0:
            lead_score_info["score_count"] += 1
            lead_score_info["total_score"] += lead_message_score
            lead_score_info[message_field] = lead_message_score
        
        return lead_score_info
  
    

class LeadClassifier:
    def __init__(self):
        pass

    
    
    def classify_lead_score(self , lead_score_info):
        print(lead_score_info)
        
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
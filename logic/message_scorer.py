class MessageScorer:
    def __init__(self):
        pass
    
    
    def score_message(self , message_to_rank , field , reason):
        rank_score = 0


        if message_to_rank["status"] == "missing" or message_to_rank["status"] == "confused":
            if reason == "regular_fallback":
                return {"status" : "unknown"}
        
        
        elif message_to_rank["status"] == "found":
            if field == "budget":
                if float(message_to_rank["value"]) >= 400:
                    rank_score += 3
                elif 250 <= float(message_to_rank["value"]) <= 399:
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
            

                
            return {"status" : "valid" , "rank_score" : rank_score}
        
        return {"status" : "invaild" , "rank_score" : rank_score}
    



    def score_follow_up_message(self , follow_up_rank):
        if follow_up_rank["lead_signal"] == "strong":
            return {"status" : "completed process" , "final" : "hot lead"}
        
        elif follow_up_rank["lead_signal"] == "cold":
            return {"status" : "completed process" , "final" : "cold lead"}
        
        else:
            return {"status" : "ongoing process" , "final" : "none"}

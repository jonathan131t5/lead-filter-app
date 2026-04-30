class MessageScorer:
    def __init__(self):
        pass
    
    
    def score_message(self , message_to_rank , field , reason , phone_attempt_number):
        rank_score = 0


        if field == "preferences":
            return {"status" : "preferences"}
        
        if message_to_rank["status"] == "missing" or message_to_rank["status"] == "confused":
            if reason == "regular_fallback":
                return {"status" : "unknown" , "rank_score" : rank_score}
        

        elif message_to_rank["status"] == "found":
            
            if field == "goal":
                if 8 <= float(message_to_rank["value"]) <= 10:
                    rank_score += 3
                elif 5 <= float(message_to_rank["value"]) <= 7:
                    rank_score += 2
                else:
                    rank_score += 1

            
            if field == "phone":
                if phone_attempt_number <= 1:
                    rank_score += 100

                elif phone_attempt_number >= 2 and reason != "regular_fallback":
                    rank_score += 40
                
                else:
                    rank_score += 25
            
            
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

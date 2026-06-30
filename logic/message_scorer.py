class MessageScorer:
    def __init__(self):
        pass
    
    
    def score_message(self , message_to_rank , field , reason):
        rank_score = 0

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

            if field == "goal":
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
    






    def score_estate_message(self , message_to_rank , field , reason):
        rank_score = 0

        if message_to_rank["status"] == "missing" or message_to_rank["status"] == "confused":
            if reason == "regular_fallback":      
                return {"status" : "unknown" , "rank_score" : rank_score}
        

        elif message_to_rank["status"] == "found":
            
            if field == "budget_buy" or field == "budget_sell":
                if message_to_rank["value"] > 400000:
                    rank_score += 3
                elif 150000 < message_to_rank["value"] <= 400000:
                    rank_score += 2
                else:
                    rank_score += 1


                
            elif field == "budget_rent_renting" or field == "budget_rent_letting":
                if message_to_rank["value"] > 1500:
                    rank_score += 3
                elif 800 < message_to_rank["value"] <= 1500:
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




    def score_visa_message(self , message_to_rank , field , reason):
        rank_score = 0

        if message_to_rank["status"] == "missing" or message_to_rank["status"] == "confused":
            if reason == "regular_fallback":      
                return {"status" : "unknown" , "rank_score" : rank_score}
        

        elif message_to_rank["status"] == "found":
            
            if field == "eligibility":
                if message_to_rank["value"] == "yes":
                    rank_score += 2
                else:
                    return {"status" : "eligibility_failed" , "rank_score" : rank_score}

        
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

import random


def validate_int(value, name):  
    if value is None:
        raise ValueError(f"{name} cannot be None")
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} cannot be negative")

def validate_str(value, name):
    if value is None:
        raise ValueError(f"{name} cannot be None")
    if not value.strip():
        raise ValueError(f"{name} cannot be empty")
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")



class ServiceLayer:
    def __init__(self , conversation_builder , open_ai_client , data_access , message_scorer , lead_score_manager , lead_classifier , questions):
        self.conversation_builder = conversation_builder
        self.open_ai_client = open_ai_client
        self.data_access = data_access
        self.message_scorer = message_scorer
        self.lead_score_manager = lead_score_manager
        self.lead_classifier = lead_classifier
        self.questions = questions


        
        
        if conversation_builder is None:
            raise ValueError(f"Conversation Builder cannot be None")

        
        if open_ai_client is None:
            raise ValueError(f"OpenAI Client cannot be None")
    
        
        if data_access is None:
            raise ValueError(f"Data Access cannot be None")
        
        
        if message_scorer is None:
            raise ValueError(f"Message Scorer cannot be None")
        

        if lead_score_manager is None:
            raise ValueError(f"Lead Score Manager cannot be None")
        

        if lead_classifier is None:
            raise ValueError(f"Lead Classifier cannot be None")
    


    
    def process_lead_message(self , phone_number , content=None , name=None , mode=1):
        validate_str(phone_number , "phone_number")        
        
        get_or_create_lead = self.lead_exists_check(phone_number=phone_number)
        if get_or_create_lead is None:
            if mode == 1:
                return {"status" : "new"}
            else:
                validate_str(name , "name")
                get_or_create_lead = self.lead_exists_check(phone_number=phone_number , lead_name=name , new=True)
        
        if get_or_create_lead is not None and mode == 1:
            #print("here")
            return {"status" : "exist"}

        validate_str(content , "content")

        lead_id = get_or_create_lead["lead_id"]
        
        ensure_lead_tables = self.ensure_user_tables_exist(lead_id)
        
        lead_base_data = self.build_base_lead_data(base_data=get_or_create_lead)
        lead_scores_data = self.build_lead_scores_data(scores_data=ensure_lead_tables["lead_scores_data"])
        lead_fields_data = self.build_lead_fields_data(fields_data=ensure_lead_tables["lead_fields_data"])
        
        current_field = lead_base_data["current_field"]
        total_score = lead_scores_data["total_score"]
                
        
        ai_response = self.generate_analyze(lead_id=lead_id , content=content , current_field=current_field)
        
        
        self.apply_ai_result(ai_response=ai_response , lead_info=lead_base_data , content=content)

        self.apply_message_score(lead_info=lead_scores_data , current_field=current_field , ai_analyze_response=ai_response)
        

        finalize_lead_status = self.finalize_lead_status(lead_scores_data)
        if finalize_lead_status is not None:
            final_lead_status = finalize_lead_status["final_status"]

            if final_lead_status == "Hot Lead":
                summary_data = self.build_summary_data(base_data=lead_base_data , fields_data=lead_fields_data , total_score=total_score)
                self.process_lead_summary(summary_data)
        


        generate_ai_question = self.generate_question(lead_info=lead_base_data , ai_response=ai_response)
        if generate_ai_question is None:
            return {"status" : "DONE"}
        
        elif generate_ai_question["status"] == "invaild answer":
            get_or_create_lead = self.lead_exists_check(phone_number=phone_number)
            lead_base_data = self.build_base_lead_data(base_data=get_or_create_lead)
            print(lead_base_data["attempt_number"])
            print("good")
            question = self.build_next_response(lead_info=lead_base_data)
            
        elif generate_ai_question["status"] == "confused":
            question = generate_ai_question["question"]
        
        elif generate_ai_question["status"] == "valid answer":
            get_or_create_lead = self.lead_exists_check(phone_number=phone_number)
            lead_base_data = self.build_base_lead_data(base_data=get_or_create_lead)
            print(lead_base_data["attempt_number"])
            print("bad")
            question = self.build_next_response(lead_info=lead_base_data , ai_response=generate_ai_question["ai_response"] , mode="follow up")
        
        return {"status" : "in process" , "question" : question}

    

    
    def lead_exists_check(self , phone_number , lead_name=None , new=False):
        validate_str(phone_number , "phone number")

        if not new:
            lead_info_exist_check = self.data_access.get_lead_base_info(phone_number)
            if lead_info_exist_check is None:
                return
            else:
                return lead_info_exist_check
            
        if new:
            lead_info_exist_check = self.data_access.get_lead_base_info(phone_number)
            if lead_info_exist_check is None:
                validate_str(lead_name , "lead name")
                
                self.data_access.create_new_lead(phone_number=phone_number , name=lead_name)
                lead_info_exist_check = self.data_access.get_lead_base_info(phone_number)
            
            return lead_info_exist_check
        

    
    
    def ensure_user_tables_exist(self , lead_id):
        validate_int(lead_id , "lead id")

        lead_score_exist_check = self.data_access.get_lead_score_info(lead_id=lead_id)
        if lead_score_exist_check is None:
            self.data_access.create_new_lead_score(lead_id=lead_id)
            lead_score_exist_check = self.data_access.get_lead_score_info(lead_id=lead_id)
        
        
        lead_fields_data_check = self.data_access.get_all_lead_field_data(lead_id=lead_id)
        if lead_fields_data_check is None:
            self.data_access.create_new_fields_data(lead_id=lead_id)
            lead_fields_data_check = self.data_access.get_all_lead_field_data(lead_id=lead_id)

        
        return {
            "lead_scores_data" : lead_score_exist_check , 
            "lead_fields_data" : lead_fields_data_check
        }
    

    

    def build_base_lead_data(self , base_data):
        return {
            "phone_number" : base_data["phone_number"] , 
            "lead_id" : base_data["lead_id"] ,
            "name" : base_data["name"] , 
            "current_field" : base_data["current_field"] , 
            "attempt_number" : base_data["attempt_number"] , 
            "status" : base_data["status"] , 
            "summary" : base_data["summary"] 
            }
    

    def build_lead_scores_data(self , scores_data):
        return {
                "lead_id" : scores_data["lead_id"] ,
                "total_score" : scores_data["total_score"] , 
                "score_count" : scores_data["score_count"] ,
                "goal_score" : scores_data["goal_score"] , 
                "budget_score" : scores_data["budget_score"] ,
                "urgency_score" : scores_data["urgency_score"]
            }
    

    
    def build_lead_fields_data(self , fields_data):
        return {
        "lead_id" : fields_data["lead_id"] , 
        "goal_user" : fields_data["goal_user"] ,
        "budget_user" : fields_data["budget_user"] ,
        "urgency_user" : fields_data["urgency_user"]
    }


    
    def build_summary_data(self , base_data , fields_data , total_score):
        return {
            "phone_number" : base_data["phone_number"] , 
            "lead_id" : base_data["lead_id"] ,
            "name" : base_data["name"] , 
            "goal_user" : fields_data["goal_user"] , 
            "budget_user" : fields_data["budget_user"] ,
            "urgency_user" : fields_data["urgency_user"] ,
            "total_score" : total_score["total_score"] ,
        }
        




    def generate_analyze(self , lead_id , current_field , content):
        ai_input = self.conversation_builder.analyze_prompt(current_field=current_field , content=content)
        ai_response = self.open_ai_client.ai_reply(ai_input)
        
        self.data_access.add_lead_message(lead_id=lead_id , role="user" , content=content)
        
        print(ai_response)
        return ai_response

    
    
    def generate_question(self , lead_info , ai_response=None):
        #validate_str(content , "content")


        if lead_info["status"] != "pending":
            return {"status" : "DONE"}
        
        #print(lead_info["current_field"])
        #print(lead_info["attempt_number"])

        
        if ai_response is None:
            question = self.questions.process_questions(mode=lead_info["current_field"] , attempt_number=lead_info["attempt_number"])
        
        elif ai_response["status"] == "missing":
            return {"status" : "invaild answer"}
        
        elif ai_response["status"] == "found":
            return {"status" : "valid answer" , "ai_response" : ai_response}
    

        elif ai_response["status"] == "confused":
            question = ai_response["clarify"]
            return {"status" : "confused" , "question" : question}
        
        self.data_access.add_lead_message(lead_id=lead_info["lead_id"] , role="bot" , content=question)

        



    def build_next_response(self , lead_info , ai_response=None , mode="regular"):
        if mode == "regular":
            return self.questions.process_questions(mode=lead_info["current_field"] , attempt_number=lead_info["attempt_number"])
        
        elif mode == "follow up":
            separators = [
            ". ",
            ", ",
            " - ",
            " — ",
            " "
            ]
            sep = random.choice(separators)

            build_question = self.questions.process_questions(mode=lead_info["current_field"] , attempt_number=lead_info["attempt_number"])
            return f"{ai_response['ack']}{sep} {build_question}"


    
    def advance_on_found(self , ai_response , lead_info , content):
        if ai_response["status"] == "found":
            if lead_info["current_field"] == "goal":
                lead_info["current_field"] = "budget"
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="goal_user" , value=content)

            elif lead_info["current_field"] == "budget":
                lead_info["current_field"] = "urgency"
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="budget_user" , value=content)

            elif lead_info["current_field"] == "urgency":
                lead_info["current_field"] = None
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="urgency_user" , value=content)

            return {"status" : "advanced"}
    
    
    def handle_unresolved_flow(self , ai_response , lead_info):
        if ai_response["status"] == "missing":
            if lead_info["regular_attempt_number"] >= 2:
                

    
    
    def apply_ai_result(self , ai_response , lead_info , content):
        if ai_response["status"] == "found":
            if lead_info["current_field"] == "goal":
                lead_info["current_field"] = "budget"
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="goal_user" , value=content)

            elif lead_info["current_field"] == "budget":
                lead_info["current_field"] = "urgency"
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="budget_user" , value=content)

            elif lead_info["current_field"] == "urgency":
                lead_info["current_field"] = None
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="urgency_user" , value=content)
            
            
            self.data_access.update_lead_current_field(lead_info["lead_id"] , updated_field=lead_info["current_field"])
            self.data_access.update_lead_attempt_number(lead_id=lead_info["lead_id"] , number=1)

    
        if ai_response["status"] == "missing":
            self.data_access.update_lead_attempt_number(lead_id=lead_info["lead_id"] , number=lead_info["regular_attempt_number"] + 1)


    
    
    def apply_message_score(self , lead_info , current_field , ai_analyze_response):
        #print("here")
        lead_message_score = self.message_scorer.score_message(message_to_rank=ai_analyze_response , field=current_field)
        
        if lead_message_score["status"] == "missing":
            return

        self.lead_score_manager.update_lead_score_info(lead_score_info=lead_info , lead_message_score=lead_message_score["rank_score"] , message_field=f"{current_field}_score")
        self.data_access.update_lead_score_info(lead_id=lead_info["lead_id"] , score_count=lead_info["score_count"] , total_score=lead_info["total_score"] , score_field=f"{current_field}_score" , value=lead_message_score["rank_score"])


    
    def finalize_lead_status(self , lead_info):
        #print("here")
        if lead_info["score_count"] == 3:
            final_lead_status = self.lead_classifier.classify_lead_score(lead_info)
            
            if final_lead_status:
                self.data_access.set_lead_status(lead_info["lead_id"] , final_lead_status)
                return {"final_status" : final_lead_status}
            
        return 


    
    def process_lead_summary(self , summary_info):
        summary_info["budget_user"] = self.format_currency(summary_info=["budget_user"])

        final_summary = self.generate_lead_summary(summary_info)

        self.upload_lead_summary(summary=final_summary , lead_id=summary_info["lead_id"])

    
    
    def format_currency(self , budget_text):
        currency_symbols = ["₪", "שקל", "שח", 'ש"ח' , "שקלים"]

        if not any(symbol in budget_text for symbol in currency_symbols):
            budget_text = budget_text.strip() + " ₪"

        return budget_text



    def generate_lead_summary(self , summary_info):
        text = (
            f"🔥 ליד חם חדש:\n\n"
            f"{summary_info['name']} פנה לגבי אימונים.\n\n"
            f"מטרה: {summary_info['goal_user']}\n"
            f"תקציב: {summary_info['budget_user']} לחודש\n"
            f"זמן התחלה: {summary_info['urgency_user']}\n\n"
            f"ציון התאמה: {summary_info['total_score']}\n"
            f"טלפון: {summary_info['phone_number']}"
            )
        
        return text
    

    
    def upload_lead_summary(self , summary , lead_id):
        self.data_access.upload_summary(lead_summary=summary , lead_id=lead_id)
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
    def __init__(self , conversation_builder , open_ai_client , data_access , message_scorer , lead_score_manager , lead_classifier , process_question):
        self.conversation_builder = conversation_builder
        self.open_ai_client = open_ai_client
        self.data_access = data_access
        self.message_scorer = message_scorer
        self.lead_score_manager = lead_score_manager
        self.lead_classifier = lead_classifier
        self.process_question = process_question


        
        
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
    


    
    def prepare_lead_context(self , phone_number , name=None , mode=1):
        validate_str(phone_number , "phone_number")        
        
        get_or_create_lead = self.lead_exists_check(phone_number=phone_number)
        if get_or_create_lead is None:
            if mode == 1:
                return {"status" : "new"}
            else:
                validate_str(name , "name")
                get_or_create_lead = self.lead_exists_check(phone_number=phone_number , lead_name=name , new=True)

        lead_id = get_or_create_lead["lead_id"]
        
        ensure_lead_tables = self.ensure_user_tables_exist(lead_id=lead_id)

        return {
            "lead_base_data" : get_or_create_lead , 
            "lead_conversation_states_data" : ensure_lead_tables["lead_conversation_states_data"] , 
            "lead_scores_data" : ensure_lead_tables["lead_scores_data"] , 
            "lead_fields_data" : ensure_lead_tables["lead_fields_data"] , 

        }
    
    
    def process_lead_message(self , lead_all_data , content , mode="output"):
        lead_id = lead_all_data["lead_base_data"]["lead_id"]
        current_field = lead_all_data["lead_conversation_states_data"]["current_field"]
        
        if mode == "output":
            question = self.generate_question(lead_all_data["lead_conversation_states_data"])
            if question is None:
                return {"status" : "DONE"}
            
            return {"status" : "output" , "question" : question}
        

        ai_response = self.generate_analyze(lead_id=lead_id , content=content , current_field=current_field)
        
        
        flow_status = self.advance_on_found(ai_response=ai_response , lead_info=lead_all_data["lead_conversation_states_data"] , content=content)
        if flow_status == False:
            unresolved_status = self.handle_unresolved_flow(lead_all_data["lead_conversation_states_data"] ,  ai_response=ai_response)
            if unresolved_status == False:
                self.handle_unresolved_fallbacks(lead_info=lead_all_data["lead_conversation_states_data"] , ai_response=ai_response)

        self.apply_message_score(current_field=current_field , lead_info=lead_all_data["lead_scores_data"] , ai_analyze_response=ai_response)

        finalize_lead_status = self.finalize_lead_status(lead_info=lead_all_data["lead_scores_data"])
        if finalize_lead_status is not None:
            final_lead_status = finalize_lead_status["final_status"]

            if final_lead_status == "Hot Lead":
                summary_context = self.data_access.prepare_lead_summary_context(lead_id=lead_id)
                self.process_lead_summary(summary_info=summary_context)
        
        return {"status" : "in process"}


    
    def lead_exists_check(self , phone_number , lead_name=None , new=False):
        validate_str(phone_number , "phone number")

        if not new:
            lead_info_exist_check = self.data_access.get_lead_base_data(phone_number)
            if lead_info_exist_check is None:
                return
            else:
                return lead_info_exist_check
            
        if new:
            lead_info_exist_check = self.data_access.get_lead_base_data(phone_number)
            if lead_info_exist_check is None:
                validate_str(lead_name , "lead name")
                
                self.data_access.create_new_lead(phone_number=phone_number , name=lead_name)
                lead_info_exist_check = self.data_access.get_lead_base_data(phone_number)
            
            return lead_info_exist_check
        

    
    
    def ensure_user_tables_exist(self , lead_id):
        validate_int(lead_id , "lead id")

        lead_score_exist_check = self.data_access.get_lead_score_data(lead_id=lead_id)
        if lead_score_exist_check is None:
            self.data_access.create_new_lead_score(lead_id=lead_id)
            lead_score_exist_check = self.data_access.get_lead_score_data(lead_id=lead_id)
        
        
        lead_fields_data_check = self.data_access.get_all_lead_field_data(lead_id=lead_id)
        if lead_fields_data_check is None:
            self.data_access.create_new_lead_fields_data(lead_id=lead_id)
            lead_fields_data_check = self.data_access.get_all_lead_field_data(lead_id=lead_id)


        lead_conversation_states_check = self.data_access.get_lead_conversation_states(lead_id=lead_id)
        if lead_conversation_states_check is None:
            self.data_access.create_new_lead_conversation_states_data(lead_id=lead_id)
            lead_conversation_states_check = self.data_access.get_lead_conversation_states
        
        return {
            "lead_scores_data" : lead_score_exist_check , 
            "lead_fields_data" : lead_fields_data_check ,
            "lead_conversation_states_data" : lead_conversation_states_check

        }
    
    
    def generate_analyze(self , lead_id , current_field , content):
        ai_input = self.conversation_builder.analyze_prompt(current_field=current_field , content=content)
        ai_response = self.open_ai_client.ai_reply(ai_input)
        
        self.data_access.add_lead_message(lead_id=lead_id , role="user" , content=content)
        
        print(ai_response)
        return ai_response

    
    
    
    def generate_question(self , lead_info):
        if lead_info["final_status"] != "pending":
            return {"status" : "DONE"}
        
        question = self.process_question.get_question(
            field=lead_info["current_field"] , 
            question_state=lead_info["question_state"] , 
            reason=lead_info["reason"] , 
            attempt_number=lead_info["regular_attempt_number"])

        return question

        
        #print(lead_info["current_field"])
        #print(lead_info["attempt_number"])

        


    
    def advance_on_found(self , ai_response , lead_info , content):
        need_to_change = None
        
        if ai_response["status"] == "found":
            if lead_info["current_field"] == "goal":
                lead_info["current_field"] = "budget"
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="goal_user" , value=content)

            elif lead_info["current_field"] == "budget":
                lead_info["current_field"] = "urgency"
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="budget_user" , value=content)

            elif lead_info["current_field"] == "urgency":
                need_to_change = True
                lead_info["current_field"] = None
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="urgency_user" , value=content)

            self.data_access.update_lead_current_field(lead_id=lead_info["lead_id"] , updated_field=lead_info["current_field"])
            self.data_access.update_lead_regular_attempt_number(lead_id=lead_info["lead_id"] , number=1)
            self.data_access.update_lead_confuse_attempt_number(lead_id=lead_info["lead_id"] , number=1)

            if need_to_change is None:
                self.data_access.update_lead_question_state(lead_id=lead_info["lead_id"] , value="base")
                self.data_access.update_lead_question_reason(lead_id=lead_info["lead_id"] , value="base")

            else:
                self.data_access.update_lead_question_state(lead_id=lead_info["lead_id"] , value=None)
                self.data_access.update_lead_question_reason(lead_id=lead_info["lead_id"] , value=None)

            return True

        return False
    
    
    
    def handle_unresolved_flow(self , ai_response , lead_info):
        if ai_response["status"] == "missing" or ai_response["status"] == "confuse":
            if lead_info["regular_attempt_number"] >= 2 or lead_info["confuse_attempt_number"] >= 2:
                if lead_info["question_state"] == "fallback" and lead_info["question_reason"] == "regular_fallback":
                    return False    
                
                self.data_access.update_lead_question_state(lead_id=lead_info["lead_id"] , value="fallback")
                self.data_access.update_lead_question_reason(lead_id=lead_info["lead_id"] , value="regular_fallback")

        
            elif lead_info["regular_attempt_number"] <= 1 or lead_info["confuse_attempt_number"] <= 1:
                if lead_info["question_state"] == "fallback" and lead_info["question_reason"] == "regular_fallback":
                    return False  
                
                elif ai_response["status"] == "missing":
                    self.data_access.update_lead_regular_attempt_number(lead_id=lead_info["lead_id"] , number=lead_info["regular_attempt_number"] + 1)
                
                elif ai_response["status"] == "confuse":
                    self.data_access.update_lead_confuse_attempt_number(lead_id=lead_info["lead_id"] , number=lead_info["confuse_attempt_number"] + 1)
                
                self.data_access.update_lead_question_state(lead_id=lead_info["lead_id"] , value=ai_response["status"])
                self.data_access.update_lead_question_reason(lead_info["lead_id"] , ai_response["reason"])
                
            return True
        
    
    
    def handle_unresolved_fallbacks(self , ai_response , lead_info):
        if ai_response["status"] == "missing" or ai_response["status"] == "confuse":
            if lead_info["question_reason"] == "regular_fallback":
                self.data_access.update_lead_question_reason(lead_id=lead_info["led_id"] , value="after_fallback")
                
            
    
    
    def apply_message_score(self , lead_info , current_field , ai_analyze_response):
        lead_message_score = self.message_scorer.score_message(message_to_rank=ai_analyze_response , field=current_field)
        
        if lead_message_score["status"] == "invaild":
            return

        self.lead_score_manager.update_lead_score_info(lead_score_info=lead_info , lead_message_score=lead_message_score["rank_score"] , message_field=f"{current_field}_score")
        self.data_access.update_lead_score_info(lead_id=lead_info["lead_id"] , score_count=lead_info["score_count"] , total_score=lead_info["total_score"] , score_field=f"{current_field}_score" , value=lead_message_score["rank_score"])


    
    def finalize_lead_status(self , lead_info):
        #print("here")
        if lead_info["score_count"] == 3:
            final_lead_status = self.lead_classifier.classify_lead_score(lead_info)
            
            if final_lead_status:
                self.data_access.set_lead_final_status(lead_info["lead_id"] , final_lead_status)
                return {"final_status" : final_lead_status}
            
        return 


    
    def process_lead_summary(self , summary_info):
        summary_info["budget_user"] = self.format_currency(summary_info=["budget_user"])

        final_summary = self.generate_lead_summary(summary_info)

        self.upload_summary(lead_summary=final_summary , lead_id=summary_info["lead_id"])

    
    
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













service_layer = ServiceLayer()


phone_number = None
new_lead = False
welcome_message = False

while True:
    #try:
    print("""
        =================================
                LEAD FILTER ENGINE
        =================================

            Analyze • Score • Classify
        """)
    
    

    if phone_number is None:
        phone_number = input("כדי להתחיל או להמשיך מאיפה שעצרת, מה המספר שלך: ")


    prepare_lead_context = service_layer.prepare_lead_context(phone_number=phone_number)
    if prepare_lead_context["status"] == "new":
        name = input("Please enter your name: ")
        validate_str(name , "name")

        prepare_lead_context = service_layer.prepare_lead_context(phone_number=phone_number , name=name , mode=2)


    content = input("Please enter your message: ")

    message_process = service_layer.process_lead_message(lead_all_data=prepare_lead_context , phone_number=phone_number , content=content)
    
    if message_process["status"] == "DONE":
        print(f"Thank you for your cooperation. We will contact you soon")
        break
    
    elif message_process["status"] == "output":
        print(message_process["question"])
        message_process = service_layer.process_lead_message(lead_all_data=prepare_lead_context , phone_number=phone_number , content=content , mode="input")
    

        


    #print(message_process)
    #print("here")
    
        

    

    #except Exception as e:
        #print(f"Error: {e}")
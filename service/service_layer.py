import random
from bidi.algorithm import get_display

from data_access.leads_data_repository import LeadsDataRepository
from data_access.leads_states_repository import LeadsStatesRepository
from data_access.leads_scores_repository import LeadsScoresRepository
from data_access.leads_fields_repository import LeadsFieldsRepository
from data_access.leads_messages_repository import MessagesRepository
from data_access.lead_summary_context_repository import LeadSummaryContextRepository

from data_base.connection import Connection

from logic.ai_result_handler import OpenAIClient
from logic.lead_classifier import LeadClassifier
from logic.message_scorer import MessageScorer
from logic.lead_score_manager import LeadScoreManager

from output_builders.analyze_prompt_builder import ConversationBuilder
from output_builders.questions_builder import (
    ProcessQuestion,
    BaseQuestions,
    MissingQuestions,
    ConfuseQuestions,
    FallBackQuestions
)

from utils.validators import validate_int, validate_str , validate_phone_number



class ServiceLayer:
    def __init__(self):
        self.db = Connection()
        
        self.leads_data = LeadsDataRepository(self.db.cursor)
        self.leads_states = LeadsStatesRepository(self.db.cursor)
        self.leads_scores = LeadsScoresRepository(self.db.cursor)
        self.leads_fields = LeadsFieldsRepository(self.db.cursor)
        self.messages = MessagesRepository(self.db.cursor)
        self.summary_context = LeadSummaryContextRepository(self.db.cursor)
        self.openai_client = OpenAIClient()
        self.lead_classifier = LeadClassifier()
        self.message_scorer = MessageScorer()
        self.lead_score_manager = LeadScoreManager()
        self.conversation_builder = ConversationBuilder()
        self.process_question = ProcessQuestion(base_questions=BaseQuestions() , missing_questions=MissingQuestions() , confuse_questions=ConfuseQuestions() , fallback_questions=FallBackQuestions())


        

    
    def prepare_lead_context(self , phone_number , name=None , mode=1):
        validate_phone_number(phone_number , "phone_number")        
        
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
    
    
    def process_lead_message(self , lead_all_data , content=None , mode="output" , ack_mode=0):        
        lead_id = lead_all_data["lead_base_data"]["lead_id"]
        current_field = lead_all_data["lead_conversation_states_data"]["current_field"]
        question_reason = lead_all_data["lead_conversation_states_data"]["question_reason"]
        final_status = lead_all_data["lead_base_data"]["final_status"]
        urgency_status = lead_all_data["lead_scores_data"]["urgency_status"]
        name = lead_all_data["lead_base_data"]["name"]


        if mode == "output":
            question = self.generate_question(lead_info=lead_all_data["lead_conversation_states_data"] , ack_mode=ack_mode , final_status=final_status)
            if question is None:
                closing_message = self.closing_message(final_status=final_status , urgency_status=urgency_status , name=name)
                return {"status" : "DONE" , "closing_message" : closing_message}
            
            return {"status" : "output" , "question" : question}
        

        ai_response = self.generate_analyze(lead_id=lead_id , content=content , current_field=current_field)
        
        
        flow_status = self.advance_on_found(ai_response=ai_response , lead_info=lead_all_data["lead_conversation_states_data"] , content=content)
        if flow_status == False:
            unresolved_status = self.handle_unresolved_flow(lead_info=lead_all_data["lead_conversation_states_data"] ,  ai_response=ai_response)
            if unresolved_status == False:
                self.handle_unresolved_fallbacks(lead_info=lead_all_data["lead_conversation_states_data"] , ai_response=ai_response)

        score_process_status = self.apply_message_score(current_field=current_field , lead_info=lead_all_data["lead_scores_data"] , ai_analyze_response=ai_response , reason=question_reason)
        if score_process_status is None:
            self.db.commit()
            return 
        
        finalize_lead_status = self.finalize_lead_status(lead_info=lead_all_data["lead_scores_data"])
        if finalize_lead_status is not None:
            lead_all_data["lead_base_data"]["final_status"] = finalize_lead_status["final_status"]
            summary_context = self.summary_context.prepare_lead_summary_context(lead_id=lead_id)
            self.process_lead_summary(summary_info=summary_context)

        self.db.commit()
        return {"status" : "in process"}


    
    def lead_exists_check(self , phone_number , lead_name=None , new=False):
        validate_phone_number(phone_number , "phone number")

        if not new:
            lead_info_exist_check = self.leads_data.get_lead_base_data(phone_number)
            if lead_info_exist_check is None:
                return
            else:
                return lead_info_exist_check
            
        if new:
            lead_info_exist_check = self.leads_data.get_lead_base_data(phone_number)
            if lead_info_exist_check is None:
                validate_str(lead_name , "lead name")
                
                self.leads_data.create_new_lead(phone_number=phone_number , name=lead_name)
                lead_info_exist_check = self.leads_data.get_lead_base_data(phone_number)
            
            return lead_info_exist_check
        

    
    
    def ensure_user_tables_exist(self , lead_id):
        validate_int(lead_id , "lead id")

        lead_score_exist_check = self.leads_scores.get_lead_score_data(lead_id=lead_id)
        if lead_score_exist_check is None:
            self.leads_scores.create_new_lead_score(lead_id=lead_id)
            lead_score_exist_check = self.leads_scores.get_lead_score_data(lead_id=lead_id)
        
        
        lead_fields_data_check = self.leads_fields.get_all_lead_field_data(lead_id=lead_id)
        if lead_fields_data_check is None:
            self.leads_fields.create_new_lead_fields_data(lead_id=lead_id)
            lead_fields_data_check = self.leads_fields.get_all_lead_field_data(lead_id=lead_id)


        lead_conversation_states_check = self.leads_states.get_lead_conversation_states(lead_id=lead_id)
        if lead_conversation_states_check is None:
            self.leads_states.create_new_lead_conversation_states_data(lead_id=lead_id)
            lead_conversation_states_check = self.leads_states.get_lead_conversation_states(lead_id=lead_id)
        
        return {
            "lead_scores_data" : lead_score_exist_check , 
            "lead_fields_data" : lead_fields_data_check ,
            "lead_conversation_states_data" : lead_conversation_states_check

        }
    
    
    def generate_analyze(self , lead_id , current_field , content):
        ai_input = self.conversation_builder.main_analyze_prompt(current_field=current_field , content=content)
        ai_response = self.openai_client.ai_reply(ai_input)
        
        self.messages.add_lead_message(lead_id=lead_id , role="user" , content=content)
        print(ai_response)
        return ai_response

    
    
    
    def generate_question(self , lead_info , ack_mode , final_status):
        if final_status != "pending":
            return None
        
        question = self.process_question.get_question(
            field=lead_info["current_field"] , 
            question_state=lead_info["question_state"] , 
            reason=lead_info["question_reason"] , 
            attempt_number=lead_info["regular_attempt_number"],
            ack_mode=ack_mode)

        self.messages.add_lead_message(lead_id=lead_info["lead_id"] , role="assistant" , content=question)
        return question



    
    def advance_on_found(self , ai_response , lead_info , content):
        need_to_change = None
        
        if ai_response["status"] == "found":
            if lead_info["current_field"] == "goal":
                lead_info["current_field"] = "budget"
                self.leads_fields.update_lead_field_data(lead_id=lead_info["lead_id"] , field="goal_user" , value=content)

            elif lead_info["current_field"] == "budget":
                lead_info["current_field"] = "urgency"
                self.leads_fields.update_lead_field_data(lead_id=lead_info["lead_id"] , field="budget_user" , value=content)

            elif lead_info["current_field"] == "urgency":
                need_to_change = True
                lead_info["current_field"] = None
                self.leads_fields.update_lead_field_data(lead_id=lead_info["lead_id"] , field="urgency_user" , value=content)

            self.leads_states.update_lead_current_field(lead_id=lead_info["lead_id"] , updated_field=lead_info["current_field"])
            self.leads_states.update_lead_regular_attempt_number(lead_id=lead_info["lead_id"] , number=1)
            self.leads_states.update_lead_confuse_attempt_number(lead_id=lead_info["lead_id"] , number=1)

            if need_to_change is None:
                self.leads_states.update_lead_question_state(lead_id=lead_info["lead_id"] , value="base")
                self.leads_states.update_lead_question_reason(lead_id=lead_info["lead_id"] , value="base")

            else:
                self.leads_states.update_lead_question_state(lead_id=lead_info["lead_id"] , value=None)
                self.leads_states.update_lead_question_reason(lead_id=lead_info["lead_id"] , value=None)

            return True

        return False
    
    
    
    def handle_unresolved_flow(self , ai_response , lead_info):
        if ai_response["status"] == "missing" or ai_response["status"] == "confused":
            if lead_info["regular_attempt_number"] >= 2 or lead_info["confuse_attempt_number"] >= 2:
                if lead_info["question_state"] == "fallback" and lead_info["question_reason"] == "regular_fallback":
                    return False    
                
                if lead_info["question_reason"] != "after_fallback":
                    self.leads_states.update_lead_question_state(lead_id=lead_info["lead_id"] , value="fallback")
                    self.leads_states.update_lead_question_reason(lead_id=lead_info["lead_id"] , value="regular_fallback")

                    lead_info["question_state"] = "fallback"
                    lead_info["question_reason"] = "regular_fallback"
        
            
            elif lead_info["regular_attempt_number"] <= 1 or lead_info["confuse_attempt_number"] <= 1:
                if lead_info["question_state"] == "fallback" and lead_info["question_reason"] == "regular_fallback":
                    return False  
                
                elif ai_response["status"] == "missing":
                    self.leads_states.update_lead_regular_attempt_number(lead_id=lead_info["lead_id"] , number=lead_info["regular_attempt_number"] + 1)
                    lead_info["regular_attempt_number"] = lead_info["regular_attempt_number"] + 1
                
                elif ai_response["status"] == "confused":
                    self.leads_states.update_lead_confuse_attempt_number(lead_id=lead_info["lead_id"] , number=lead_info["confuse_attempt_number"] + 1)
                    lead_info["confuse_attempt_number"] = lead_info["confuse_attempt_number"] + 1

                self.leads_states.update_lead_question_state(lead_id=lead_info["lead_id"] , value=ai_response["status"])
                self.leads_states.update_lead_question_reason(lead_info["lead_id"] , ai_response["reason"])
  
            return True
        
    
    
    def handle_unresolved_fallbacks(self , ai_response , lead_info):
        if ai_response["status"] == "missing" or ai_response["status"] == "confused":
            if lead_info["question_reason"] == "regular_fallback":
                self.leads_states.update_lead_question_reason(lead_id=lead_info["lead_id"] , value="after_fallback")
                lead_info["question_reason"] = "after_fallback"
                
                if lead_info["current_field"] == "goal":
                    self.leads_states.update_lead_current_field(lead_id=lead_info["lead_id"] , updated_field="budget")
                    lead_info["current_field"] = "budget"
                
                elif lead_info["current_field"] == "budget":
                    self.leads_states.update_lead_current_field(lead_id=lead_info["lead_id"] , updated_field="urgency")
                    lead_info["current_field"] = "urgency"

                elif lead_info["current_field"] == "urgency":
                    self.leads_states.update_lead_current_field(lead_id=lead_info["lead_id"] , updated_field=None)
                    lead_info["current_field"] = None

                self.leads_states.update_lead_regular_attempt_number(lead_id=lead_info["lead_id"] , number=1)
                self.leads_states.update_lead_confuse_attempt_number(lead_id=lead_info["lead_id"] , number=1)

                lead_info["regular_attempt_number"] = 1
                lead_info["confuse_attempt_number"] = 1
    
    
    def apply_message_score(self , lead_info , current_field , ai_analyze_response , reason):
        lead_message_score = self.message_scorer.score_message(message_to_rank=ai_analyze_response , field=current_field , reason=reason)
        
        if lead_message_score["status"] == "invaild":
            return

        if lead_message_score["status"] == "unknown":
            self.lead_score_manager.update_lead_score_info(lead_score_info=lead_info , lead_message_score=lead_message_score["status"] , message_field=f"{current_field}_status")
            self.leads_scores.update_lead_score_info(lead_id=lead_info["lead_id"] , score_count=lead_info["score_count"] , total_score=lead_info["total_score"] , score_field=f"{current_field}_status" , value=lead_message_score["status"])

        else:
            self.lead_score_manager.update_lead_score_info(lead_score_info=lead_info , lead_message_score=lead_message_score["rank_score"] , message_field=f"{current_field}_score")
            self.leads_scores.update_lead_score_info(lead_id=lead_info["lead_id"] , score_count=lead_info["score_count"] , total_score=lead_info["total_score"] , score_field=f"{current_field}_score" , value=lead_message_score["rank_score"])


        return True


    
    def finalize_lead_status(self , lead_info):
        if lead_info["score_count"] == 3:
            final_lead_status = self.lead_classifier.classify_lead_score(lead_info)
            
            if final_lead_status:
                self.leads_data.set_lead_final_status(lead_info["lead_id"] , final_lead_status)
                return {"final_status" : final_lead_status}
            
        return 

    
    def closing_message(self , final_status , name , urgency_status):
        urgency_close_message = "סבבה, קיבלתי כיוון טוב ממה שכתבת."
        if final_status == "Hot Lead":
            closinge_message = (f"תודה על שיתוף {name}, זה נותן תמונה ברורה על מה שאתה מחפש.\n"
                    "נראה שיש התאמה טובה, וניצור איתך קשר בקרוב כדי להמשיך משם בצורה מסודרת.")
    
        elif final_status == "Cold Lead":
            closinge_message = (f"תודה על המידע {name}, זה נותן תמונה כללית.\n"
                    "כרגע זה פחות מתאים, ואם זה יהיה רלוונטי בהמשך ניצור איתך קשר.")
        else:
            raise ValueError("Invaild final status")
        
        if urgency_status == "unknown":
            return f"{urgency_close_message} {closinge_message}"
        
        return closinge_message
    


    
    def process_lead_summary(self , summary_info):
        summary_info["budget_user"] = self.format_currency(budget_text=summary_info["budget_user"])
        
        summary_info = self.field_unknown_check(summary_info=summary_info)

        final_status_context = self.generate_final_status_context(summary_info=summary_info)
        
        final_summary = self.generate_lead_summary(summary_info=summary_info , final_status_context=final_status_context)

        self.upload_lead_summary(summary=final_summary , lead_id=summary_info["lead_id"])

    
    
    def format_currency(self , budget_text):
        currency_symbols = ["₪", "שקל", "שח", 'ש"ח' , "שקלים"]

        if not any(symbol in budget_text for symbol in currency_symbols):
            budget_text = budget_text.strip() + " ₪"
        if "חודש" not in budget_text:
            budget_text = budget_text.strip() + " לחודש"
        
        return budget_text



    def field_unknown_check(self , summary_info):
        if summary_info["goal_status"] == "unknown":
            summary_info["goal_user"] = "לא סופק על ידי הלקוח"
        
        if summary_info["budget_status"] == "unknown":
            summary_info["budget_user"] = "לא סופק על ידי הלקוח"

        if summary_info["urgency_status"] == "unknown":
            summary_info["urgency_user"] = "לא סופק על ידי הלקוח"

        return summary_info


    def generate_final_status_context(self , summary_info):
        if summary_info["final_status"] == "Hot Lead":
            final_status_context = "ליד חם חדש 🔥"
        elif summary_info["final_status"] == "Cold Lead":
            final_status_context = "ליד קר חדש 🧊"

        elif summary_info["final_status"] == "pending":
            final_status_context = "ליד בתהליך ⏳"
        
        return final_status_context
    
    def generate_lead_summary(self , summary_info , final_status_context):
        text = (
            f"{final_status_context}\n\n"
            f"{summary_info['name']} פנה לגבי אימונים.\n\n"
            f"מטרה: {summary_info['goal_user']}\n"
            f"תקציב: {summary_info['budget_user']}\n"
            f"זמן התחלה: {summary_info['urgency_user']}\n\n"
            f"ציון התאמה: {summary_info['total_score']}\n"
            f"טלפון: {summary_info['phone_number']}"
            )
        
        return text
    

    
    def upload_lead_summary(self , summary , lead_id):
        self.leads_data.upload_summary(lead_summary=summary , lead_id=lead_id)



if __name__ == "__main__":
    service_layer = ServiceLayer()

    phone_number = None
    ack_mode = 0

    service_layer.leads_data.create_leads_data_table()
    service_layer.leads_states.create_lead_conversation_states()
    service_layer.leads_scores.create_leads_scores_table()
    service_layer.leads_fields.create_leads_fields_data()
    service_layer.messages.create_leads_messages_table()

    while True:
        try:
            print("""
                =================================
                        LEAD FILTER ENGINE
                =================================

                    Analyze • Score • Classify
                """)

            if phone_number is None:
                phone_number = input("שנייה לפני שמתחילים, כדי לשמור לך את ההתקדמות ולהמשיך איתך — מה המספר שלך?: ")
                validate_phone_number(phone_number=phone_number)

            prepare_lead_context = service_layer.prepare_lead_context(phone_number=phone_number)
            if "status" in prepare_lead_context:
                if prepare_lead_context["status"] == "new":
                    name = input("מעולה, איך קוראים לך?: ")
                    validate_str(name, "name")
                    prepare_lead_context = service_layer.prepare_lead_context(phone_number=phone_number, name=name, mode=2)

            message_process = service_layer.process_lead_message(lead_all_data=prepare_lead_context)

            ack_mode = 1

            if message_process["status"] == "DONE":
                closing_message = message_process["closing_message"]
                fixed = get_display(closing_message)
                print(fixed)
                break

            elif message_process["status"] == "output":
                question = message_process["question"]
                fixed = get_display(question)
                print(fixed)
                content = input("Please enter your message: ")
                message_process = service_layer.process_lead_message(
                    lead_all_data=prepare_lead_context,
                    content=content,
                    mode="input"
                )

        except Exception as e:
            print(f"Error: {e}")
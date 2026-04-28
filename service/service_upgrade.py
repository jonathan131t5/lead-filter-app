
from datetime import datetime, timezone
import sqlite3
import traceback
import logging


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

from utils.validators import validate_int, validate_str, extract_phone
from utils.validators import UserError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [APP] %(message)s"
)



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


    def process_lead_message(self , session_id , name=None , content=None):
        try:
            logging.info(
            f"[NEW MESSAGE] session_id={session_id} | "
            f"name_provided={name is not None} | "
            f"content_len={len(content) if content else 0}"
        )
            
            if content is not None:
                content = content.strip()[:100]

            if name is not None:
                name = name.strip()[:100]
            
            init_result = self.initialize_lead_context(session_id=session_id , name=name)
            
            if init_result.get("status") == "new":
                logging.info(f"New user detected session_id={session_id}")
                return init_result
            
            
            result = self.run_lead_flow(prepare_lead_context=init_result, content=content)
            logging.info(f"Response sent session_id={session_id} | status={result.get('status')}")
            return result
        
        except UserError as e:
            logging.warning(f"UserError session_id={session_id} | status=error | error={str(e)}")
            return {
                "content": str(e),
                "status": "error"
            }
        
        except Exception as e:
            logging.exception("SYSTEM ERROR")
            return {
                "content" : "יש תקלה זמנית, נסה שוב עוד רגע." ,
                "status": "error"
            }

    
    
    def initialize_lead_context(self , session_id , name=None):
        check = self.ensure_lead_data(session_id=session_id , name=name)
        
        #print(check)
        if check["status"] == "new":
            return {"status" : "new" , "message" : "היי, לפני שנתחיל איך קוראים לך?"}
        
        if check["status"] == "exists" or check["status"] == "created":
            logging.info(f"User logged in / created. session_id={session_id} | lead_id={check["lead_id"]}")
            return self.prepare_lead_context(lead_id=check["lead_id"] , session_id=check["session_id"])




    def run_lead_flow(self , prepare_lead_context , content=None):
        logging.info(
            f"lead context ready lead_id={prepare_lead_context['lead_base_data']['lead_id']}"
            f"field={prepare_lead_context['lead_conversation_states_data']['current_field']}"
        )
        
        if content is None:
            return self.generate_lead_question(lead_all_data=prepare_lead_context , ack_mode=0)

        
        if prepare_lead_context["lead_conversation_states_data"]["current_field"] == "phone":
            generate_ai_analysis = extract_phone(content=content)
            logging.info(f"Phone analysis lead_id={prepare_lead_context['lead_base_data']['lead_id']} | result={generate_ai_analysis}")
            
        
        else:
            try:
                validate_str(value=content , name="content")
                generate_ai_analysis = self.generate_analyze(lead_id=prepare_lead_context["lead_base_data"]["lead_id"] , content=content , current_field=prepare_lead_context["lead_conversation_states_data"]["current_field"])
                logging.info(f"Regular analysis lead_id={prepare_lead_context['lead_base_data']['lead_id']} | result={generate_ai_analysis}")
            
            except UserError:
                generate_ai_analysis = {"status": "missing", "reason": "no_info"}
                logging.info(f"UserError analysis lead_id={prepare_lead_context['lead_base_data']['lead_id']} | result={generate_ai_analysis}")
        

        self.leads_data.update_lead_last_interaction(last_interaction=datetime.now(timezone.utc) , lead_id=prepare_lead_context["lead_base_data"]["lead_id"])
        #print(generate_ai_analysis)
        self.apply_message_score(current_field=prepare_lead_context["lead_conversation_states_data"]["current_field"] , lead_info=prepare_lead_context["lead_scores_data"] , ai_analyze_response=generate_ai_analysis , reason=prepare_lead_context["lead_conversation_states_data"]["question_reason"])
        logging.info(f"Lead scores updated, lead_id={prepare_lead_context['lead_base_data']['lead_id']} | current_field={prepare_lead_context['lead_conversation_states_data']['current_field']} | score_count={prepare_lead_context['lead_scores_data']['score_count']} | total_score={prepare_lead_context['lead_scores_data']['total_score']}")
        logging.debug(prepare_lead_context['lead_scores_data'])

#
        self.update_flow_state(lead_all_data=prepare_lead_context , ai_response=generate_ai_analysis , content=content)
        
        logging.info(f"Flow updated, lead_id={prepare_lead_context['lead_base_data']['lead_id']} | current_field={prepare_lead_context['lead_conversation_states_data']['current_field']}")
        logging.debug(prepare_lead_context['lead_conversation_states_data'])
        
        determine_final_status = self.determine_final_status(lead_all_data=prepare_lead_context)
        logging.info(f"Lead finalize try, lead_id={prepare_lead_context['lead_base_data']['lead_id']} | final_status={prepare_lead_context["lead_base_data"]["final_status"]} | score_count={prepare_lead_context['lead_scores_data']['score_count']} | total_score={prepare_lead_context['lead_scores_data']['total_score']}")
        logging.debug(prepare_lead_context)
        if determine_final_status == True:
            self.build_lead_summary(lead_all_data=prepare_lead_context)
        
        self.db.commit()
        
        ack_mode = self.is_new_session(lead_id=prepare_lead_context["lead_base_data"]["lead_id"])
        return self.generate_lead_question(lead_all_data=prepare_lead_context, ack_mode=ack_mode)
        









    def is_new_session(self , lead_id):
        last_interaction = self.leads_data.get_lead_last_interaction(lead_id=lead_id)
        #print(f"last_interaction: {last_interaction}")
        
        if last_interaction is None:
            #print("no interaction")
            return 0
        
        if isinstance(last_interaction, str):
            last_interaction = datetime.fromisoformat(last_interaction)
        
        if last_interaction.tzinfo is None:
            last_interaction = last_interaction.replace(tzinfo=timezone.utc)
        
        now = datetime.now(timezone.utc)
        diff = now - last_interaction

        minutes = diff.total_seconds() / 60
        #print(minutes)
        if minutes >= 15:
            return 0
        
        return 1
    

   

    def ensure_lead_data(self , session_id , name=None):
        #validate_str(name , "name")
        #print(f"name: {name}")
        check_lead = self.leads_data.get_lead_base_data(session_id=session_id)
        #print(f"check_lead 1: {check_lead}")
        #print(check_lead)
        if check_lead is not None:
            #print("exists")
            return {"status" : "exists" , "lead_id" : check_lead["lead_id"] , "session_id" : session_id}
        
        if name is None:
            #print("no name here")
            return {"status" : "new"}
        
        #print(f"check_lead 2: {check_lead}")
        #print("alr bet")
        #print("we good")
        #print(f"second name: {name} | session id: {session_id}")        
        lead_id = self.leads_data.create_new_lead(name=name , session_id=session_id)


        if lead_id is not None:
            self.leads_scores.create_new_lead_score(lead_id=lead_id)
            self.leads_states.create_new_lead_conversation_states_data(lead_id=lead_id)
            self.leads_fields.create_new_lead_fields_data(lead_id=lead_id)


        return {"status" : "created" , "lead_id" : lead_id , "session_id" : session_id}





    def prepare_lead_context(self , lead_id , session_id):
        validate_int(lead_id , "lead id")

        lead_base_data = self.leads_data.get_lead_base_data(session_id=session_id)
        lead_states_data = self.leads_states.get_lead_conversation_states(lead_id=lead_id)
        lead_scores_data = self.leads_scores.get_lead_score_data(lead_id=lead_id)
        lead_fields_data = self.leads_fields.get_all_lead_field_data(lead_id=lead_id)
    
    
        return {
            "lead_base_data" : lead_base_data , 
            "lead_conversation_states_data" : lead_states_data , 
            "lead_scores_data" : lead_scores_data , 
            "lead_fields_data" : lead_fields_data 
        }

        
        

    def generate_lead_question(self , lead_all_data , ack_mode=0):
        #print(f"question_state: {lead_all_data['lead_conversation_states_data']['question_state']} | reason: {lead_all_data['lead_conversation_states_data']['question_reason']}")
        #print(f"current field: {lead_all_data['lead_conversation_states_data']['current_field']}")
        question = self.generate_question(lead_info=lead_all_data["lead_conversation_states_data"] , ack_mode=ack_mode , final_status=lead_all_data["lead_base_data"]["final_status"])
        if question is None:
            closing_message = self.closing_message(final_status=lead_all_data["lead_base_data"]["final_status"] , urgency_status=lead_all_data["lead_scores_data"]["urgency_status"] , name=lead_all_data["lead_base_data"]["name"])
            return {"status" : "DONE" , "message" : closing_message}
            
        return {"status" : "output" , "message" : question}



    def update_flow_state(self , lead_all_data , ai_response , content=None):
        flow_status = self.advance_on_found(ai_response=ai_response , lead_info=lead_all_data["lead_conversation_states_data"] , content=content)
        if flow_status == False:
            unresolved_status = self.handle_unresolved_flow(lead_info=lead_all_data["lead_conversation_states_data"] , ai_response=ai_response)
            if unresolved_status == False:
                self.handle_unresolved_fallbacks(lead_info=lead_all_data["lead_conversation_states_data"] , ai_response=ai_response)


    def determine_final_status(self , lead_all_data):
        finalize_lead_status = self.finalize_lead_status(lead_info=lead_all_data["lead_scores_data"])
        if finalize_lead_status is not None:
            lead_all_data["lead_base_data"]["final_status"] = finalize_lead_status["final_status"]
            return True
        
        return False


    def build_lead_summary(self , lead_all_data):
        summary_context = self.summary_context.prepare_lead_summary_context(lead_id=lead_all_data["lead_base_data"]["lead_id"])
        self.process_lead_summary(summary_info=summary_context)
  

    
    def generate_analyze(self , lead_id , current_field , content):
        ai_input = self.conversation_builder.build_prompt(current_field=current_field , content=content)
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
        #print("found")
        if ai_response["status"] == "found":
            if lead_info["current_field"] == "goal":
                lead_info["current_field"] = "budget"
                self.leads_fields.update_lead_field_data(lead_id=lead_info["lead_id"] , field="goal_user" , value=content)

            
            elif lead_info["current_field"] == "budget":
                lead_info["current_field"] = "phone"
                self.leads_fields.update_lead_field_data(lead_id=lead_info["lead_id"] , field="budget_user" , value=content)


            elif lead_info["current_field"] == "phone":
                lead_info["current_field"] = "urgency"
                self.leads_data.update_lead_phone(phone=ai_response["value"] , lead_id=lead_info["lead_id"])
                self.leads_fields.update_lead_field_data(lead_id=lead_info["lead_id"] , field="phone_user" , value=content)


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
            
            lead_info["question_state"] = "base"
            lead_info["question_reason"] = "base"

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

                lead_info["question_state"] = ai_response["status"]
                lead_info["question_reason"] = ai_response["reason"]

            return True
        
    
    
    def handle_unresolved_fallbacks(self , ai_response , lead_info):
        if ai_response["status"] == "missing" or ai_response["status"] == "confused":
            if lead_info["question_reason"] == "regular_fallback":
                if lead_info["current_field"] == "phone":
                    return
                
                self.leads_states.update_lead_question_reason(lead_id=lead_info["lead_id"] , value="after_fallback")
                lead_info["question_reason"] = "after_fallback"
                
                if lead_info["current_field"] == "goal":
                    self.leads_states.update_lead_current_field(lead_id=lead_info["lead_id"] , updated_field="budget")
                    lead_info["current_field"] = "budget"
                
                elif lead_info["current_field"] == "budget":
                    self.leads_states.update_lead_current_field(lead_id=lead_info["lead_id"] , updated_field="phone")
                    lead_info["current_field"] = "phone"


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
        
        if lead_message_score["status"] == "phone":
            print("alr bet")
            return True
        
        else:
            print(f"lead_message_score: {lead_message_score}")
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
        if summary_info["budget_user"] is not None:
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



service_layer = ServiceLayer()

service_layer.leads_data.create_leads_data_table()
service_layer.leads_states.create_lead_conversation_states()
service_layer.leads_scores.create_leads_scores_table()
service_layer.leads_fields.create_leads_fields_data()
service_layer.messages.create_leads_messages_table()

#lead_id = None
#name = None




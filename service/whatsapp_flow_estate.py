import logging
from datetime import datetime, timezone
import time
import sys   

from utils.validators import validate_int, validate_str, extract_phone
from utils.validators import UserError

from data_access.postgres.leads_data_repository import LeadsDataRepository
from data_access.postgres.leads_states_repository import LeadsStatesRepository
from data_access.postgres.leads_scores_repository import LeadsScoresRepository
from data_access.postgres.leads_fields_repository import LeadsFieldsRepository
from data_access.postgres.leads_messages_repository import MessagesRepository

from service.booking_service_w import BookingFlow
from service.summary_flow import SummaryFlow


from logic.message_scorer import MessageScorer
from logic.lead_score_manager import LeadScoreManager
from logic.ai_result_handler import OpenAIClient
from logic.lead_classifier import LeadClassifier

from output_builders.analyze_prompt_builder_english import ConversationBuilder
from output_builders.question_builder_estate import (
    ProcessQuestion,
    BaseQuestions,
    MissingQuestions,
    ConfuseQuestions,
    FallBackQuestions
)


class WhatsappFlow:
    def __init__(self , db):
        self.db = db
        self.summary_flow = SummaryFlow(self.db)
        self.booking_flow = BookingFlow(self.db)
        self.leads_data = LeadsDataRepository(self.db)
        self.leads_states = LeadsStatesRepository(self.db.new_cursor())
        self.leads_scores = LeadsScoresRepository(self.db.new_cursor())
        self.messages = MessagesRepository(self.db.new_cursor())
        self.leads_fields = LeadsFieldsRepository(self.db.new_cursor())
        self.message_scorer = MessageScorer()
        self.lead_score_manager = LeadScoreManager()
        self.openai_client = OpenAIClient()
        self.lead_classifier = LeadClassifier()
        self.conversation_builder = ConversationBuilder()
        self.process_question = ProcessQuestion(base_questions=BaseQuestions() , missing_questions=MissingQuestions() , confuse_questions=ConfuseQuestions() , fallback_questions=FallBackQuestions())




    def handle_pre_flow(self , prepare_lead_context , external_message_id):
        self.leads_states.update_lead_current_field(lead_id=prepare_lead_context['lead_base_data']['lead_id'] , updated_field="pre_flow")
        prepare_lead_context['lead_conversation_states_data']['current_field'] = "pre_flow"
        question = self.generate_lead_question(lead_all_data=prepare_lead_context, ack_mode=0 , external_message_id=external_message_id)
        self.db.commit()
        print(f"QUESTION-PRE: {question}" ,flush=True)
        return question


    def handle_qualification_flow(self , prepare_lead_context , external_message_id , content=None):
        try:
            generate_ai_analysis = self.generate_analyze(lead_id=prepare_lead_context["lead_base_data"]["lead_id"] , content=content , current_field=prepare_lead_context["lead_conversation_states_data"]["current_field"])
            logging.info(f"Regular analysis lead_id={prepare_lead_context['lead_base_data']['lead_id']} | result={generate_ai_analysis}")
            
        except UserError:
            generate_ai_analysis = {"status": "missing", "reason": "no_info"}
            logging.info(f"UserError analysis lead_id={prepare_lead_context['lead_base_data']['lead_id']} | result={generate_ai_analysis}")
            

        self.leads_data.update_lead_last_interaction(last_interaction=datetime.now(timezone.utc) , lead_id=prepare_lead_context["lead_base_data"]["lead_id"])
        self.apply_message_score(current_field=prepare_lead_context["lead_conversation_states_data"]["current_field"] , lead_info=prepare_lead_context["lead_scores_data"] , ai_analyze_response=generate_ai_analysis , reason=prepare_lead_context["lead_conversation_states_data"]["question_reason"])
        
        logging.info(f"Lead scores updated, lead_id={prepare_lead_context['lead_base_data']['lead_id']} | current_field={prepare_lead_context['lead_conversation_states_data']['current_field']} | score_count={prepare_lead_context['lead_scores_data']['score_count']} | total_score={prepare_lead_context['lead_scores_data']['total_score']}")
        logging.debug(prepare_lead_context['lead_scores_data'])
        
        self.update_flow_state(lead_all_data=prepare_lead_context , ai_response=generate_ai_analysis , content=content)
        
        logging.info(f"Flow updated, lead_id={prepare_lead_context['lead_base_data']['lead_id']} | current_field={prepare_lead_context['lead_conversation_states_data']['current_field']}")
        logging.debug(prepare_lead_context['lead_conversation_states_data'])
        
        determine_final_status = self.determine_final_status(lead_all_data=prepare_lead_context)
        
        logging.info(f"Lead finalize try, lead_id={prepare_lead_context['lead_base_data']['lead_id']} | final_status={prepare_lead_context['lead_base_data']['final_status']} | score_count={prepare_lead_context['lead_scores_data']['score_count']} | total_score={prepare_lead_context['lead_scores_data']['total_score']}")
        logging.debug(prepare_lead_context)
        
        if determine_final_status == True:
            return {"status" : "summary_flow"}


        ack_mode = self.is_new_session(lead_id=prepare_lead_context["lead_base_data"]["lead_id"])
        question = self.generate_lead_question(lead_all_data=prepare_lead_context, ack_mode=ack_mode , external_message_id=external_message_id)
        if question["status"] == "booking":
            self.db.commit()
            return {"status" : "booking_flow"}
        
        self.db.commit()
        print(f"QUESTION: {question}" ,flush=True)
        return question



    def process_whatsapp_flow(self , prepare_lead_context , external_message_id , content=None):
        print(f"CURRENTFIELD {prepare_lead_context['lead_conversation_states_data']['current_field']}", flush=True)
        if prepare_lead_context['lead_conversation_states_data']['current_field'] is None:
            return self.handle_pre_flow(prepare_lead_context=prepare_lead_context , external_message_id=external_message_id)
        
        elif prepare_lead_context['lead_conversation_states_data']['current_field'] == "booking_flow":
            return {"status" : "booking_flow"}
        
        else:
            return self.handle_qualification_flow(prepare_lead_context , external_message_id , content)
        


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

        

    def generate_lead_question(self , lead_all_data , external_message_id , ack_mode=0):
        question = self.generate_question(lead_info=lead_all_data["lead_conversation_states_data"] , ack_mode=ack_mode , final_status=lead_all_data["lead_base_data"]["final_status"] , external_message_id=external_message_id)
        if question is None:
            return {"status" : "booking"}

        elif lead_all_data["lead_conversation_states_data"]["current_field"] == "pre_flow":
            return {"status" : "pre_flow" , "message" : question}
        
        elif lead_all_data["lead_conversation_states_data"]["current_field"] == "goal":
            return {"status" : "goal" , "message" : question}

        return {"status" : "output" , "message" : question}






    def update_flow_state(self , lead_all_data , ai_response , content=None):
        flow_status = self.advance_on_found(ai_response=ai_response , lead_info=lead_all_data["lead_conversation_states_data"] , content=content)
        if flow_status == False:
            unresolved_status = self.handle_unresolved_flow(lead_info=lead_all_data["lead_conversation_states_data"] , ai_response=ai_response)
            if unresolved_status == False:
                self.handle_unresolved_fallbacks(lead_info=lead_all_data["lead_conversation_states_data"] , ai_response=ai_response)


    def determine_final_status(self , lead_all_data):
        finalize_lead_status = self.finalize_lead_status(lead_info=lead_all_data["lead_scores_data"])
        
        logging.info(f"[SERVICE] lead_id={lead_all_data['lead_base_data']['lead_id']} step=final_status result={finalize_lead_status}")
        
        if finalize_lead_status is not None:
            lead_all_data["lead_base_data"]["final_status"] = finalize_lead_status["final_status"]
            return True
        
        return False




    def generate_analyze(self , lead_id , current_field , content):
        print("CURRENT_FIELD RESULT:", current_field, flush=True)
        if current_field == "name":
            self.messages.add_lead_message(lead_id=lead_id , role="user" , content=content)
            return {"status" : "found" , "value" : content}
        
        elif current_field == "pre_flow":
            self.messages.add_lead_message(lead_id=lead_id , role="user" , content="Lead selected: Start")
            return {"status" : "found" , "value" : content}
        
        elif current_field == "goal":
            self.messages.add_lead_message(lead_id=lead_id , role="user" , content=content["title"])
            return {"status" : "found" , "value" : content["title"]}

        ai_input = self.conversation_builder.build_prompt(current_field=current_field , content=content)

        before_ai = time.time()
        #logging.info("[TIMER] BEFORE OPENAI")

        ai_response = self.openai_client.ai_reply(ai_input)
        
        #logging.info(f"[TIMER] AFTER OPENAI | took={time.time() - before_ai:.2f}s")

        self.messages.add_lead_message(lead_id=lead_id , role="user" , content=content)
        
        logging.info(f"[AI] lead_id={lead_id} step=analysis_result result={ai_response}")
        
        return ai_response

    
    
    
    def generate_question(self , lead_info , final_status , external_message_id , ack_mode):
        if final_status != "pending":
            return None
        
        question = self.process_question.get_question(
            field=lead_info["current_field"] , 
            question_state=lead_info["question_state"] , 
            reason=lead_info["question_reason"] , 
            attempt_number=lead_info["regular_attempt_number"],
            ack_mode=ack_mode)

        print(f"QUESRION: {question}" , flush=True)

        if lead_info["current_field"] == "pre_flow":
            text = question["body"]
            message_id = self.messages.add_lead_message(lead_id=lead_info["lead_id"] , role="assistant" , content=text)
        
        elif lead_info["current_field"] == "goal":
            text = question["body"]
            message_id = self.messages.add_lead_message(lead_id=lead_info["lead_id"] , role="assistant" , content=text)
        
        else:
            message_id = self.messages.add_lead_message(lead_id=lead_info["lead_id"] , role="assistant" , content=question)

        self.messages.add_external_message_id(message_id=message_id ,external_message_id=external_message_id)
        return question











    def advance_on_found(self , ai_response , lead_info , content):
            need_to_change = None

            if ai_response["status"] == "found":
                if lead_info["current_field"] == "pre_flow":
                    if isinstance(content , str):
                        return True
                    lead_info["current_field"] = "name"


                elif lead_info["current_field"] == "name":
                    lead_info["current_field"] = "goal"
                    self.leads_data.update_lead_name(lead_id=lead_info["lead_id"] , name=content)


                elif lead_info["current_field"] == "goal":
                    self.leads_fields.update_lead_field_data(lead_id=lead_info["lead_id"] , field="goal_user" , value=content["title"])
                    lead_info["current_field"] = "budget"

                
                elif lead_info["current_field"] == "budget":
                    self.leads_fields.update_lead_field_data(lead_id=lead_info["lead_id"] , field="budget_user" , value=content)
                    lead_info["current_field"] = "urgency"
                    

            
                elif lead_info["current_field"] == "urgency":
                    need_to_change = True
                    lead_info["current_field"] = "booking_flow"
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
        print(lead_info["current_field"], flush=True)
        if ai_response["status"] == "missing" or ai_response["status"] == "confused":
            if lead_info["question_reason"] == "regular_fallback":
                
                #if lead_info["current_field"] == "phone":
                    #return
                
                self.leads_states.update_lead_question_reason(lead_id=lead_info["lead_id"] , value="after_fallback")
                lead_info["question_reason"] = "after_fallback"
                

                if lead_info["current_field"] == "goal":
                    lead_info["current_field"] = "budget"
                
                if lead_info["current_field"] == "budget":
                    lead_info["current_field"] = "urgency"


                elif lead_info["current_field"] == "urgency":
                    lead_info["current_field"] = "booking_flow"

                self.leads_states.update_lead_current_field(lead_id=lead_info["lead_id"] , updated_field=lead_info["current_field"])
                self.leads_states.update_lead_regular_attempt_number(lead_id=lead_info["lead_id"] , number=1)
                self.leads_states.update_lead_confuse_attempt_number(lead_id=lead_info["lead_id"] , number=1)

                lead_info["regular_attempt_number"] = 1
                lead_info["confuse_attempt_number"] = 1
    
    
    def apply_message_score(self , lead_info , current_field , ai_analyze_response , reason):
        if current_field == "name":
            return
        
        if current_field == "pre_flow":
            return
        
        if current_field == "goal":
            return
        
        lead_message_score = self.message_scorer.score_estate_message(message_to_rank=ai_analyze_response , field=current_field , reason=reason)
        
        if lead_message_score["status"] == "invaild":
            return

        if lead_message_score["status"] == "unknown":
            self.lead_score_manager.update_lead_score_info(lead_score_info=lead_info , lead_message_score=lead_message_score , message_field=f"{current_field}_status")
            self.leads_scores.update_lead_score_info(lead_id=lead_info["lead_id"] , score_count=lead_info["score_count"] , total_score=lead_info["total_score"] , score_field=f"{current_field}_status" , value=lead_message_score["status"])
        
        else:
            print(f"lead_message_score: {lead_message_score}")
            self.lead_score_manager.update_lead_score_info(lead_score_info=lead_info , lead_message_score=lead_message_score , message_field=f"{current_field}_score")
            self.leads_scores.update_lead_score_info(lead_id=lead_info["lead_id"] , score_count=lead_info["score_count"] , total_score=lead_info["total_score"] , score_field=f"{current_field}_score" , value=lead_message_score["rank_score"])


        return True


    
    def finalize_lead_status(self , lead_info):
        if lead_info["score_count"] == 2:
            final_lead_status = self.lead_classifier.classify_lead_score(lead_info)
            
            if final_lead_status:
                self.leads_data.set_lead_final_status(lead_info["lead_id"] , final_lead_status)
                return {"final_status" : final_lead_status}
            
        return 
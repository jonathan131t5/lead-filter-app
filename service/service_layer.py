import logging

from service.whatsapp_flow import WhatsappFlow
from service.summary_flow import SummaryFlow
from service.booking_service_w import BookingFlow

from data_base.connection2 import Connection

from utils.validators import validate_int, validate_str, extract_phone
from utils.validators import UserError


class ServiceLayer:
    def __init__(self):
        self.db = Connection()
        self.whatsapp_flow = WhatsappFlow(self.db)
        self.summary_flow = SummaryFlow(self.db)
        self.booking_flow = BookingFlow(self.db)


    def handle_flow_result(self , session_id , external_message_id , content=None):
        try:
            logging.info(
            f"[NEW MESSAGE] session_id={session_id} | "
            f"content_len={len(content) if content else 0}"
            )
            
            if isinstance(content, str):
                content = content.strip()[:100]

            prepare_lead_context = self.initialize_lead_context(session_id=session_id)

            result = self.whatsapp_flow.process_whatsapp_flow(prepare_lead_context=prepare_lead_context , external_message_id=external_message_id , content=content)
            if "status" in result:
                if result["status"] == "summary_flow":
                    self.summary_flow.build_lead_summary(prepare_lead_context['lead_base_data']['lead_id'])
                    return self.booking_flow.process_booking_flow(lead_id=prepare_lead_context['lead_base_data']['lead_id'] , content=content)
                elif result["status"] == "booking_flow":
                    return self.booking_flow.process_booking_flow(lead_id=prepare_lead_context['lead_base_data']['lead_id'] , content=content)
                else:
                    return result
                
        except Exception:
            logging.exception(
                f"[FLOW ERROR] lead_id={prepare_lead_context['lead_base_data']['lead_id']} step=run_lead_flow"
            )
            self.db.rollback()
            raise
  




    def initialize_lead_context(self , session_id):
        check = self.ensure_lead_data(session_id=session_id)
        
        if check["status"] == "exists" or check["status"] == "created":
            logging.info(f"User logged in / created. session_id={session_id} | lead_id={check['lead_id']}")
            self.leads_data.update_lead_phone(lead_id=check["lead_id"] , phone=session_id)
            return self.prepare_lead_context(lead_id=check["lead_id"] , session_id=check["session_id"])
        


    def ensure_lead_data(self , session_id):
        check_lead = self.leads_data.get_lead_base_data(session_id=session_id)
        
        if check_lead is not None:
            return {"status" : "exists" , "lead_id" : check_lead["lead_id"] , "session_id" : session_id}
        
        
        lead_id = self.leads_data.create_new_lead(session_id=session_id)


        if lead_id is not None:
            self.leads_scores.create_new_lead_score(lead_id=lead_id)
            self.leads_states.create_new_lead_conversation_states_data(lead_id=lead_id , session_id=session_id)
            self.leads_fields.create_new_lead_fields_data(lead_id=lead_id)
            self.leads_booking.create_lead_booking(lead_id=lead_id)



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

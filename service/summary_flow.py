from data_access.postgres.lead_summary_context_repository import LeadSummaryContextRepository
from data_access.postgres.leads_data_repository import LeadsDataRepository


class SummaryFlow:
    def __init__(self , db):
        self.db = db
        self.summary_context = LeadSummaryContextRepository(self.db.new_cursor())
        self.leads_data = LeadsDataRepository(self.db.new_cursor())



    def build_lead_summary(self , lead_id):
        summary_context = self.summary_context.prepare_lead_summary_context(lead_id=lead_id)
        self.process_lead_summary(summary_info=summary_context)
        return summary_context

    

    def process_lead_summary(self , summary_info):
        summary_info = self.field_unknown_check(summary_info=summary_info)

        final_status_context = self.generate_final_status_context(summary_info=summary_info)
        
        final_summary = self.generate_lead_summary(summary_info=summary_info , final_status_context=final_status_context)

        self.upload_lead_summary(summary=final_summary , lead_id=summary_info["lead_id"])

    


    def field_unknown_check(self , summary_info):
        if summary_info["goal_status"] == "unknown":
            summary_info["goal_user"] = "Not provided by the client"
        
        if summary_info["urgency_status"] == "unknown":
            summary_info["urgency_user"] = "Not provided by the client"

        return summary_info


    def generate_final_status_context(self, summary_info):
        if summary_info["final_status"] == "Hot Lead":
            final_status_context = "Hot lead 🔥"

        elif summary_info["final_status"] == "Cold Lead":
            final_status_context = "Cold lead 🧊"

        elif summary_info["final_status"] == "pending":
            final_status_context = "Lead in progress ⏳"

        else:
            final_status_context = f"Unknown status: {summary_info['final_status']}"
        
        return final_status_context
    

    def generate_lead_summary(self, summary_info, final_status_context):
        text = (
            f"{summary_info['name']} — {final_status_context}\n\n"
            f"Goal: {summary_info['goal_user']}\n"
            f"Timeline: {summary_info['urgency_user']}\n\n"
            f"Score: {summary_info['total_score']}\n"
            f"Phone: {summary_info['phone_number']}"
        )

        return text

    
    def upload_lead_summary(self , summary , lead_id):
        self.leads_data.upload_summary(lead_summary=summary , lead_id=lead_id)
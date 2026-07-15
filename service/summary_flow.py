from data_access.postgres.lead_summary_context_repository import LeadSummaryContextRepository
from data_access.postgres.leads_data_repository import LeadsDataRepository


class SummaryFlow:
    def __init__(self , db):
        self.db = db
        self.summary_context = LeadSummaryContextRepository(self.db.new_cursor())
        self.leads_data = LeadsDataRepository(self.db)



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
        #if summary_info["goal_status"] == "unknown":
            #summary_info["goal_user"] = "Not provided by the client"
        
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
        eligibility_sentences = self.build_eligibility_summary(
            summary_info=summary_info
        )

        eligibility_text = "\n".join(
            [f"• {sentence}" for sentence in eligibility_sentences]
        )

        goal = summary_info["goal_user"].replace("_", " ").title()

        text = (
            f"{summary_info['name']} — {final_status_context}\n\n"

            f"🎯 Goal\n"
            f"{goal}\n\n"

            f"👤 Client Profile\n"
            f"{eligibility_text}\n\n"

            f"⏱ Intent\n"
            f"{summary_info['urgency_user']}\n\n"

            f"🔥 Lead Score\n"
            f"{summary_info['total_score']}/30\n\n"

            f"📞 Phone\n"
            f"{summary_info['phone_number']}"
        )

        return text

    

    def upload_lead_summary(self , summary , lead_id):
        self.leads_data.upload_summary(lead_summary=summary , lead_id=lead_id)





    def build_eligibility_summary(self, summary_info):
        goal = summary_info["goal_user"]

        answers = [
            summary_info["eligibility_user1"],
            summary_info["eligibility_user2"],
            summary_info["eligibility_user3"],
            summary_info["eligibility_user4"],
            summary_info["eligibility_user5"]
        ]

        sentence_maps = {
            "permanent_residence": [
                lambda answer: f"Works as {answer}",
                {
                    "yes": "Has a job offer in Canada",
                    "no": "Does not have a job offer in Canada",
                    "not_sure": "Is not sure whether they have a job offer in Canada"
                },
                lambda answer: f"Highest level of education is {answer}",
                {
                    "yes": "Has taken an English or French proficiency test",
                    "no": "Has not taken an English or French proficiency test",
                    "not_sure": "Is not sure about their language test status"
                },
                {
                    "yes": "Has lived or worked in Canada before",
                    "no": "Has not lived or worked in Canada before",
                    "not_sure": "Is not sure whether previous Canadian experience applies"
                }
            ],

            "work_permit": [
                {
                    "yes": "Has a job offer from a Canadian employer",
                    "no": "Does not have a job offer from a Canadian employer",
                    "not_sure": "Is not sure whether they have a Canadian job offer"
                },
                {
                    "specific": "Has a specific job offer",
                    "explore": "Is still exploring general work options",
                    "not_sure": "Is not sure which work option they need"
                },
                lambda answer: f"Works in {answer}",
                {
                    "permanent": "Wants to stay in Canada permanently",
                    "temporary": "Wants to stay in Canada temporarily",
                    "not_sure": "Is not sure whether they want to stay permanently or temporarily"
                },
                {
                    "yes": "Has applied for a work permit before",
                    "no": "Has not applied for a work permit before",
                    "not_sure": "Is not sure about previous work permit applications"
                }
            ],

            "study_permit": [
                {
                    "college": "Plans to study at a college",
                    "undergrad": "Plans to apply for undergraduate studies",
                    "grad": "Plans to apply for graduate studies"
                },
                {
                    "yes": "Has an acceptance letter from a Canadian institution",
                    "no": "Does not have an acceptance letter from a Canadian institution",
                    "not_sure": "Is not sure about their acceptance letter"
                },
                lambda answer: f"Plans to study {answer}",
                {
                    "yes": "Has proof of funds for tuition and living costs",
                    "no": "Does not have proof of funds for tuition and living costs",
                    "not_sure": "Is not sure whether their proof of funds is sufficient"
                },
                {
                    "yes": "This is their first study permit application",
                    "no": "Has applied for a study permit before",
                    "not_sure": "Is not sure about their previous study permit application"
                }
            ],

            "family_sponsorship": [
                {
                    "spouse_partner": "The sponsorship is for a spouse or partner",
                    "parent": "The sponsorship is for a parent",
                    "child": "The sponsorship is for a child",
                    "other": "The sponsorship is for another family member"
                },
                {
                    "yes": "The sponsor is a Canadian citizen or permanent resident",
                    "no": "The sponsor is not a Canadian citizen or permanent resident",
                    "not_sure": "Is not sure about the sponsor's Canadian status"
                },
                lambda answer: f"The applicant currently lives in {answer}",
                {
                    "yes": "A sponsorship application has been submitted before",
                    "no": "No sponsorship application has been submitted before",
                    "not_sure": "Is not sure about previous sponsorship applications"
                },
                {
                    "yes": "Has had a visa application refused before",
                    "no": "Has not had a visa application refused before",
                    "not_sure": "Is not sure about previous visa refusals"
                }
            ],

            "visitor_visa": [
                {
                    "tourism": "Plans to visit Canada for tourism",
                    "family": "Plans to visit family in Canada",
                    "business": "Plans to visit Canada for business"
                },
                lambda answer: f"Plans to stay in Canada for {answer}",
                {
                    "yes": "Has travelled to Canada before",
                    "no": "Has not travelled to Canada before",
                    "not_sure": "Is not sure about their previous travel to Canada"
                },
                {
                    "yes": "Has travelled internationally before",
                    "no": "Has not travelled internationally before",
                    "not_sure": "Is not sure about their international travel history"
                },
                {
                    "yes": "Has had a visa application refused before",
                    "no": "Has not had a visa application refused before",
                    "not_sure": "Is not sure about previous visa refusals"
                }
            ],

            "business_immigration": [
                {
                    "invest": "Wants to invest in a business",
                    "start_my_own": "Wants to start their own business",
                    "not_sure": "Is not sure which business immigration option they need"
                },
                {
                    "yes": "Has investment funds ready",
                    "no": "Does not have investment funds ready",
                    "not_sure": "Is not sure whether their investment funds are sufficient"
                },
                {
                    "yes": "Has business ownership or management experience",
                    "no": "Does not have business ownership or management experience",
                    "not_sure": "Is not sure whether their business experience qualifies"
                },
                {
                    "yes": "Has a specific Canadian province in mind",
                    "no": "Does not have a specific Canadian province in mind",
                    "not_sure": "Is not sure which Canadian province to choose"
                },
                {
                    "yes": "Has a business plan prepared",
                    "no": "Does not have a business plan prepared",
                    "not_sure": "Is not sure whether their business plan is ready"
                }
            ],

            "not_sure": [
                lambda answer: answer
            ]
        }

        goal_rules = sentence_maps.get(goal, [])
        sentences = []

        for index, rule in enumerate(goal_rules):
            answer = answers[index]

            if not answer:
                continue

            if callable(rule):
                sentence = rule(answer)
            else:
                sentence = rule.get(
                    answer,
                    f"Answer provided: {answer}"
                )

            sentences.append(sentence)

        return sentences
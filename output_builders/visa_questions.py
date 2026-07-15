import random


VISA_FIELDS = [
    "permanent_residence",
    "work_permit",
    "study_permit",
    "family_sponsorship",
    "visitor_visa",
    "business_immigration",
    "not_sure"
]


class BaseQuestions:
    def goal_base_questions(self):
        button = [
            {"id": "goal_permanent_residence", "title": "Permanent Residence"},
            {"id": "goal_work_permit", "title": "Work Permit"},
            {"id": "goal_study_permit", "title": "Study Permit"},
            {"id": "goal_family_sponsorship", "title": "Family Sponsorship"},
            {"id": "goal_visitor_visa", "title": "Visitor Visa"},
            {"id": "goal_business_immigration", "title": "Business Immigration"},
            {"id": "goal_not_sure", "title": "Not sure"}
        ]

        question = "What type of Canadian immigration service are you interested in?"

        return {
            "buttons": button,
            "body": question,
            "button_label": "View visa options"
        }


    def pre_flow_base_question(self):
        button = [
            {"id": "approved", "title": "start"}
        ]

        question = "Hey! Welcome 👋 I'll ask you a few quick questions to get started — please send one answer per message so everything stays clear."

        return {
            "buttons": button,
            "body": question
        }


    
    def eligibility_buttons(self , field , question , raw_index=1):
        yes_no_not_sure_buttons = [
            {"id": "eligibility_yes", "title": "Yes"},
            {"id": "eligibility_no", "title": "No"},
            {"id": "eligibility_not_sure", "title": "Not sure"}
        ]
        
        question_index = raw_index - 1
        
        if (
            field == "permanent_residence" and question_index in [0 , 2]
            or field == "work_permit" and question_index == 2
            or field == "study_permit" and question_index == 2
            or field == "family_sponsorship" and question_index == 2
            or field == "visitor_visa" and question_index == 1
            or field == "not_sure" and question_index == 0
        ):
            return question
        
    
        elif field == "work_permit" and question_index == 1:
            return {
                "buttons": [
                    {"id": "eligibility_specific", "title": "Specific offer"},
                    {"id": "eligibility_explore", "title": "Still exploring"},
                    {"id": "eligibility_not_sure", "title": "Not sure"}
                    ],
                
                "body": question
                }
        
        elif field == "work_permit" and question_index == 3:
            return {
                "buttons": [
                {"id": "eligibility_permanent", "title": "Permanent"},
                {"id": "eligibility_temporary", "title": "Temporary"},
                {"id": "eligibility_not_sure", "title": "Not sure"}
                ],
            "body": question
        }
        
        elif field == "study_permit" and question_index == 0:
            return {
                "buttons": [
                {"id": "eligibility_college", "title": "College"},
                {"id": "eligibility_undergrad", "title": "Undergrad"},
                {"id": "eligibility_grad", "title": "Grad"}
                ],
            "body": question
        }

        elif field == "family_sponsorship" and question_index == 0:
            return {
                "buttons": [
                {"id": "eligibility_spouse_partner", "title": "Spouse/Partner"},
                {"id": "eligibility_parent", "title": "Parent"},
                {"id": "eligibility_child", "title": "Child"} , 
                {"id": "eligibility_other", "title": "Other"} ,
                ],
            "body": question , 
            "button_label": "View options"
        }

        elif field == "visitor_visa" and question_index == 0:
            return {
                "buttons": [
                {"id": "eligibility_tourism", "title": "Tourism"},
                {"id": "eligibility_family", "title": "Family"},
                {"id": "eligibility_business", "title": "Business"} 
                ],
            "body": question
        }

        elif field == "business_immigration" and question_index == 0:
            return {
                "buttons": [
                {"id": "eligibility_invest", "title": "Invest"},
                {"id": "eligibility_start_my_own", "title": "Start my own"},
                {"id": "eligibility_not_sure", "title": "Not sure"} 
                ],
            "body": question
        }

        else:
            return {
                "buttons" : yes_no_not_sure_buttons ,
                "body" : question
            }

        
    
    
    def eligibility_base_questions(self, field, question_index=1):
        questions = {
            "permanent_residence": [
                "What's your current occupation and years of experience?",
                "Do you have a job offer in Canada?",
                "What's your highest level of education?",
                "Have you taken an English or French proficiency test?",
                "Have you lived or worked in Canada before?"
            ],

            "work_permit": [
                "Do you already have a job offer from a Canadian employer?",
                "Do you have a specific job offer, or are you exploring general work options?",
                "What's your occupation/field?",
                "Are you looking to stay in Canada permanently, or just temporarily?",
                "Have you applied for a work permit before?"
            ],

            "study_permit": [
                "What level of study are you planning to apply for: college, undergraduate, or graduate?",
                "Do you have an acceptance letter from a Canadian institution?",
                "What's your intended field of study?",
                "Do you have proof of funds for tuition and living costs?",
                "Is this your first time applying for a study permit?"
            ],

            "family_sponsorship": [
                "What's your relationship to the person you're sponsoring/being sponsored by?",
                "Is the sponsor currently a Canadian citizen or permanent resident?",
                "Where does the applicant currently live?",
                "Has a sponsorship application been submitted before?",
                "Have you had any visa applications refused before?"
            ],

            "visitor_visa": [
                "What's the purpose of the visit?",
                "How long do you plan to stay?",
                "Have you traveled to Canada before?",
                "Have you traveled internationally before?",
                "Have you had any visa applications refused before?"
            ],

            "business_immigration": [
                "Are you looking to invest in a business, or start your own?",
                "Do you have investment funds ready?",
                "Do you have business ownership/management experience?",
                "Do you have a specific province in mind?",
                "Do you have a business plan prepared?"
            ],

            "not_sure": [
                "Can you briefly describe your situation and what you're hoping to do in Canada?"
            ]
        }

        
        question = questions[field][question_index - 1]

        return self.eligibility_buttons(field=field , question=question , raw_index=question_index)



    def urgency_base_questions(self):
        return [
            "When are you looking to get started?"
        ]


    def phone_base_question(self):
        return [
            "What's the best number to reach you?"
        ]


    def name_base_question(self):
        return [
            "Before we start what's your name?"
        ]


    def process_base_question(self, field, ack_mode, question_index=1):
        print(
            f"PROCESS BASE QUESTION FIELD={repr(field)} ACK_MODE={repr(ack_mode)} QUESTION_INDEX={repr(question_index)}",
            flush=True
        )

        if field == "goal":
            questions = self.goal_base_questions()

        elif field in VISA_FIELDS:
            questions = self.eligibility_base_questions(
                field=field,
                question_index=question_index
            )

        elif field == "urgency":
            questions = self.urgency_base_questions()

        elif field == "name":
            questions = self.name_base_question()

        elif field == "pre_flow":
            questions = self.pre_flow_base_question()

        else:
            raise TypeError("Invalid field")

        if field not in ["pre_flow", "goal"] + VISA_FIELDS:
            question = questions[0]
        else:
            question = questions

        if ack_mode == 1:
            if field not in ["pre_flow", "goal"] + VISA_FIELDS:
                return f"{self.build_ack_prefix()} {question}"

        return question


    def build_ack_prefix(self):
        return f"{random.choice(['Got it', 'Nice', 'Awesome', 'Perfect', 'Great', 'Thanks', 'Sounds good'])}{random.choice([',', '.'])}"


class MissingQuestions:
    def urgency_missing_questions(self, question_type, attempt_number):
        if question_type == "no_info":
            return [
                "Do you have a rough timeframe in mind?"
            ]

        elif question_type == "vague":
            return [
                "Could you be a little more specific on timing?"
            ]

        elif question_type == "avoid":
            return [
                "Even something general works — sooner, later, or not sure yet?"
            ]


    def process_missing_question(self, field, reason, attempt_number):
        print(f"FIELD PROCESS: {field}", flush=True)

        if field == "urgency":
            questions = self.urgency_missing_questions(reason, attempt_number)
        else:
            raise TypeError(f"Invalid field: {field}")

        return random.choice(questions)


class ConfuseQuestions:
    def urgency_confuse_questions(self, question_type):
        if question_type == "meaning":
            return [
                "I mean when you'd like to get started."
            ]

        elif question_type == "answer_type":
            return [
                "Just write roughly when you'd like to get started."
            ]

        elif question_type == "focus":
            return [
                "For now, I just need to know roughly when you'd like to get started."
            ]


    def process_confuse_question(self, field, reason):
        if field == "urgency":
            questions = self.urgency_confuse_questions(reason)
        else:
            raise TypeError("Invalid field")

        return random.choice(questions)


class FallBackQuestions:
    def urgency_fallback_questions(self, fallback_type):
        if fallback_type == "after_fallback":
            return [
                "All good, when are you looking to get started?"
            ]

        elif fallback_type == "regular_fallback":
            return [
                "Is this something you want to start now, soon, or further down the line?"
            ]


    def process_fallback_question(self, field, reason):
        if field == "urgency":
            questions = self.urgency_fallback_questions(fallback_type=reason)
        else:
            raise TypeError("Invalid field choice")

        return random.choice(questions)


class ProcessQuestion:
    def __init__(self, base_questions, missing_questions, confuse_questions, fallback_questions):
        self.base_questions = base_questions
        self.missing_questions = missing_questions
        self.confuse_questions = confuse_questions
        self.fallback_questions = fallback_questions


    def get_question(self, field, question_state, reason, attempt_number, ack_mode, question_index=1):
        if question_state == "base":
            return self.base_questions.process_base_question(
                field=field,
                ack_mode=ack_mode,
                question_index=question_index
            )

        elif question_state == "missing":
            return self.missing_questions.process_missing_question(
                field=field,
                reason=reason,
                attempt_number=attempt_number
            )

        elif question_state == "confused":
            return self.confuse_questions.process_confuse_question(
                field=field,
                reason=reason
            )

        elif question_state == "fallback":
            return self.fallback_questions.process_fallback_question(
                field=field,
                reason=reason
            )

        raise TypeError("Invalid question state")   
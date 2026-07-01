import random


VISA_FIELDS = [
    "skilled_worker",
    "health_care",
    "student",
    "family_spouse",
    "ilr",
    "not_sure"
]


class BaseQuestions:
    def goal_base_questions(self):
        button = [
            {"id": "goal_skilled_worker", "title": "Skilled Worker Visa"},
            {"id": "goal_health_care", "title": "Health Care Visa"},
            {"id": "goal_student", "title": "Student Visa"},
            {"id": "goal_family_spouse", "title": "Family / Spouse Visa"},
            {"id": "goal_ilr", "title": "Settlement / ILR"},
            {"id": "goal_not_sure", "title": "Not sure"},
        ]

        question = "What type of UK visa are you interested in?"

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


    def eligibility_base_questions(self, field, question_index=1):
        questions = {
            "skilled_worker": [
                "Do you have a job offer from a UK employer?",
                "Is your employer licensed to sponsor visas?",
                "Is the job full-time?",
                "Do you meet the English language requirement?",
                "Do you have enough funds to support yourself initially?"
            ],

            "health_care": [
                "Do you have a job offer in health or social care from a UK employer?",
                "Is your employer licensed to sponsor visas?",
                "Is your job on the UK's eligible occupations list?",
                "Do you meet the English language requirement?",
                "Do you have enough funds to support yourself initially?"
            ],

            "student": [
                "Do you have an offer from a UK university or college?",
                "Is the institution licensed to sponsor international students?",
                "Do you meet the English language requirement?",
                "Can you cover your tuition fees?",
                "Can you cover your living expenses in the UK?"
            ],

            "family_spouse": [
                "Does your partner or family member have British citizenship or settled status?",
                "Are you married, engaged, or in a long-term relationship?",
                "Do you have evidence of your relationship?",
                "Do you plan to live together in the UK?",
                "Does your sponsor meet the financial requirements?"
            ],

            "ilr": [
                "Have you been living in the UK for at least 5 years?",
                "Do you currently hold a valid UK visa?",
                "Have you passed the Life in the UK test?",
                "Do you meet the English language requirement?",
                "Have you complied with your visa conditions during your stay?"
            ],

            "not_sure": [
                "Can you briefly describe your situation and what you're hoping to do in the UK?"
            ]
        }

        yes_no_buttons = [
            {"id": "eligibility_yes", "title": "Yes"},
            {"id": "eligibility_no", "title": "No"}
        ]

        yes_no_not_sure_buttons = [
            {"id": "eligibility_yes", "title": "Yes"},
            {"id": "eligibility_no", "title": "No"},
            {"id": "eligibility_not_sure", "title": "Not sure"}
        ]

        question = questions[field][question_index - 1]

        if field == "not_sure":
            return question

        if (
            field == "skilled_worker" and question_index == 2
            or field == "health_care" and question_index in [2, 3]
            or field == "student" and question_index == 2
            or field == "family_spouse" and question_index == 5
            or field == "ilr" and question_index == 3
        ):
            buttons = yes_no_not_sure_buttons
        else:
            buttons = yes_no_buttons

        return {
            "buttons": buttons,
            "body": question
        }


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
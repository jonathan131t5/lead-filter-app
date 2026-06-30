import random


class BaseQuestions:
    def goal_base_questions(self):
        button = [
            {"id": "goal_skilled_worker", "title": "Skilled Worker Visa"},
            {"id": "goal_student", "title": "Student Visa"},
            {"id": "goal_family_spouse", "title": "Family / Spouse Visa"},
            {"id": "goal_ilr", "title": "Settlement / ILR"},
            {"id": "goal_not_sure", "title": "Not sure"},
        ]
        question = "What type of UK visa are you interested in?"
        return {"buttons": button, "body": question}


    def pre_flow_base_question(self):
        button = [
            {"id": "approved", "title": "start"}
        ]
        question = "Hey! Welcome 👋 I'll ask you a few quick questions to get started — please send one answer per message so everything stays clear."
        return {"buttons": button, "body": question}



    def eligibility_base_questions(self, goal_value=None):
        button = [
            {"id": "eligibility_yes", "title": "Yes"},
            {"id": "eligibility_no", "title": "No"}
        ]

        if goal_value == "skilled_worker":
            question = "Do you have a job offer from a UK employer?"

        elif goal_value == "student":
            question = "Do you have an offer from a UK university or college?"

        elif goal_value == "family_spouse":
            question = "Does your partner or family member have UK settled status or British citizenship?"

        elif goal_value == "ilr":
            question = "Have you been living in the UK for at least 5 years?"

        elif goal_value == "not_sure":
            question = "Do you already know which UK visa you may qualify for?"

        return {
            "buttons": button,
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


    def process_base_question(self, field, ack_mode, goal_value=None):
        print(f"PROCESS BASE QUESTION FIELD={repr(field)} ACK_MODE={repr(ack_mode)}", flush=True)

        if field == "goal":
            questions = self.goal_base_questions()
        elif field in ["skilled_worker" , "student" , "family_spouse" , "ilr" , "not_sure"]:
            questions = self.eligibility_base_questions(goal_value=goal_value)
        elif field == "urgency":
            questions = self.urgency_base_questions()
        elif field == "name":
            questions = self.name_base_question()
        elif field == "pre_flow":
            questions = self.pre_flow_base_question()
        else:
            raise TypeError("Invalid field")

        if field != "pre_flow" and field != "goal":
            question = questions[0]
        else:
            question = questions

        if ack_mode == 1:
            if field != "pre_flow" and field != "goal":
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
        if field == "goal":
            questions = self.goal_fallback_questions(fallback_type=reason)
        elif field == "eligibility":
            questions = self.eligibility_fallback_questions(fallback_type=reason)
        elif field == "phone":
            questions = self.phone_fallback_question(fallback_type=reason)
        elif field == "urgency":
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


    def get_question(self, field, question_state, reason, attempt_number, ack_mode, goal_value=None):
        if question_state == "base":
            return self.base_questions.process_base_question(
                field=field,
                ack_mode=ack_mode,
                goal_value=goal_value
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
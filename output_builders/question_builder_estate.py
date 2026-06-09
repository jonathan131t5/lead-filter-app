import random


class BaseQuestions:
    def goal_base_questions(self):
        button = [
            {"id" : "goal_buy" , "title" : "buy"} , 
            {"id" : "goal_sell" , "title" : "sell"} , 
            {"id" : "goal_rent" , "title" : "rent"} , 
        ]
        question = ("Are you looking to buy, sell, or rent?")
        return {"buttons" : button , "body" : question}

    def budget_base_questions(self):
        return [
            "What's your budget?"
        ]

    def urgency_base_questions(self):
        return [
            "What's your timeframe?"
        ]

    def phone_base_question(self):
        return [
            "What's the best number to reach you?"
        ]
    
    def name_base_question(self):
        return [
            "Before we start what's your name?"
        ]
    
    def pre_flow_base_question(self):
        button = [
            {"id" : "approved" , "title" : "start"}
        ]
        question = ("Hey! Welcome 👋 I'll ask you a few quick questions to get started — please send one answer per message so everything stays clear.")
        
        return {"buttons" : button , "body" : question}

    def process_base_question(self, field, ack_mode):
        print(f"PROCESS BASE QUESTION FIELD={repr(field)} ACK_MODE={repr(ack_mode)}", flush=True)
        if field == "goal":
            questions = self.goal_base_questions()
        elif field == "budget":
            questions = self.budget_base_questions()
        elif field == "urgency":
            questions = self.urgency_base_questions()
        elif field == "name":
            questions = self.name_base_question()
        elif field == "pre_flow":
            questions = self.pre_flow_base_question()
        else:
            raise TypeError("Invalid field")

        if field != "pre_flow" and field != "budget":
            question = questions[0]
        else:
            question = questions

        if ack_mode == 1:
            if field != "pre_flow":
                return f"{self.build_ack_prefix()} {question}"

        return question

    def build_ack_prefix(self):
        return f"{random.choice(['Got it', 'Nice', 'Awesome', 'Perfect'])}{random.choice([',', '.'])}"


class MissingQuestions:
    def goal_missing_questions(self, question_type, attempt_number):
        if attempt_number != 2:
            return

        if question_type == "no_info":
            return [
                "Even something simple is fine, are you looking to buy, sell, or rent?"
            ]
        elif question_type == "vague":
            return [
                "Can you share a bit more — are you buying, selling, or renting?"
            ]
        elif question_type == "avoid":
            return [
                "Just so I can understand better, are you looking to buy, sell, or rent?"
            ]

    def budget_missing_questions(self, question_type, attempt_number):
        if attempt_number != 2:
            return

        if question_type == "no_info":
            return [
                "Even something simple is fine, do you have a budget in mind?"
            ]
        elif question_type == "vague":
            return [
                "Can you share a bit more about your budget?"
            ]
        elif question_type == "avoid":
            return [
                "Just so I can understand better, what's your budget?"
            ]

    def urgency_missing_questions(self, question_type, attempt_number):
        if attempt_number != 2:
            return

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
                "Even something general works — sooner, later, not sure yet?"
            ]

    def phone_missing_questions(self, question_type, attempt_number):
        if question_type == "no_info":
            if attempt_number == 2:
                return [
                    "I'll need your number so we can continue"
                ]
        elif question_type == "invalid_format":
            if attempt_number == 2:
                return [
                    "That number doesn't look right — can you send it again?"
                ]

    def process_missing_question(self, field, reason, attempt_number):
        if field == "goal":
            questions = self.goal_missing_questions(reason, attempt_number)
        elif field == "budget":
            questions = self.budget_missing_questions(reason, attempt_number)
        elif field == "urgency":
            questions = self.urgency_missing_questions(reason, attempt_number)
        elif field == "phone":
            questions = self.phone_missing_questions(reason, attempt_number)
        else:
            raise TypeError("Invalid field")

        return random.choice(questions)


class ConfuseQuestions:
    def goal_confuse_questions(self, question_type):
        if question_type == "meaning":
            return [
                "I mean whether you're looking to buy, sell, or rent."
            ]
        elif question_type == "answer_type":
            return [
                "Just tell me — buy, sell, or rent."
            ]
        elif question_type == "focus":
            return [
                "For now, I just need to know if you're buying, selling, or renting."
            ]

    def budget_confuse_questions(self, question_type):
        if question_type == "meaning":
            return [
                "I mean how much you're looking to spend."
            ]
        elif question_type == "answer_type":
            return [
                "Just tell me your budget."
            ]
        elif question_type == "focus":
            return [
                "For now, I just need to know your budget."
            ]

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
        if field == "goal":
            questions = self.goal_confuse_questions(reason)
        elif field == "budget":
            questions = self.budget_confuse_questions(reason)
        elif field == "urgency":
            questions = self.urgency_confuse_questions(reason)
        else:
            raise TypeError("Invalid field")

        return random.choice(questions)


class FallBackQuestions:
    def __init__(self):
        pass

    def goal_fallback_questions(self, fallback_type):
        if fallback_type == "after_fallback":    
            return [
                "Even a general answer helps, are you looking to buy, sell, or rent?"
            ]
        elif fallback_type == "regular_fallback":
            return [
                "Even a general answer helps, are you looking to buy, sell, or rent?"
            ]

    def budget_fallback_questions(self, fallback_type):
        if fallback_type == "after_fallback":
            return [
                "Alright, let's keep going — what's your budget?"
            ]
        elif fallback_type == "regular_fallback":
            return [
                "Even a general answer helps, what's your budget?"
            ]
        else:
            raise TypeError("Invalid fallback type")

    def phone_fallback_question(self, fallback_type):
        if fallback_type == "after_fallback":
            return [
                "Alright, let's keep going — what's the best number to reach you?"
            ]
        elif fallback_type == "regular_fallback":
            return [
                "Without a number, we can't continue 🙏 If you'd like to keep going, just send it here."
            ]

    def urgency_fallback_questions(self, fallback_type):
        if fallback_type == "after_fallback":
            return [
                "All good, what's your timeframe?"
            ]
        elif fallback_type == "regular_fallback":
            return [
                "Is this something you want to start now, soon, or further down the line?"
            ]
        else:
            raise TypeError("Invalid fallback type")

    def process_fallback_question(self, field, reason):
        questions = []
        if field == "goal":
            questions = self.goal_fallback_questions(fallback_type=reason)
        elif field == "budget":
            questions = self.budget_fallback_questions(fallback_type=reason)
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

    def get_question(self, field, question_state, reason, attempt_number, ack_mode):
        if question_state == "base":
            return self.base_questions.process_base_question(field, ack_mode)
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
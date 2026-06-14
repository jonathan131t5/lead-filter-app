import random


class BaseQuestions:
    def goal_base_questions(self):
        button = [
            {"id": "goal_buy", "title": "buy"},
            {"id": "goal_sell", "title": "sell"},
            {"id": "goal_rent", "title": "rent"},
        ]
        question = "Perfect, are you looking to buy, sell, or rent?"
        return {"buttons": button, "body": question}


    def pre_flow_base_question(self):
        button = [
            {"id": "approved", "title": "start"}
        ]
        question = "Hey! Welcome 👋 I'll ask you a few quick questions to get started — please send one answer per message so everything stays clear."
        return {"buttons": button, "body": question}


    def budget_buy_base_questions(self):
        return [
            "What's your buying budget?"
        ]


    def budget_sell_base_questions(self):
        return [
            "What price are you hoping to sell for?"
        ]


    def rent_role_base_questions(self):
        button = [
            {"id": "rent_renting", "title": "renting"},
            {"id": "rent_letting", "title": "letting"},
        ]
        question = "Are you looking to rent a property or let one?"
        return {"buttons": button, "body": question}


    def budget_rent_tenant_base_questions(self):
        return [
            "What's your monthly rental budget?"
        ]


    def budget_rent_landlord_base_questions(self):
        return [
            "What monthly rent are you hoping to get?"
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


    def process_base_question(self, field, ack_mode):
        print(f"PROCESS BASE QUESTION FIELD={repr(field)} ACK_MODE={repr(ack_mode)}", flush=True)

        if field == "goal":
            questions = self.goal_base_questions()
        elif field == "budget_buy":
            questions = self.budget_buy_base_questions()
        elif field == "budget_sell":
            questions = self.budget_sell_base_questions()
        elif field == "rent_role":
            questions = self.rent_role_base_questions()
        elif field == "budget_rent_renting":
            questions = self.budget_rent_tenant_base_questions()
        elif field == "budget_rent_letting":
            questions = self.budget_rent_landlord_base_questions()
        elif field == "urgency":
            questions = self.urgency_base_questions()
        elif field == "name":
            questions = self.name_base_question()
        elif field == "pre_flow":
            questions = self.pre_flow_base_question()
        else:
            raise TypeError("Invalid field")

        if field != "pre_flow" and field != "goal" and field != "rent_role":
            question = questions[0]
        else:
            question = questions

        if ack_mode == 1:
            if field != "pre_flow" and field != "goal" and field != "rent_role":
                return f"{self.build_ack_prefix()} {question}"

        return question


    def build_ack_prefix(self):
        return f"{random.choice(['Got it', 'Nice', 'Awesome', 'Perfect', 'Great', 'Thanks', 'Sounds good'])}{random.choice([',', '.'])}"



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


    def budget_buy_missing_questions(self, question_type, attempt_number):
        if attempt_number != 2:
            return

        if question_type == "no_info":
            return [
                "Even something simple is fine, do you have a buying budget in mind?"
            ]
        elif question_type == "vague":
            return [
                "Can you share a bit more about your buying budget?"
            ]
        elif question_type == "avoid":
            return [
                "Just so I can understand better, what's your buying budget?"
            ]


    def budget_sell_missing_questions(self, question_type, attempt_number):
        if attempt_number != 2:
            return

        if question_type == "no_info":
            return [
                "Even something rough is fine, what price are you hoping to sell for?"
            ]
        elif question_type == "vague":
            return [
                "Can you share a bit more about the price you're hoping to sell for?"
            ]
        elif question_type == "avoid":
            return [
                "Just so I can understand better, what price are you hoping to sell for?"
            ]


    def rent_role_missing_questions(self, question_type, attempt_number):
        if attempt_number != 2:
            return

        if question_type == "no_info":
            return [
                "Even something simple is fine, are you looking to rent a property or let one?"
            ]
        elif question_type == "vague":
            return [
                "Can you share a bit more — are you renting or letting?"
            ]
        elif question_type == "avoid":
            return [
                "Just so I can understand better, are you renting or letting?"
            ]


    def budget_rent_tenant_missing_questions(self, question_type, attempt_number):
        if attempt_number != 2:
            return

        if question_type == "no_info":
            return [
                "Even something rough is fine, what's your monthly rental budget?"
            ]
        elif question_type == "vague":
            return [
                "Can you share a bit more about your monthly rental budget?"
            ]
        elif question_type == "avoid":
            return [
                "Just so I can understand better, what's your monthly rental budget?"
            ]


    def budget_rent_landlord_missing_questions(self, question_type, attempt_number):
        if attempt_number != 2:
            return

        if question_type == "no_info":
            return [
                "Even something rough is fine, what monthly rent are you hoping to get?"
            ]
        elif question_type == "vague":
            return [
                "Can you share a bit more about the monthly rent you're hoping to get?"
            ]
        elif question_type == "avoid":
            return [
                "Just so I can understand better, what monthly rent are you hoping to get?"
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
        print(f"FIELD PROCESS: {field}" , flush=True)
        if field == "goal":
            questions = self.goal_missing_questions(reason, attempt_number)
        elif field == "budget_buy":
            questions = self.budget_buy_missing_questions(reason, attempt_number)
        elif field == "budget_sell":
            questions = self.budget_sell_missing_questions(reason, attempt_number)
        elif field == "rent_role":
            questions = self.rent_role_missing_questions(reason, attempt_number)
        elif field == "budget_rent_tenant":
            questions = self.budget_rent_tenant_missing_questions(reason, attempt_number)
        elif field == "budget_rent_landlord":
            questions = self.budget_rent_landlord_missing_questions(reason, attempt_number)
        elif field == "urgency":
            questions = self.urgency_missing_questions(reason, attempt_number)
        elif field == "phone":
            questions = self.phone_missing_questions(reason, attempt_number)
        else:
            raise TypeError(f"Invalid field: {field}")

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

    def budget_buy_confuse_questions(self, question_type):
        if question_type == "meaning":
            return [
                "I mean how much you're looking to spend on buying."
            ]
        elif question_type == "answer_type":
            return [
                "Just tell me your buying budget."
            ]
        elif question_type == "focus":
            return [
                "For now, I just need to know your buying budget."
            ]

    def budget_sell_confuse_questions(self, question_type):
        if question_type == "meaning":
            return [
                "I mean the price you're hoping to sell the property for."
            ]
        elif question_type == "answer_type":
            return [
                "Just tell me the price you're hoping to sell for."
            ]
        elif question_type == "focus":
            return [
                "For now, I just need to know the price you're hoping to sell for."
            ]

    def rent_role_confuse_questions(self, question_type):
        if question_type == "meaning":
            return [
                "I mean whether you want to rent a property or let one out."
            ]
        elif question_type == "answer_type":
            return [
                "Just tell me — renting or letting."
            ]
        elif question_type == "focus":
            return [
                "For now, I just need to know if you're renting or letting."
            ]

    def budget_rent_tenant_confuse_questions(self, question_type):
        if question_type == "meaning":
            return [
                "I mean how much you're looking to pay per month for rent."
            ]
        elif question_type == "answer_type":
            return [
                "Just tell me your monthly rental budget."
            ]
        elif question_type == "focus":
            return [
                "For now, I just need to know your monthly rental budget."
            ]

    def budget_rent_landlord_confuse_questions(self, question_type):
        if question_type == "meaning":
            return [
                "I mean how much rent you want to receive per month."
            ]
        elif question_type == "answer_type":
            return [
                "Just tell me the monthly rent you're hoping to get."
            ]
        elif question_type == "focus":
            return [
                "For now, I just need to know the monthly rent you're hoping to get."
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
        elif field == "budget_buy":
            questions = self.budget_buy_confuse_questions(reason)
        elif field == "budget_sell":
            questions = self.budget_sell_confuse_questions(reason)
        elif field == "rent_role":
            questions = self.rent_role_confuse_questions(reason)
        elif field == "budget_rent_tenant":
            questions = self.budget_rent_tenant_confuse_questions(reason)
        elif field == "budget_rent_landlord":
            questions = self.budget_rent_landlord_confuse_questions(reason)
        elif field == "urgency":
            questions = self.urgency_confuse_questions(reason)
        else:
            raise TypeError("Invalid field")

        return random.choice(questions)


class FallBackQuestions:
    def goal_fallback_questions(self, fallback_type):
        if fallback_type == "after_fallback":
            return [
                "Even a general answer helps, are you looking to buy, sell, or rent?"
            ]
        elif fallback_type == "regular_fallback":
            return [
                "Even a general answer helps, are you looking to buy, sell, or rent?"
            ]

    def budget_buy_fallback_questions(self, fallback_type):
        if fallback_type == "after_fallback":
            return [
                "Alright, let's keep going — what's your buying budget?"
            ]
        elif fallback_type == "regular_fallback":
            return [
                "Even a general answer helps, what's your buying budget?"
            ]
        else:
            raise TypeError("Invalid fallback type")

    def budget_sell_fallback_questions(self, fallback_type):
        if fallback_type == "after_fallback":
            return [
                "Alright, let's keep going — what price are you hoping to sell for?"
            ]
        elif fallback_type == "regular_fallback":
            return [
                "Even a general answer helps, what price are you hoping to sell for?"
            ]
        else:
            raise TypeError("Invalid fallback type")

    def rent_role_fallback_questions(self, fallback_type):
        if fallback_type == "after_fallback":
            return [
                "Alright, let's keep going — are you renting or letting?"
            ]
        elif fallback_type == "regular_fallback":
            return [
                "Even a general answer helps, are you renting a property or letting one?"
            ]
        else:
            raise TypeError("Invalid fallback type")

    def budget_rent_tenant_fallback_questions(self, fallback_type):
        if fallback_type == "after_fallback":
            return [
                "Alright, let's keep going — what's your monthly rental budget?"
            ]
        elif fallback_type == "regular_fallback":
            return [
                "Even a general answer helps, what's your monthly rental budget?"
            ]
        else:
            raise TypeError("Invalid fallback type")

    def budget_rent_landlord_fallback_questions(self, fallback_type):
        if fallback_type == "after_fallback":
            return [
                "Alright, let's keep going — what monthly rent are you hoping to get?"
            ]
        elif fallback_type == "regular_fallback":
            return [
                "Even a general answer helps, what monthly rent are you hoping to get?"
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
        if field == "goal":
            questions = self.goal_fallback_questions(fallback_type=reason)
        elif field == "budget_buy":
            questions = self.budget_buy_fallback_questions(fallback_type=reason)
        elif field == "budget_sell":
            questions = self.budget_sell_fallback_questions(fallback_type=reason)
        elif field == "rent_role":
            questions = self.rent_role_fallback_questions(fallback_type=reason)
        elif field == "budget_rent_tenant":
            questions = self.budget_rent_tenant_fallback_questions(fallback_type=reason)
        elif field == "budget_rent_landlord":
            questions = self.budget_rent_landlord_fallback_questions(fallback_type=reason)
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
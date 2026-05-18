import random


class BaseQuestions:
    def goal_base_questions(self):
        return [
            "What are you looking for help with?"
        ]

    def urgency_base_questions(self):
        return [
            "When are you looking to get started?"
        ]

    def phone_base_question(self):
        return [
            "What's the best number to reach you?"
        ]
#
    def process_base_question(self, field, ack_mode):
        print(f"PROCESS BASE QUESTION FIELD={repr(field)} ACK_MODE={repr(ack_mode)}", flush=True)
        if field == "goal":
            questions = self.goal_base_questions()
        elif field == "urgency":
            questions = self.urgency_base_questions()
        else:
            raise TypeError("Invalid field")

        question = random.choice(questions)

        if ack_mode == 1:
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
                "Even something simple is fine, what would you like help with?"
            ]
        elif question_type == "vague":
            return [
                "Can you share a bit more about what you're looking for help with?"
            ]
        elif question_type == "avoid":
            return [
                "Just so I can understand better, what are you looking for help with?"
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
                "I mean what you're looking for help with."
            ]
        elif question_type == "answer_type":
            return [
                "Just tell me what you're looking for help with."
            ]
        elif question_type == "focus":
            return [
                "For now, I just need to understand what you're looking for help with."
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
        elif field == "urgency":
            questions = self.urgency_confuse_questions(reason)
        else:
            raise TypeError("Invalid field")

        return random.choice(questions)


class FallBackQuestions:
    def __init__(self):
        pass

    def goal_fallback_questions(self , fallback_type):
        if fallback_type == "after_fallback":    
            return [
                "Even a general answer helps, what are you looking for help with?"
            ]
        elif fallback_type == "regular_fallback":
            return [
                "Even a general answer helps, what are you looking for help with?"
            ]

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
                "All good, when would you like to start?"
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
            questions = self.goal_fallback_questions()
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
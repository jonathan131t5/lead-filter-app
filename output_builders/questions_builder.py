import random

#אחד או מה?
class BaseQuestions:
    def goal_base_questions(self):
        return [
            "מה היית רוצה להשיג מהתהליך?"
        ]

    def preferences_base_questions(self):
        return [
           "יש משהו ספציפי שחשוב לך באיך שהתהליך יתנהל?"
        ]

    def urgency_base_questions(self):
        return [
            "מתי היית רוצה להתחיל?"
        ]

    def phone_base_question(self):
        return [
            "כדי לשמור על קשר מה הטלפון שלך?" 
        ]

    def process_base_question(self, field, ack_mode):
        if field == "goal":
            questions = self.goal_base_questions()

        elif field == "preferences":
            questions = self.preferences_base_questions()

        elif field == "urgency":
            questions = self.urgency_base_questions()

        elif field == "phone":
            questions = self.phone_base_question()

        else:
            raise TypeError("Invalid field")

        question = random.choice(questions)

        if ack_mode == 1:
            return f"{self.build_ack_prefix()} {question}"

        return question

    def build_ack_prefix(self):
        return f"{random.choice(['מעולה', 'הבנתי', 'סבבה', 'אחלה'])}{random.choice([',', '.'])}"



class MissingQuestions:
    def goal_missing_questions(self, question_type, attempt_number):
        if attempt_number != 2:
            return

        if question_type == "no_info":
            return [
                "לא כל כך הצלחתי להבין מה אתה רוצה להשיג בתהליך?"
            ]

        elif question_type == "vague":
            return [
                "תוכל לפרט קצת יותר למה הכוונה?"
            ]

        elif question_type == "avoid":
            return [
                "כדי להמשיך אני צריך להבין מה המטרה שלך"
            ]


    def preferences_missing_questions(self, question_type, attempt_number):
        if attempt_number != 2:
            return

        if question_type == "no_info":
            return [
                "תן לי להבין אם יש משהו שחשוב לך באיך שהתהליך יתנהל"
            ]


    def urgency_missing_questions(self, question_type, attempt_number):
        if attempt_number != 2:
            return

        if question_type == "no_info":
            return [
                "יש לך זמן התחלה בראש?"
            ]

        elif question_type == "vague":
            return [
                "תוכל לפרט קצת יותר מתי היית רוצה להתחיל?"
            ]

        elif question_type == "avoid":
            return [
                "אפילו זמן כללי יעזור לי"
            ]


    def phone_missing_questions(self, question_type, attempt_number):
        if question_type == "no_info":
            
            if attempt_number == 2:
                return [
                    "בלי טלפון לא נוכל להמשיך" 
                ]
            

        
        elif question_type == "invalid_format":
            if attempt_number == 2:
                return [
                    "נראה שהמספר לא מלא, תוכל לשלוח שוב?"
                ] 


    def process_missing_question(self, field, reason, attempt_number):
        if field == "goal":
            questions = self.goal_missing_questions(reason, attempt_number)

        elif field == "preferences":
            questions = self.preferences_missing_questions(reason, attempt_number)

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
                "אני מתכוון למה שאתה רוצה להשיג מהתהליך"
            ]

        elif question_type == "answer_type":
            return [
                "פשוט תכתוב מה המטרה שלך."
            ]

        elif question_type == "focus":
            return [
                "כרגע אני שואל רק על המטרה שלך"
            ]


    def preferences_confuse_questions(self , question_type):
        if question_type == "meaning":
            return [
                "אני מתכוון למה חשוב לך באיך שהתהליך יתנהל"
            ]


    def urgency_confuse_questions(self, question_type):
        if question_type == "meaning":
            return [
                "אני מתכוון למתי אתה רוצה להתחיל"
            ]

        elif question_type == "answer_type":
            return [
                "פשוט תכתוב מתי בערך היית רוצה להתחיל"
            ]

        elif question_type == "focus":
            return [
                "רק מתי אתה רוצה להתחיל"
            ]


    def process_confuse_question(self, field, reason):
        if field == "goal":
            questions = self.goal_confuse_questions(reason)

        elif field == "preferences":
            questions = self.preferences_confuse_questions(reason)

        elif field == "urgency":
            questions = self.urgency_confuse_questions(reason)

        else:
            raise TypeError("Invalid field")

        return random.choice(questions)



class FallBackQuestions:
    def __init__(self):
        pass


    def goal_fallback_questions(self):
        return [
            "גם תשובה כללית תעזור לי להבין מה המטרה שלך"
            ]
                

    def preferences_fallback_questions(self):
        return [
            "סבבה נתקדם, יש משהו שחשוב לך במיוחד באיך שהתהליך יתנהל?"
        ]
        


    def phone_fallback_question(self , fallback_type):
        if fallback_type == "after_fallback":
            return [
               "אוקי נמשיך, כדי להמשיך את ההתאמה ולחזור אליך תשאיר מספר טלפון" 
            ]
        
        elif fallback_type == "regular_fallback":
            return [
                "בלי מספר טלפון אי אפשר להמשיך את ההתאמה 🙏 אם מתאים לך, שלח מספר ונמשיך"
            ]


    
    def urgency_fallback_questions(self , fallback_type):
        if fallback_type == "after_fallback":
            return [
                "אוקי נמשיך, מתי היית רוצה להתחיל בתהליך?"
            ]
        
        elif fallback_type == "regular_fallback":
            return [
                "זה משהו שאתה רוצה להתחיל עכשיו, בקרוב, או בהמשך?"
            ]

        else:
            raise TypeError("Invaild fallback type")
        

    
    def process_fallback_question(self , field , reason):
        questions = []
        if field == "goal":
            questions = self.goal_fallback_questions()

        elif field == "preferences":
            questions = self.preferences_fallback_questions()

        elif field == "phone":
            questions = self.phone_fallback_question(fallback_type=reason)

        elif field == "urgency":
            questions = self.urgency_fallback_questions(fallback_type=reason)

        else:
            raise TypeError("Invaild field choice")

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


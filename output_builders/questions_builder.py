import random

#אחד או מה?
class BaseQuestions:
    def goal_base_questions(self):
        return [
            "מה המטרה המרכזית שאתה רוצה להשיג?",
            "מה היית רוצה להשיג או לשפר?",
            "מה היעד העיקרי שלך כרגע?"
        ]

    def preferences_base_questions(self):
        return [
            "יש משהו שחשוב לך במיוחד באיך שהתהליך יתנהל?",
           "יש משהו שחשוב לך באיך שהתהליך יתנהל?",
            "יש משהו שחשוב לך שנשים לב אליו לאורך התהליך?"
        ]

    def urgency_base_questions(self):
        return [
            "מתי היית רוצה להתחיל?",
            "מתי היית רוצה להתחיל?",
        ]

    def phone_base_question(self):
        return [
            "בכדי לחזור אלייך תשאיר מספר טלפון" , 
            "כדי לשמור על קשר מה הטלפון שלך?" , 
            "תוכל להשאיר מספר טלפון להמשך ההתאמה "
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
                "עוד לא הבנתי מה אתה מחפש",
                "תן לי להבין מה המטרה שלך",
                "מה היית רוצה להשיג?"
            ]

        elif question_type == "vague":
            return [
                "תוכל לפרט קצת יותר למה הכוונה?",
                "אשמח אם תוכל לחדד לי מעט את הנקודה הזו.",
                "אפשר קצת יותר פירוט כדי שאהיה בטוח שהבנתי?"
            ]

        elif question_type == "avoid":
            return [
                "כדי להמשיך אני צריך להבין מה המטרה שלך",
                "בלי להבין מה אתה מחפש יהיה קשה להתקדם"
            ]


    def preferences_missing_questions(self, question_type, attempt_number):
        if attempt_number != 2:
            return

        if question_type == "no_info":
            return [
                "לא כל כך הצלחתי להבין למה אתה מצפה מהתהליך עצמו",
               "לא ממש הבנתי אם יש משהו ספציפי שחשוב לך שיהיה לאורך התהליך",
                "תן לי להבין אם יש משהו שחשוב לך באיך שהתהליך יתנהל"
            ]


    def urgency_missing_questions(self, question_type, attempt_number):
        if attempt_number != 2:
            return

        if question_type == "no_info":
            return [
                "עוד לא הבנתי מתי אתה רוצה להתחיל",
                "יש לך זמן התחלה בראש?",
                "מתי זה רלוונטי לך בערך?"
            ]

        elif question_type == "vague":
            return [
                "תוכל לפרט קצת יותר מתי היית רוצה להתחיל?",
              "תחדד לי קצת יותר מתי היית רוצה להתחיל",
                "מתי אתה רואה את עצמך מתחיל בתהליך?"
            ]

        elif question_type == "avoid":
            return [
                "אפילו זמן כללי יעזור לי",
                "כדי להמשיך אני צריך להבין מתי זה מתאים לך",
                "תן לי זמן כללי שבו היית רוצה להתחיל"
            ]


    def phone_missing_questions(self, question_type, attempt_number):
        if question_type == "no_info":
            
            if attempt_number == 2:
                return [
                    "בלי טלפון לא נוכל להמשיך" , 
                    "בכדי להמשיך בתהליך תוכל להשאיר מספר טלפון" , 
                    "חסר מספר טלפון להתאמה" ,
                    "חסר מספר טלפון להמשך ההתאמה"
                ]
            

        
        elif question_type == "invalid_format":
            if attempt_number == 2:
                return [
                    "נראה שהמספר לא מלא, תוכל לשלוח שוב?",
                    "המספר ששלחת לא תקין, תשלח בבקשה מספר מלא",
                    "כנראה חסרות ספרות במספר, תוכל לרשום שוב?",
                    "לא הצלחתי לזהות מספר תקין, תשלח בבקשה שוב"
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
                "אני מתכוון למה שאתה רוצה להשיג",
                "הכוונה היא למה המטרה שלך",
                "אני מנסה להבין מה אתה רוצה להשיג מהתהליך"
            ]

        elif question_type == "answer_type":
            return [
                "פשוט תכתוב מה הכיוון הכללי שלך.",
                "פשוט תכתוב מה המטרה שלך.",
                "תרשום פשוט מה היעד שאתה מכוון אליו."
            ]

        elif question_type == "focus":
            return [
                "כרגע אני שואל רק על המטרה שלך",
                "רק מה אתה רוצה להשיג",
                "אני צריך להבין רק מה אתה רוצה להשיג כרגע"
            ]


    def preferences_confuse_questions(self , question_type):
        if question_type == "meaning":
            return [
                "אני מתכוון למה חשוב לך באיך שהתהליך יתנהל",
                "כלומר איך היית רוצה שהתהליך ירגיש לך",
                "אני מתכוון אם יש משהו שחשוב לך שנשים לב אליו לאורך התהליך"
            ]


    def urgency_confuse_questions(self, question_type):
        if question_type == "meaning":
            return [
                "אני מתכוון למתי אתה רוצה להתחיל",
               "כלומר מתי מתאים לך להתחיל",
                "הכוונה היא מתי אתה רואה את עצמך מתחיל בתהליך?"
            ]

        elif question_type == "answer_type":
            return [
                "פשוט תכתוב מתי בערך היית רוצה להתחיל",
                "אפשר גם זמן כללי",
                "תרשום מתי בערך תרצה להתחיל"
            ]

        elif question_type == "focus":
            return [
                "כרגע אני שואל רק על הזמן",
                "רק מתי אתה רוצה להתחיל",
                "אני צריך להבין רק מתי אתה רוצה להתחיל"
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
            "זה יותר משהו ספציפי או מטרה כללית?",
            "גם תשובה כללית תעזור לי להבין מה המטרה שלך",
            "יש לך משהו ספציפי שהיית רוצה להגיע אליו או אפילו משהו כללי?"
            ]
                

    def preferences_fallback_questions(self):
        return [
            "סבבה נתקדם, יש משהו שחשוב לך במיוחד באיך שהתהליך יתנהל?",
            "אוקי נעבור הלאה, יש משהו שחשוב לך שנשים לב אליו לאורך התהליך?",
            "טוב נתקדם, איך היית רוצה שהתהליך ירגיש לך?"
        ]
        


    def phone_fallback_question(self , fallback_type):
        if fallback_type == "after_fallback":
            return [
                "אוקי, נמשיך  כדי שנחזור אליך תשאיר בבקשה מספר טלפון" , 
               "אוקי נמשיך, כדי להמשיך את ההתאמה ולחזור אליך תשאיר מספר טלפון" , 
                "אוקי נעבור הלאה, בכדי להמשיך את ההתאמה ויצירת קשר בהמשך תשאיר מספר טלפון" , 
                "אוקי נתקדם, כדי להמשיך את התהליך ולחזור אליך תשאיר טלפון"


            ]
        
        elif fallback_type == "regular_fallback":
            return [
                "בלי מספר טלפון אי אפשר להמשיך להתאמה 🙏 אם מתאים לך, שלח מספר ונמשיך" , 
                "לא ניתן להמשיך בלי מספר טלפון אם תרצה להמשיך, תזין את מספר הטלפון שלך" , 
                "בלי טלפון התהליך עוצר כאן. כשמוכן, תזין את מספרף ונמשיך" , 
                "בלי מספר לא ניתן להמשיך את ההתאמה. תשתף את מספר הטלפון שלך כשתהיה מוכן"
            ]


    
    def urgency_fallback_questions(self , fallback_type):
        if fallback_type == "after_fallback":
            return [
                "אוקי נמשיך, מתי היית רוצה להתחיל בתהליך?",
                "סבבה נתקדם, מתי היית רוצה להתחיל בתהליך?",
                "אוקי, נמשיך, מתי היית רוצה להתחיל בתהליך?"
            ]
        
        elif fallback_type == "regular_fallback":
            return [
                "מה יותר קרוב אליך?\n1. בימים הקרובים\n2. בשבועות הקרובים\n3. מתישהו בהמשך",
                "כמה זה דחוף לך להתחיל מ-1 עד 10?",
                "זה משהו שאתה רוצה להתחיל עכשיו, בקרוב, או בהמשך?",
                "תוך כמה זמן אתה רואה את עצמך מתחיל?\nימים / שבועות / חודשים"
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


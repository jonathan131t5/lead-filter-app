import random

class BaseQuestions:
    def __init__(self):
        pass


    def goal_Base_questions(self):
        return [
            "מה אתה רוצה להשיג מהאימונים?",
            "מה המטרה שלך כרגע באימונים?",
            "מה אתה רוצה לשפר אצלך בתקופה הקרובה?",
            "מה היית רוצה לשפר או לחזק בגוף שלך?"
            ]


    def budget_Base_questions(self):
        return [
            "כמה אתה מוכן להשקיע בתהליך?",
            "יש לך תקציב מסוים בראש?",
            "על איזה טווח מחיר אתה חושב?",
            "כמה אתה מתכנן לשים על זה?"
            ]


    def urgency_Base_questions(self):
        return [
            "מתי אתה רוצה להתחיל?",
            "מתי זה רלוונטי לך?",
            "יש לך זמן התחלה בראש?",
            "מתי אתה מתכנן להתחיל בפועל?"
            ]
    

    def process_base_question(self , field , ack_mode):
        if field == "goal":
            questions = self.goal_Base_questions()

        elif field == "budget":
            questions = self.budget_Base_questions()

        elif field == "urgency":
            questions = self.urgency_Base_questions()

        else:
            raise TypeError("Invaild field choice")

        question = random.choice(questions)
        if ack_mode == 1:
            prefix = self.build_ack_prefix()
            return f"{prefix} {question}"
        
        return question

    
    def build_ack_prefix(self):
        ack = self.get_ack()
        punctuation_mark = self.get_punctuation()

        return f"{ack}{punctuation_mark}"
    
    
    def get_ack(self):
        ack_found = [
        "מעולה",
        "הבנתי",
        "סבבה",
        "אחלה"
        ]
        return random.choice(ack_found)
    
    def get_punctuation(self):
        punctuation = {
            "comma": "," , 
            "period": "."
        }
        return random.choice(list(punctuation.values()))



class MissingQuestions:
    def __init__(self):
        pass



    def goal_missing_questions(self, question_type, attempt_number):
        if question_type == "no_info":

            if attempt_number == 1:
                return [
                    "כדי להתקדם אני צריך להבין מה המטרה שלך",
                    "מה היעד שאתה מכוון אליו?",
                    "על מה אתה רוצה לעבוד בעיקר?"
                ]

            elif attempt_number == 2:
                return [
                    "חסר לי להבין מה אתה רוצה להשיג",
                    "מה חשוב לך להגיע אליו?",
                    "לאן אתה רוצה להגיע בתהליך הזה?"
                ]

            elif attempt_number == 3:
                return [
                    "איזה תוצאה היית רוצה לראות?",
                    "מה המטרה המרכזית שלך?",
                    "מה הדבר העיקרי שאתה רוצה להשיג?"
                ]


        elif question_type == "vague":

            if attempt_number == 1:
                return [
                    "תן לי קצת יותר פירוט על המטרה שלך",
                    "תחדד לי מה אתה רוצה להשיג",
                    "תסביר לי יותר לאן אתה מכוון"
                ]

            elif attempt_number == 2:
                return [
                    "אני צריך קצת יותר כיוון כדי להבין אותך",
                    "מה בדיוק אתה רוצה לשפר?",
                    "איזה שינוי אתה מחפש?"
                ]

            elif attempt_number == 3:
                return [
                    "מה התוצאה שאתה מכוון אליה?",
                    "תן לי דוגמה למה שאתה רוצה להשיג",
                    "איך זה ייראה כשזה יצליח?"
                ]


        elif question_type == "avoid":

            if attempt_number == 1:
                return [
                    "בלי להבין מטרה יהיה קשה לדייק לך",
                    "אני צריך כיוון ממך כדי להמשיך",
                    "תן לי להבין מה אתה רוצה להשיג"
                ]

            elif attempt_number == 2:
                return [
                    "מה חשוב לך להגיע אליו?",
                    "אני חייב כיוון בסיסי כדי להמשיך",
                    "בלי מטרה קשה להתקדם, תן כיוון"
                ]

            elif attempt_number == 3:
                return [
                    "מה הדבר העיקרי שאתה רוצה להשיג?",
                    "תן יעד כללי כדי שנוכל לזוז",
                    "אפילו כיוון קטן יעזור להתקדם"
                ]
            

    

    def budget_missing_questions(self, question_type, attempt_number):

        if question_type == "no_info":

            if attempt_number == 1:
                return [
                    "יש לך טווח מסוים בראש?",
                    "כמה בערך חשבת להשקיע על זה?",
                    "על איזה אזור מחיר אתה חושב?"
                ]

            elif attempt_number == 2:
                return [
                    "אפילו טווח כללי יעזור לי להבין",
                    "מה בערך הסכום שאתה חושב עליו?",
                    "על איזה סדר גודל מדובר?"
                ]

            elif attempt_number == 3:
                return [
                    "תן לי טווח בערך כדי להתקדם",
                    "גם הערכה גסה תעזור לי להבין אותך",
                    "מה האזור מחיר שאתה מכוון אליו בערך?"
                ]


        elif question_type == "vague":

            if attempt_number == 1:
                return [
                    "תחדד לי קצת את הסכום",
                    "אפשר טווח קצת יותר ברור?",
                    "כמה זה יוצא בערך במספרים?"
                ]

            elif attempt_number == 2:
                return [
                    "אני צריך טווח יותר ממוקד כדי להבין אותך",
                    "על איזה אזור מחיר זה יושב אצלך?",
                    "תן לי סדר גודל יותר ברור"
                ]

            elif attempt_number == 3:
                return [
                    "אפשר לצמצם את זה לטווח יותר ספציפי?",
                    "כמה זה בערך יותר מדויק?",
                    "מה הסכום שאתה רואה לנכון בערך?"
                ]


        elif question_type == "avoid":

            if attempt_number == 1:
                return [
                    "רק כדי לכוון אותך נכון — יש טווח שמתאים לך?",
                    "זה יעזור לי לדייק — על איזה אזור מחיר חשבת?",
                    "יש כיוון כללי של סכום שאתה מרגיש איתו נוח?"
                ]

            elif attempt_number == 2:
                return [
                    "בלי טווח יהיה קשה להתאים לך משהו מדויק",
                    "גם סדר גודל כללי יספיק כדי להתקדם",
                    "תן לי טווח בערך כדי שאוכל לכוון אותך"
                ]

            elif attempt_number == 3:
                return [
                    "בוא ניקח טווח כללי רק כדי להתקדם",
                    "אפילו הערכה גסה תספיק כדי שנמשיך",
                    "מה האזור מחיר שאתה רואה לנכון?"
                ]



    def urgency_missing_questions(self, question_type, attempt_number):

        if question_type == "no_info":

            if attempt_number == 1:
                return [
                    "צריך להבין זמנים כדי להמשיך",
                    "מתי זה אמור לקרות מבחינתך?",
                    "מתי אתה רוצה להיכנס לזה?"
                ]

            elif attempt_number == 2:
                return [
                    "אני צריך להבין בערך מתי זה מתאים לך",
                    "מתי חשבת להתחיל?",
                    "על איזה טווח זמן מדובר?"
                ]

            elif attempt_number == 3:
                return [
                    "תן לי זמן כללי כדי להתקדם",
                    "אפילו הערכה גסה תעזור",
                    "מתי בערך זה רלוונטי לך?"
                ]


        elif question_type == "vague":

            if attempt_number == 1:
                return [
                    "תן זמן בערך",
                    "מתי אתה רואה את עצמך מתחיל עם זה?",
                    "מתי זה מתאים לך להתחיל?"
                ]

            elif attempt_number == 2:
                return [
                    "תן לי בבקשה זמן יותר מדויק",
                    "תוך כמה זמן אתה רואה את עצמך מתחיל?" 
                    "תחדד לי קצת את הזמנים"
                ]

            elif attempt_number == 3:
                return [
                    "מתי בערך זה קורה בפועל?",
                    "תן לי טווח זמן ברור יותר",
                    "כמה זמן לוקח עד שאתה מתחיל?"
                ]


        elif question_type == "avoid":

            if attempt_number == 1:
                return [
                    "כדי להתקדם אני צריך זמן ממך",
                    "בלי לדעת מתי זה קורה קשה להמשיך",
                    "תן לי להבין מתי זה מתאים לך"
                ]

            elif attempt_number == 2:
                return [
                    "מתי כן רלוונטי לך להתחיל?",
                    "בלי זמן קשה להתקדם",
                    "תן לי כיוון של מתי זה קורה"
                ]

            elif attempt_number == 3:
                return [
                    "אפילו זמן כללי יעזור להתקדם",
                    "תן הערכה מתי זה קורה",
                    "מתי בערך אתה מתכנן להתחיל?"
                ]
    


    def process_missing_question(self , field , reason , attempt_number):
        questions = []
        if field == "goal":
            questions = self.goal_missing_questions(question_type=reason , attempt_number=attempt_number)

        elif field == "budget":
            questions = self.budget_missing_questions(question_type=reason , attempt_number=attempt_number)

        elif field == "urgency":
            questions = self.urgency_missing_questions(question_type=reason , attempt_number=attempt_number)

        else:
            raise TypeError("Invaild field choice")

        return random.choice(questions)
    
    
class ConfuseQuestions:
    def __init__(self):
        pass    
    
    
    def goal_confuse_questions(self, question_type):
        if question_type == "meaning":
            return [
                "אני שואל מה אתה רוצה להשיג",
                "הכוונה היא למה שאתה רוצה להגיע אליו",
                "מדובר במה שאתה רוצה לשפר",
               "לאן אתה רוצה להגיע?"
            ]
        
        elif question_type == "answer_type":
            return [
                "תכתוב מה אתה רוצה להשיג",
                "תענה עם המטרה שלך",
                "תרשום מה היעד שלך",
                "תכתוב מה אתה רוצה לשפר"
            ]
            
        elif question_type == "focus":
            return [
                "רק מה אתה רוצה להשיג",
                "אני שואל רק על המטרה שלך",
                "כרגע רק מה היעד שלך",
                "רק על מה שאתה רוצה להגיע אליו"
            ]
        

    def budget_confuse_questions(self, question_type):
        if question_type == "meaning":
            return [
               "בערך כמה מתאים לך להשקיע",
                "הכוונה לכיוון כללי של סכום שמתאים לך",
                "אני שואל על סדר גודל של מה שמתאים לך לשים",
                "פשוט להבין בערך איזה תקציב מתאים לך"
            ]
            
        elif question_type == "answer_type":
            return [
                "תן לי בערך סכום או טווח",
                "אפילו כיוון כללי של סכום זה מספיק",
                "מה בערך הסכום שאתה חושב עליו?",
                "תן לי סדר גודל של תקציב"
            ]

            
        elif question_type == "focus":
            return [
                "רק מבחינת תקציב, בערך כמה מתאים לך?",
                "כרגע רק להבין כיוון של סכום",
                "רק לדעת בערך איזה תקציב מתאים לך",
                "רק מה הכיוון שלך מבחינת סכום"
            ]
        

    def urgency_confuse_questions(self, question_type):
        if question_type == "meaning":
            return [
                "אני שואל מתי אתה רוצה להתחיל",
                "הכוונה למתי זה מתאים לך להתחיל את התהליך",
                "מדובר במתי אתה חושב להתחיל",
                "אני מתכוון למתי זה מתאים לך להתחיל"
            ]
        
        elif question_type == "answer_type":
            return [
                "כתוב מתי בערך זה מתאים לך להתחיל",
                "תענה עם זמן",
                "תרשום מתי אתה רוצה להתחיל",
                "תן לי זמן בערך"
            ]
            
        elif question_type == "focus":
            return [
                "רק מתי אתה מתחיל",
                "אני שואל רק על זמן",
                "כרגע רק מתי",
                "רק זמן"
            ]
        

    def process_confuse_question(self , field , reason):
        questions = []
        if field == "goal":
            questions = self.goal_confuse_questions(question_type=reason)

        elif field == "budget":
            questions = self.budget_confuse_questions(question_type=reason)

        elif field == "urgency":
            questions = self.urgency_confuse_questions(question_type=reason)

        else:
            raise TypeError("Invaild field choice")

        return random.choice(questions)
        


class FallBackQuestions:
    def __init__(self):
        pass


    def goal_fallback_questions(self):
        return [
            "למה בכלל החלטת להתחיל עכשיו?",
            "מה גרם לך לרצות להיכנס לזה?",
            "מה הסיבה שאתה רוצה להתחיל?",
            "מה דוחף אותך להתחיל דווקא עכשיו?"
        ]
    

    def budget_fallback_questions(self , fallback_type):
        if fallback_type == "after_fallback":
            return [
                "אוקי, נתקדם לתקציב — כמה בערך חשבת להשקיע?",
                "סבבה, נעבור לתקציב — יש לך טווח מסוים בראש?",
                "אוקי, נמשיך — על איזה אזור מחיר אתה חושב?",
                "טוב, נתקדם לתקציב — כמה בערך אתה רואה את עצמך משקיע?"
            ]
        
        elif fallback_type == "regular_fallback":
            return [
                "מה יותר קרוב למה שחיפשת?\n1. עד 250₪\n2. 250-450₪\n3. 450₪+",
                "איזה טווח יותר מתאים לך כרגע?\n1. עד 250₪\n2. 250-450₪\n3. 450₪+",
                "מה נשמע לך יותר באזור שלך?\n1. עד 250₪\n2. 250-450₪\n3. 450₪+",
                "לאיזה אזור מחיר אתה יותר מתחבר?\n1. עד 250₪\n2. 250-450₪\n3. 450₪+"
            ]
        
        else:
            raise TypeError("Invaild fallback type")
        
    
    def urgency_fallback_questions(self , fallback_type):
        if fallback_type == "after_fallback":
            return [
                "אוקי, נתקדם לזמן — מתי היית רוצה להתחיל?",
                "סבבה, נעבור לזמן — מתי זה מתאים לך להתחיל?",
                "אוקי, נמשיך — כמה זה דחוף לך להתחיל?",
                "טוב, נתקדם — מתי אתה רואה את עצמך מתחיל?"
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

        elif field == "budget":
            questions = self.budget_fallback_questions(fallback_type=reason)

        elif field == "urgency":
            questions = self.urgency_fallback_questions(fallback_type=reason)

        else:
            raise TypeError("Invaild field choice")

        return random.choice(questions)
        




class ProcessQuestion:
    def __init__(self , base_questions , missing_questions , confuse_questions , fallback_questions):
        self.base_questions = base_questions
        self.missing_questions = missing_questions
        self.confuse_questions = confuse_questions
        self.fallback_questions = fallback_questions



    
    
    
    def get_question(self , field , question_state , reason , attempt_number , ack_mode=1):
        if question_state == "base":
            question = self.base_questions.process_base_question(field , ack_mode)

        elif question_state == "missing":
            question = self.missing_questions.process_missing_question(field=field , reason=reason , attempt_number=attempt_number)

        elif question_state == "confused":
            question = self.confuse_questions.process_confuse_question(field=field , reason=reason)

        elif question_state == "fallback":
            question = self.fallback_questions.process_fallback_question(field=field , reason=reason)

        return question
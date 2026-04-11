import random

class RegularQuestions:
    def __init__(self):
        pass


    def goal_regular_questions(self):
        return [
            "מה אתה רוצה להשיג מהאימונים?",
            "מה המטרה שלך כרגע באימונים?",
            "מה אתה רוצה לשפר אצלך בתקופה הקרובה?",
            "לאן אתה רוצה להגיע עם זה?"
            ]


    def budget_regular_questions(self):
        return [
            "כמה אתה מוכן להשקיע בתהליך?",
            "יש לך תקציב מסוים בראש?",
            "על איזה טווח מחיר אתה חושב?",
            "כמה אתה מתכנן לשים על זה?"
            ]


    def urgency_regular_questions(self):
        return [
            "מתי אתה רוצה להתחיל?",
            "מתי זה רלוונטי לך?",
            "יש לך זמן התחלה בראש?",
            "מתי אתה מתכנן להתחיל בפועל?"
            ]



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
                    "צריך להבין תקציב כדי להמשיך",
                    "מה התקציב שאתה מכוון אליו?",
                    "כמה זה אמור להיות מבחינתך?"
                ]

            elif attempt_number == 2:
                return [
                    "אין לי עדיין כיוון של סכום ממך",
                    "כמה בערך חשבת להשקיע?",
                    "על איזה סדר גודל מדובר?"
                ]

            elif attempt_number == 3:
                return [
                    "תן לי מספר גס כדי להתקדם",
                    "אפילו טווח יעזור לי להבין",
                    "מה הסכום בערך שאתה רואה לנכון?"
                ]


        elif question_type == "vague":

            if attempt_number == 1:
                return [
                    "תן לי סדר גודל של סכום",
                    "בערך כמה מדובר?",
                    "תן לי מספר בערך"
                ]

            elif attempt_number == 2:
                return [
                    "תחדד לי קצת את המספר",
                    "על איזה טווח אתה מדבר?",
                    "תן לי כיוון יותר מדויק"
                ]

            elif attempt_number == 3:
                return [
                    "כמה בערך זה יוצא במספרים?",
                    "תן לי סכום משוער",
                    "מה התקציב בערך שאתה מייעד לזה?"
                ]


        elif question_type == "avoid":

            if attempt_number == 1:
                return [
                    "בלי תקציב קשה להתקדם מכאן",
                    "צריך מספר כדי לכוון אותך נכון",
                    "תן לי כיוון של סכום כדי להמשיך"
                ]

            elif attempt_number == 2:
                return [
                    "כמה אתה רואה את עצמך משקיע?",
                    "בלי מספר קשה לי לדייק לך",
                    "תן לפחות טווח כדי שנוכל להתקדם"
                ]

            elif attempt_number == 3:
                return [
                    "אפילו סכום כללי יעזור להתקדם",
                    "תן הערכה גסה כדי שנמשיך",
                    "מה הסכום המינימלי שאתה חושב עליו?"
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
                    "תוך כמה זמן אתה רואה את עצמך מתחיל?" ת
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
                "אני שואל כמה אתה מוכן להשקיע",
                "הכוונה לסכום שאתה רוצה לשים",
                "מדובר בכמה כסף אתה מתכנן לשלם",
                "אני מתכוון לתקציב שלך"
            ]
        
        elif question_type == "answer_type":
            return [
                "תכתוב סכום",
                "תענה עם תקציב",
                "תרשום כמה אתה משקיע",
                "תן סכום"
            ]
            
        elif question_type == "focus":
            return [
                "רק כמה אתה משקיע",
                "אני שואל רק על תקציב",
                "כרגע רק סכום",
                "רק כמה כסף"
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
        


class FallBackQuestions:
    def __init__(self):
        pass


    def goal_fallback_questions(self):
        return
    

    def budget_fallback_questions(self , fallback_type):
        if fallback_type == "after":
            return [
                "אוקי, נתקדם — בערך איזה תקציב יש לך לזה?" ,
                "סבבה, אז בוא ניגע במספרים — כמה אתה מוכן להשקיע?" ,
                "לא נורא, נמשיך — על איזה סכום חשבת להשקיע בתהליך?"
                ]
        
    
    def urgency_fallback_questions(self , fallback_type):
        if fallback_type == "to start":
            return [
                "הבנתי, נתקדם — מתי היית רוצה להתחיל?" ,
               "סבבה, אז מתי זה רלוונטי לך להתחיל?" ,
               "אוקי, נמשיך — תוך כמה זמן בא לך להתחיל?"
            ]
        
        elif fallback_type == "to end":
            return [
                "סבבה, נתקדם." ,
               "יאללה, ממשיכים." ,
               "קיבלתי, ממשיכים."
            ]




class ProcessQuestion:
    def __init__(self):
        pass

    
    def process_questions(self , mode , question_type):
        if mode == "goal":
            questions = self.goal_questions(question_type=question_type)

        elif mode == "budget":
            questions = self.budget_quesitons(question_type=question_type)

        elif mode == "urgency":
            questions = self.urgency_quesitons(question_type=question_type)

        else:
            raise ValueError("Invalid mode")

        return random.choice(questions)
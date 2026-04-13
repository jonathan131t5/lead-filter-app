import requests
from openai import OpenAI 
from dotenv import load_dotenv
import os
import json
import sqlite3
from bidi.algorithm import get_display
import time
import random

load_dotenv()
ai_key = os.getenv("OPENAI_API_KEY")

def validate_int(value, name):  
    if value is None:
        raise ValueError(f"{name} cannot be None")
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value < 0:
        raise ValueError(f"{name} cannot be negative")

def validate_str(value, name):
    if value is None:
        raise ValueError(f"{name} cannot be None")
    if not value.strip():
        raise ValueError(f"{name} cannot be empty")
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")

    

class DataAccess:
    def __init__(self):
        self.conn = sqlite3.connect("lead_qualification.db", check_same_thread=False)
        self.cursor = self.conn.cursor()


    
    def create_leads_info_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads_info(
        lead_id INTEGER PRIMARY KEY AUTOINCREMENT , 
        name TEXT ,
        phone_number TEXT UNIQUE NOT NULL ,
        status TEXT Default pending ,
        summary TEXT ,
        current_field TEXT DEFAULT goal ,
        attempt_number INTEGER DEFAULT 0 ,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,
        updated_at TIMESTAMP,
        last_interaction_at TIMESTAMP                 
        )                   
        """)
        self.conn.commit()

    

    def create_leads_scores_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads_scores(
        lead_id INTEGER PRIMARY KEY ,
        goal_score INTEGER DEFAULT 0 ,
        budget_score INTEGER DEFAULT 0 ,
        urgency_score INTEGER DEFAULT 0,
        score_count INTEGER DEFAULT 0 ,
        total_score INTEGER DEFAULT 0
        )                 
        """)
        self.conn.commit()
    
    
    
    def create_leads_messages_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads_messages(
        message_id INTEGER PRIMARY KEY AUTOINCREMENT ,
        lead_id INTEGER ,
        role TEXT ,
        content TEXT ,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )                   
        """)
        self.conn.commit()


    
    def create_leads_fields_data(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads_fields_data(
        lead_id INTEGER PRIMARY KEY , 
        goal_bot TEXT ,
        goal_user TEXT ,
        budget_bot TEXT ,
        budget_user TEXT ,
        urgency_bot TEXT ,
        urgency_user TEXT ,
        updated_at TIMESTAMP
        )
        """)
        self.conn.commit()

    
    
    
    def add_lead_message(self , lead_id , role , content):   
        self.cursor.execute(
        "INSERT INTO leads_messages (lead_id , role , content) VALUES (? , ? , ?)" ,
        (lead_id , role , content)
        )
        self.conn.commit()


    
    def create_new_lead_score(self , lead_id):
        self.cursor.execute(
        "INSERT INTO leads_scores (lead_id) VALUES(?)" , 
        (lead_id , )
        )
        self.conn.commit()
    
    
    
    def create_new_lead(self , name , phone_number):
        self.cursor.execute(
        "INSERT INTO leads_info (name , phone_number) VALUES(? , ?)" , 
        (name , phone_number)
        )
        self.conn.commit()


    def create_new_fields_data(self , lead_id):
        self.cursor.execute(
        "INSERT INTO leads_fields_data (lead_id) VALUES (?)" ,
        (lead_id , )
        )
        self.conn.commit()

    
    def update_lead_score_info(self , lead_id , score_count , total_score , score_field , value):
        self.cursor.execute(
        f"UPDATE leads_scores SET score_count = ? , total_score = ? , {score_field} = ? WHERE lead_id = ?" , 
        (score_count , total_score , value , lead_id)
        )
        self.conn.commit()

    
    
    def set_lead_status(self , lead_id , status):
        self.cursor.execute(
        "UPDATE leads_info SET status = ? WHERE lead_id = ?" ,
        (status , lead_id)
        )
        self.conn.commit()

    
    
    def get_lead_status(self , lead_id):
        self.cursor.execute(
        "SELECT status FROM leads_info WHERE lead_id = ?" ,
        (lead_id , )
        )

        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return result[0]

    
    
    def update_lead_current_field(self , lead_id , updated_field):
        self.cursor.execute(
        "UPDATE leads_info SET current_field = ? WHERE lead_id = ?" , 
        (updated_field , lead_id)
        )
        self.conn.commit()
    
    
    def update_lead_attempt_number(self , lead_id , number):
        self.cursor.execute(
        "UPDATE leads_info SET attempt_number = ? WHERE lead_id = ?" , 
        (number , lead_id)
        )
        self.conn.commit()


    
    def get_lead_base_info(self , phone_number):
        self.cursor.execute(
        "SELECT lead_id , name , current_field , attempt_number , status , summary FROM leads_info WHERE phone_number = ?" , 
        (phone_number , )
        )
        
        result = self.cursor.fetchone()
        if result is None:
            return None
    
        return {
            "phone_number" : phone_number , 
            "lead_id" : result[0] ,
            "name" : result[1] ,
            "current_field" : result[2] ,
            "attempt_number" : result[3] ,
            "status" : result[4] ,
            "summary" : result[5]
        }
    

    def get_lead_score_info(self , lead_id):
        self.cursor.execute(
        "SELECT total_score , score_count , goal_score , budget_score , urgency_score FROM leads_scores WHERE lead_id = ?" ,
        (lead_id , )
        )
        
        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return {
            "lead_id" : lead_id ,
            "total_score" : result[0] , 
            "score_count" : result[1] ,
            "goal_score" : result[2] , 
            "budget_score" : result[3] ,
            "urgency_score" : result [4]
        }
    

    
    def create_lead_fields_data(self , lead_id):
        self.cursor.execute(
        "INSERT INTO leads_fields_data (lead_id) VALUES (?)" ,
        (lead_id , )
        )
        self.conn.commit()


    def update_lead_field_data(self , lead_id , field , value):
        self.cursor.execute(
        f"UPDATE leads_fields_data SET {field} = ? WHERE lead_id = ?" ,
        (value , lead_id)
        )
        self.conn.commit()


    def get_lead_specific_field_data(self , lead_id , field):
        self.cursor.execute(
        f"SELECT {field} FROM leads_fields_data WHERE lead_id = ?" , 
        (lead_id ,)
        )

        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return result[0]
    

    def get_all_lead_field_data(self , lead_id):
        self.cursor.execute(
        "SELECT goal_user , budget_user , urgency_user FROM leads_fields_data WHERE lead_id = ?" , 
        (lead_id , )
        )

        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return {
            "lead_id" : lead_id ,
            "goal_user" : result[0] ,
            "budget_user" : result[1] ,
            "urgency_user" : result[2]
        }
    


    def get_last_exchange(self , lead_id):
        self.cursor.execute(
        "SELECT role , content FROM leads_messages WHERE lead_id = ? ORDER BY message_id DESC LIMIT 3" ,
        (lead_id , )
        )


        raw_messages = self.cursor.fetchall()
        if not raw_messages:
            return []
        
        final_messages = raw_messages[::-1]
        
        ai_input = []
        for role , content in final_messages:
            ai_input.append({"role" : role , "content" : content})

        return ai_input


    def get_lead_total_score(self , lead_id):
        self.cursor.execute(
        "SELECT total_score FROM leads_scores WHERE lead_id = ?" ,
        (lead_id , )
        )
        
        result = self.cursor.fetchone()
        if result is None:
            return None
        
        return result[0]
    

    def upload_summary(self , lead_summary , lead_id):
        self.cursor.execute(
        "UPDATE leads_info SET summary = ? WHERE lead_id = ?" , 
        (lead_summary , lead_id)
        )
        self.conn.commit()
        
    
   

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



    def goal_missing_questions(self , question_type):
        if question_type == "no_info": 
            return [
                "כדי להתקדם אני צריך להבין מה המטרה שלך",
                "חסר לי להבין מה אתה רוצה להשיג",
                "מה היעד שאתה מכוון אליו?",
                "על מה אתה רוצה לעבוד בעיקר?"
                ]
            
        elif question_type == "vague": 
            return [
                "תן לי קצת יותר פירוט על המטרה שלך", 
                "תחדד לי מה אתה רוצה להשיג" , 
                "תסביר לי יותר לאן אתה מכוון" , 
                "אני צריך קצת יותר כיוון כדי להבין אותך"
                ]
        
        elif question_type == "avoid":
            return [
                "בלי להבין מטרה יהיה קשה לדייק לך",
                "אני צריך כיוון ממך כדי להמשיך",
                "תן לי להבין מה אתה רוצה להשיג",
                "מה חשוב לך להגיע אליו?"
                ]


    

    def budget_missing_questions(self, question_type):   
        if question_type == "no_info": 
            return [
                "צריך להבין תקציב כדי להמשיך",
                "אין לי עדיין כיוון של סכום ממך",
                "מה התקציב שאתה מכוון אליו?",
                "כמה זה אמור להיות מבחינתך?"
            ]
            
        elif question_type == "vague": 
            return [
                "תן לי סדר גודל של סכום",
                "בערך כמה מדובר?",
               "תן לי מספר בערך",
                "תחדד לי קצת את המספר"
            ]
        
        elif question_type == "avoid":
            return [
                "בלי תקציב קשה להתקדם מכאן",
                "צריך מספר כדי לכוון אותך נכון",
                "תן לי כיוון של סכום כדי להמשיך",
                "כמה אתה רואה את עצמך משקיע?"
            ]



    def urgency_missing_questions(self, question_type):
        if question_type == "no_info": 
            return [
                "צריך להבין זמנים כדי להמשיך",
                "אני צריך להבין בערך מתי זה מתאים לך",
                "מתי זה אמור לקרות מבחינתך?",
                "מתי אתה רוצה להיכנס לזה?"
            ]
            
        elif question_type == "vague": 
            return [
                "תן זמן בערך",
                "מתי אתה רואה את עצמך מתחיל עם זה?",
                "מתי זה מתאים לך להתחיל?",
               "תן לי בבקשה זמן יותר מדויק"
            ]
        
        elif question_type == "avoid":
            return [
                "כדי להתקדם אני צריך זמן ממך",
                "בלי לדעת מתי זה קורה קשה להמשיך",
                "תן לי להבין מתי זה מתאים לך",
                "מתי כן רלוונטי לך להתחיל?"
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





class ConversationBuilder:
    def __init__(self):
        pass



    def analyze_prompt(self, current_field, content):
        print("chill")
        return [
            {
                "role": "system",
                "content": (
                    "אתה חלק ממערכת סינון לידים של מאמן כושר.\n"
                    "המערכת שואלת את המשתמש כל פעם שאלה אחת בלבד.\n"
                    "כל שאלה שייכת לשדה אחד בלבד: goal, budget, urgency.\n\n"

                    "התפקיד שלך:\n"
                    "לנתח רק את תשובת המשתמש האחרונה ולבדוק אם היא עונה על השדה הנוכחי.\n\n"

                    "חשוב מאוד:\n"
                    "- אסור לעבור לשדה אחר\n"
                    "- אסור לשנות נושא\n"
                    "- אסור להזכיר שדות אחרים\n"
                    "- אתה מתייחס רק ל: " + current_field + "\n\n"

                    "החזר JSON בלבד באחד מהפורמטים:\n\n"

                    "אם יש מידע:\n"
                    "{"
                    "\"status\":\"found\","
                    "\"value\":NUMBER,"
                    "\"ack\":\"TEXT\""
                    "}\n\n"

                    "אם אין מידע:\n"
                    "{"
                    "\"status\":\"missing\""
                    "}\n\n"

                    "אם המשתמש מבולבל:\n"
                    "{"
                    "\"status\":\"confused\","
                    "\"clarify\":\"TEXT\""
                    "}\n\n"

                    "====================\n"

                    "goal:\n"
                    "כל מטרה שקשורה לכושר נחשבת מידע.\n"
                    "דוגמאות:\n"
                    "'להתחטב', 'לרדת במשקל', 'לעלות מסה', 'לבנות שריר',\n"
                    "'לחזק את הגוף', 'להיכנס לכושר', 'לשפר סיבולת', 'להיראות טוב'.\n"
                    "אין צורך בפירוט.\n"
                    "אם יש מטרה כלשהי -> found.\n"
                    "רק אם אין בכלל מטרה -> missing.\n"
                    "value בין 1 ל-10 לפי רמת הבהירות.\n\n"

                    "budget:\n"
                    "החזר סכום מספרי בלבד.\n"
                    "אם המשתמש כתב מילים כמו 'שלוש מאות' -> המר ל-300.\n"
                    "אם יש טווח -> קח את הגבוה.\n"
                    "אם אין סכום ברור -> missing.\n\n"

                    "urgency:\n"
                    "החזר מספר 1-10 לפי כמה מהר המשתמש רוצה להתחיל.\n"
                    "10 = מיידי, 1 = רחוק.\n"
                    "דוגמאות:\n"
                    "'עכשיו', 'מייד' -> 10\n"
                    "'בשבוע הקרוב' -> 8\n"
                    "'עוד חודש' -> 5\n"
                    "'מתישהו' -> missing\n\n"

                    "====================\n"

                    "missing:\n"
                    "אם המשתמש כתב משהו לא שימושי כמו:\n"
                    "'לא יודע', 'אולי', 'נראה', 'אין לי מושג'\n"
                    "-> missing\n\n"

                    "confused:\n"
                    "החזר status='confused' רק אם ברור מהודעת המשתמש שהוא לא הבין מה צריך לענות עכשיו,\n"
                    "או לא הבין איזה סוג תשובה נדרש עבור השדה הנוכחי.\n\n"

                    "confused הוא מצב של בלבול אמיתי בלבד, לא מצב של חוסר מידע רגיל.\n"
                    "כלומר: המשתמש לא רק נמנע מלענות, אלא באמת מבקש להבין מה מבקשים ממנו עכשיו.\n\n"

                    "החזר confused במקרים כמו:\n"
                    "- המשתמש מבקש הבהרה ישירה על השאלה הנוכחית\n"
                    "- המשתמש לא מבין למה הכוונה בשאלה\n"
                    "- המשתמש לא מבין איזה סוג תשובה צריך לתת\n"
                    "- המשתמש מחזיר שאלה שמראה שהוא לא הבין מה רוצים ממנו עכשיו\n"
                    "- המשתמש מביע בלבול מפורש או עקיף לגבי המשמעות של השדה הנוכחי\n\n"

                    "דוגמאות רעיוניות ל-confused:\n"
                    "- 'מה?'\n"
                    "- 'לא הבנתי'\n"
                    "- 'למה הכוונה?'\n"
                    "- 'מה צריך לכתוב?'\n"
                    "- 'על מה אתה שואל?'\n"
                    "- 'איזה מספר?'\n"
                    "- 'מה זאת אומרת?'\n"
                    "- 'מה לרשום פה?'\n\n"

                    "אל תחזיר confused אם המשתמש רק לא נתן מידע מספיק.\n"
                    "במקרים כאלה צריך להחזיר missing.\n\n"

                    "זה missing ולא confused במקרים כמו:\n"
                    "- תשובה קצרה שלא נותנת מידע\n"
                    "- ברכה או תגובה כללית\n"
                    "- חוסר רצון לענות\n"
                    "- היסוס\n"
                    "- תשובה עמומה בלי סימן לבלבול אמיתי\n\n"

                    "דוגמאות ל-missing ולא confused:\n"
                    "- 'היי'\n"
                    "- 'כן'\n"
                    "- 'סבבה'\n"
                    "- 'לא יודע'\n"
                    "- 'אולי'\n"
                    "- 'נראה'\n"
                    "- 'אין לי מושג'\n"
                    "- 'מתישהו'\n"
                    "- 'לא בטוח'\n\n"

                    "אם יש ספק בין missing ל-confused:\n"
                    "העדף missing.\n"
                    "החזר confused רק כשבאמת אפשר להבין שהמשתמש מבקש הבהרה על השאלה עצמה,\n"
                    "ולא רק נכשל בלתת מידע.\n\n"
                    
                    "clarify:\n"
                    "- החזר clarify רק אם status הוא 'confused'\n"
                    "- clarify חייב להיות קצר מאוד: 4 עד 10 מילים בלבד\n"
                    "- המטרה של clarify היא להבהיר בדיוק מה המשתמש לא הבין\n"
                    "- clarify לא נועד לנהל שיחה\n"
                    "- clarify לא נועד להיות תגובה מלאה למשתמש\n"
                    "- clarify לא נועד להישמע כמו נציג שירות\n"
                    "- clarify לא נועד פשוט לשאול שוב את אותה שאלה\n\n"

                    "הכלל הכי חשוב:\n"
                    "clarify חייב להיות מבוסס על סוג הבלבול הספציפי של הודעת המשתמש האחרונה,\n"
                    "ולא להיות ניסוח כללי קבוע שמתאים לכל משתמש.\n\n"

                    "כלומר:\n"
                    "- אם המשתמש לא הבין מה הנושא -> clarify צריך להסביר מה מבקשים ממנו\n"
                    "- אם המשתמש לא הבין איזה סוג תשובה צריך -> clarify צריך להסביר איזה סוג תשובה נדרש\n"
                    "- אם המשתמש לא הבין מונח או כוונה -> clarify צריך לנסח מחדש בפשטות את המשמעות\n"
                    "- אם המשתמש החזיר שאלה כללית שמראה בלבול -> clarify צריך למקד אותו למה צריך לענות עכשיו\n\n"

                    "clarify צריך לתקן רק את נקודת הבלבול.\n"
                    "לא יותר.\n"
                    "לא להרחיב.\n"
                    "לא להסביר מעבר למה שצריך.\n"
                    "לא להוסיף מילים מיותרות.\n\n"

                    "חוקים ל-clarify:\n"
                    "- רק על השדה הנוכחי\n"
                    "- בלי להזכיר שדות אחרים\n"
                    "- בלי תשובה שיחתית מלאה\n"
                    "- בלי ברכה\n"
                    "- בלי מילות נימוס מיותרות\n"
                    "- בלי הסבר ארוך\n"
                    "- בלי לענות למשתמש במקום להבהיר\n"
                    "- בלי לשנות נושא\n"
                    "- בלי ניסוח גנרי שחוזר על עצמו אם אפשר לדייק לפי ההודעה\n"
                    "- בלי template קבוע של השדה, אלא אם אין שום דרך להיות יותר מדויק\n\n"

                    "clarify טוב הוא כזה שמרגיש כאילו הוא נכתב בתגובה לבלבול הספציפי של המשתמש,\n"
                    "ולא כאילו הוא נשלף מרשימה קבועה מראש.\n\n"

                    "clarify לא צריך להיות יצירתי סתם.\n"
                    "הוא צריך להיות מדויק.\n"
                    "עדיף הבהרה פשוטה וממוקדת מאשר ניסוח מתוחכם או יפה.\n\n"

                    "אל תחזור אוטומטית על ניסוחים כלליים כמו:\n"
                    "'תכתוב מה המטרה שלך'\n"
                    "'תכתוב סכום תקציב'\n"
                    "'מתי אתה רוצה להתחיל'\n"
                    "אלא אם באמת אין דרך יותר מדויקת להתאים את ההבהרה למה שהמשתמש כתב.\n\n"

                    "אם אפשר להבין מה בדיוק המשתמש לא הבין,\n"
                    "clarify חייב להתייחס דווקא לזה.\n"
                    "לא לשדה באופן כללי, אלא לנקודת הבלבול עצמה.\n\n"

                    "לפני שאתה יוצר clarify, זהה מה המשתמש לא הבין:\n"
                    "- את הנושא?\n"
                    "- את סוג התשובה?\n"
                    "- את המשמעות של המונח?\n"
                    "- את מה מבקשים ממנו לעשות עכשיו?\n"
                    "ואז כתוב הבהרה קצרה רק על זה.\n\n"

                    "clarify צריך להרגיש כמו:\n"
                    "- הבהרה ממוקדת\n"
                    "- ניסוח מחדש פשוט\n"
                    "- תיקון של בלבול\n"
                    "ולא כמו:\n"
                    "- שאלה רגילה חדשה\n"
                    "- תשובת שירות\n"
                    "- תגובה אוטומטית קבועה\n\n"

                    "חוק הכרעה חשוב:\n"
                    "אם המשתמש מבולבל לגבי המשמעות או סוג התשובה,\n"
                    "clarify צריך להסביר את הדבר שלא הובן.\n"
                    "אם המשתמש פשוט לא סיפק מידע,\n"
                    "אל תחזיר clarify בכלל.\n\n"

                    "אל תשתמש ב-clarify כדרך לשאול שוב.\n"
                    "השתמש בו רק כדי להבהיר.\n\n"
                    
                    "ack:\n"
                    "- רק אם status הוא found\n"
                    "- 1 עד 3 מילים בלבד\n"
                    "- בלי שאלה\n"
                    "- בלי הסבר\n"
                    "- בלי לחזור על תשובת המשתמש\n"
                    "- טבעי וקצר\n"
                    "- אפשר לגוון בין ניסוחים קצרים שונים\n"
                    "- דוגמאות: 'מעולה', 'סבבה', 'הבנתי', 'סגור', 'אחלה'\n"
                    "- אל תחזיר תמיד את אותו ack אם אין צורך\n\n"

                    "חוקים אחרונים:\n"
                    "- החזר JSON בלבד\n"
                    "- ללא טקסט נוסף\n"
                )
            },
            {
                "role": "user",
                "content": content
            }
        ]
    

    def analyze_prompt(self, current_field, content):
        return [
            {
                "role": "system",
                "content": (
                    "אתה חלק ממערכת סינון לידים של מאמן כושר.\n"
                    "המערכת שואלת את המשתמש כל פעם שאלה אחת בלבד.\n"
                    "כל שאלה שייכת לשדה אחד בלבד: goal, budget, urgency.\n\n"

                    "התפקיד שלך:\n"
                    "לנתח רק את תשובת המשתמש האחרונה ולבדוק אם היא מתאימה לשדה הנוכחי.\n"
                    "כל ההחלטה שלך חייבת להתבסס רק על השדה הנוכחי: " + current_field + "\n\n"

                    "חשוב מאוד:\n"
                    "- אסור לעבור לשדה אחר כי כל שדה הוא שלב נפרד בתהליך\n"
                    "- אסור לשנות נושא כי זה שובר את הלוגיקה של הסינון\n"
                    "- אסור להזכיר שדות אחרים כדי לא לבלבל את המשתמש ואת המערכת\n\n"

                    "====================\n"

                    "החזר JSON בלבד באחד מהמצבים:\n\n"

                    "====================\n"

                    "FOUND:\n"
                    "{"
                    "\"status\":\"found\","
                    "\"value\":NUMBER,"
                    "\"ack\":\"TEXT\""
                    "}\n\n"

                    "FOUND אומר שהמשתמש נתן מידע אמיתי וברור שאפשר להפוך לערך מספרי.\n"
                    "זה המצב הכי חשוב במערכת כי כאן אפשר להפיק נתון אמיתי מהשיחה.\n"
                    "value הוא הערך שחולץ מהתשובה והוא חייב להיות מספר כדי לאפשר עיבוד אחיד של כל הנתונים.\n"
                    "למשל תקציב או דחיפות תמיד מומר למספר כדי לשמור על אחידות.\n\n"

                    "value הוא הנתון שחולץ מהתשובה לפי השדה הנוכחי:\n\n"

                    "אם current_field הוא goal:\n"
                    "- value הוא רמת בהירות של המטרה בין 1 ל-10\n"
                    "- זה לא מספר מהמשתמש אלא דירוג כמה המטרה ברורה\n"
                    "- 1 = מאוד כללי ולא ברור\n"
                    "- 10 = מטרה ברורה מאוד עם יעד מוגדר\n\n"

                    "אם current_field הוא budget:\n"
                    "- value הוא סכום כסף מספרי בלבד\n"
                    "- מילים (שלוש מאות) -> 300\n"
                    "- טווחים (200-300) -> לוקחים את הגבוה (300)\n"
                    "- הערכה כללית -> מספר הכי קרוב למה שנאמר\n"
                    "- אם אין מספר שניתן להבין ממנו סכום -> לא מגיע ל-found\n\n"

                    "אם current_field הוא urgency:\n"
                    "- value הוא רמת דחיפות בין 1 ל-10\n"
                    "- 10 = מיידי / 1 = רחוק מאוד\n"
                    "- עכשיו / מיד -> 10\n"
                    "- השבוע הקרוב -> 8-9\n"
                    "- חודש -> 5\n"
                    "- מתישהו -> 2-4\n\n"
                    
                    "ack ב-FOUND הוא תגובה קצרה מאוד אחרי חילוץ מידע.\n"
                    "המטרה שלו היא לשמור על שיחה טבעית ולא טכנית.\n"
                    "הוא לא מסביר, לא מנתח, ולא חוזר על מה שהמשתמש אמר.\n"
                    "הוא רק מאשר בצורה קצרה שהמידע נקלט.\n\n"

                    "value הוא הנתון שחולץ מהתשובה לפי השדה הנוכחי:\n\n"


                    "====================\n"

                    "MISSING:\n"
                    "{"
                    "\"status\":\"missing\","
                    "\"type\":\"no_info|vague|avoid\""
                    "}\n\n"

                    "MISSING אומר שלא הצלחנו לקבל מידע שימושי לשדה הנוכחי.\n"
                    "זה לא אומר שהמשתמש טעה, אלא שפשוט אין נתון שאפשר לעבוד איתו.\n"
                    "המטרה כאן היא להבין שצריך לשאול שוב בצורה אחרת ולא להמשיך לחלץ מידע בכוח.\n\n"

                    "סוגי missing:\n"
                    "- no_info: המשתמש לא נתן בכלל מידע שקשור לשדה הנוכחי\n"
                    "- vague: המשתמש נתן תשובה כללית מדי שלא מאפשרת לחלץ ערך מספרי ברור\n"
                    "- avoid: המשתמש מתחמק מהשאלה, משנה נושא או לא עונה ישירות לשאלה\n\n"

                    "מטרת missing היא לשמור על דיוק ולא לפרש מידע שלא קיים.\n"
                    "זה מצב של חוסר נתונים בלבד, לא בלבול.\n\n"

                    "====================\n"

                    "CONFUSED:\n"
                    "{"
                    "\"status\":\"confused\","
                    "\"type\":\"meaning|answer_type|focus\","
                    "\"ack\":\"TEXT\""
                    "}\n\n"

                    "CONFUSED אומר שהמשתמש לא הבין מה רוצים ממנו בשאלה הנוכחית.\n"
                    "זה מצב שונה מ-missing כי כאן הבעיה היא הבנה ולא חוסר מידע.\n"
                    "המשתמש כן מגיב, אבל לא מבין מה צריך לענות או מה המשמעות של השאלה.\n\n"

                    "סוגי confused:\n"
                    "- meaning: המשתמש לא מבין מה השדה או מה השאלה מנסה להשיג בכלל\n"
                    "- answer_type: המשתמש לא מבין איזה סוג תשובה צריך לתת (מספר, מטרה, זמן וכו')\n"
                    "- focus: המשתמש לא מבין על מה הוא אמור להתמקד עכשיו או יוצא מהנושא\n\n"

                    "CONFUSED חשוב כי הוא אומר שהבעיה היא בהבנה ולא בתוכן.\n"
                    "במצב כזה לא מחפשים מידע אלא מסבירים מחדש בצורה פשוטה יותר.\n\n"

                    "ack בתוך CONFUSED שונה מ-FOUND.\n"
                    "ב-FOUND זה אישור על מידע שהתקבל.\n"
                    "ב-CONFUSED זה לא אישור מידע אלא תגובה קצרה שמטרתה להרגיע ולהחזיר את המשתמש להבנה.\n"
                    "לכן הוא חייב להיות מותאם לסוג הבלבול ולא גנרי.\n\n"

                    "דוגמאות לכיוון ack ב-confused:\n"
                    "- meaning: תגובה שמבהירה שמדובר בשאלה עצמה\n"
                    "- answer_type: תגובה שמסבירה מה צריך לכתוב\n"
                    "- focus: תגובה שמחזירה את המשתמש לנושא הנוכחי\n\n"

                    "====================\n"

                    "RULE חשוב מאוד:\n"
                    "אם יש ספק בין missing ל-confused -> תמיד לבחור missing\n"
                    "כי עדיף לא להניח בלבול אם אין ודאות ברורה.\n\n"

                    "====================\n"

                    "חוקים אחרונים:\n"
                    "- החזר JSON בלבד\n"
                    "- ללא טקסט נוסף\n"
                )
            },
            {
                "role": "user",
                "content": content
            }
        ]
    
   




class OpenAIClient:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    
    def ai_reply(self, messages):
        res = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
            max_completion_tokens=80,
            response_format={"type": "json_object"}
        )

        text = res.choices[0].message.content
        #print("RAW:", text)

        data = json.loads(text)

        # validation קצר
        if "status" not in data:
            raise ValueError("AI returned invaild JSON structure")

        if not ("ack" in data or "clarify" or "value"):
            raise ValueError("AI returned invaild JSON structure")

        return data




class MessageScorer:
    def __init__(self):
        pass
    
    
    def score_message(self , message_to_rank , field):
        rank_score = 0

        if message_to_rank["status"] == "found":
            if field == "budget":
                if float(message_to_rank["value"]) >= 450:
                    rank_score += 3
                elif 250 <= float(message_to_rank["value"]) <= 449:
                    rank_score += 2
                else:
                    rank_score += 1

            
            
            elif field == "goal":
                if 8 <= float(message_to_rank["value"]) <= 10:
                    rank_score += 3
                elif 5 <= float(message_to_rank["value"]) <= 7:
                    rank_score += 2
                else:
                    rank_score += 1
            
            
            elif field == "urgency":
                if 8 <= float(message_to_rank["value"]) <= 10:
                    rank_score += 3
                elif 5 <= float(message_to_rank["value"])  <= 7:
                    rank_score += 2
                else:
                    rank_score += 1
            

        
            return {"status" : "found" , "rank_score" : rank_score}
        
        return {"status" : "missing" , "rank_score" : rank_score}
    



    def score_follow_up_message(self , follow_up_rank):
        if follow_up_rank["lead_signal"] == "strong":
            return {"status" : "completed process" , "final" : "hot lead"}
        
        elif follow_up_rank["lead_signal"] == "cold":
            return {"status" : "completed process" , "final" : "cold lead"}
        
        else:
            return {"status" : "ongoing process" , "final" : "none"}

    

class LeadScoreManager:
    def __init__(self):
        pass

    
    
    def update_lead_score_info(self , lead_score_info , lead_message_score , message_field):
        if lead_message_score > 0:
            lead_score_info["score_count"] += 1
            lead_score_info["total_score"] += lead_message_score
            lead_score_info[message_field] = lead_message_score
        
        return lead_score_info
  
    

class LeadClassifier:
    def __init__(self):
        pass

    
    
    def classify_lead_score(self , lead_score_info):
        print(lead_score_info)
        
        if lead_score_info["score_count"] < 3:
            return None
        
        elif lead_score_info["total_score"] >= 8:
            return "Hot Lead"
        
        elif lead_score_info["total_score"] >= 7:
            if lead_score_info["budget_score"] >= 2 and lead_score_info["urgency_score"] >= 2:
                return "Hot Lead"
            else:
                return "Cold Lead"
        
        else:
            return "Cold Lead"
        
            








class ServiceLayer:
    def __init__(self , conversation_builder , open_ai_client , data_access , message_scorer , lead_score_manager , lead_classifier , questions):
        self.conversation_builder = conversation_builder
        self.open_ai_client = open_ai_client
        self.data_access = data_access
        self.message_scorer = message_scorer
        self.lead_score_manager = lead_score_manager
        self.lead_classifier = lead_classifier
        self.questions = questions


        
        
        if conversation_builder is None:
            raise ValueError(f"Conversation Builder cannot be None")

        
        if open_ai_client is None:
            raise ValueError(f"OpenAI Client cannot be None")
    
        
        if data_access is None:
            raise ValueError(f"Data Access cannot be None")
        
        
        if message_scorer is None:
            raise ValueError(f"Message Scorer cannot be None")
        

        if lead_score_manager is None:
            raise ValueError(f"Lead Score Manager cannot be None")
        

        if lead_classifier is None:
            raise ValueError(f"Lead Classifier cannot be None")
    


    
    def process_lead_message(self , phone_number , content=None , name=None , mode=1):
        validate_str(phone_number , "phone_number")        
        
        get_or_create_lead = self.lead_exists_check(phone_number=phone_number)
        if get_or_create_lead is None:
            if mode == 1:
                return {"status" : "new"}
            else:
                validate_str(name , "name")
                get_or_create_lead = self.lead_exists_check(phone_number=phone_number , lead_name=name , new=True)
        
        if get_or_create_lead is not None and mode == 1:
            #print("here")
            return {"status" : "exist"}

        validate_str(content , "content")

        lead_id = get_or_create_lead["lead_id"]
        
        ensure_lead_tables = self.ensure_user_tables_exist(lead_id)
        
        lead_base_data = self.build_base_lead_data(base_data=get_or_create_lead)
        lead_scores_data = self.build_lead_scores_data(scores_data=ensure_lead_tables["lead_scores_data"])
        lead_fields_data = self.build_lead_fields_data(fields_data=ensure_lead_tables["lead_fields_data"])
        
        current_field = lead_base_data["current_field"]
        total_score = lead_scores_data["total_score"]
                
        
        ai_response = self.generate_analyze(lead_id=lead_id , content=content , current_field=current_field)
        
        
        self.apply_ai_result(ai_response=ai_response , lead_info=lead_base_data , content=content)

        self.apply_message_score(lead_info=lead_scores_data , current_field=current_field , ai_analyze_response=ai_response)
        

        finalize_lead_status = self.finalize_lead_status(lead_scores_data)
        if finalize_lead_status is not None:
            final_lead_status = finalize_lead_status["final_status"]

            if final_lead_status == "Hot Lead":
                summary_data = self.build_summary_data(base_data=lead_base_data , fields_data=lead_fields_data , total_score=total_score)
                self.process_lead_summary(summary_data)
        


        generate_ai_question = self.generate_question(lead_info=lead_base_data , ai_response=ai_response)
        if generate_ai_question is None:
            return {"status" : "DONE"}
        
        elif generate_ai_question["status"] == "invaild answer":
            get_or_create_lead = self.lead_exists_check(phone_number=phone_number)
            lead_base_data = self.build_base_lead_data(base_data=get_or_create_lead)
            print(lead_base_data["attempt_number"])
            print("good")
            question = self.build_next_response(lead_info=lead_base_data)
            
        elif generate_ai_question["status"] == "confused":
            question = generate_ai_question["question"]
        
        elif generate_ai_question["status"] == "valid answer":
            get_or_create_lead = self.lead_exists_check(phone_number=phone_number)
            lead_base_data = self.build_base_lead_data(base_data=get_or_create_lead)
            print(lead_base_data["attempt_number"])
            print("bad")
            question = self.build_next_response(lead_info=lead_base_data , ai_response=generate_ai_question["ai_response"] , mode="follow up")
        
        return {"status" : "in process" , "question" : question}

    

    
    def lead_exists_check(self , phone_number , lead_name=None , new=False):
        validate_str(phone_number , "phone number")

        if not new:
            lead_info_exist_check = self.data_access.get_lead_base_info(phone_number)
            if lead_info_exist_check is None:
                return
            else:
                return lead_info_exist_check
            
        if new:
            lead_info_exist_check = self.data_access.get_lead_base_info(phone_number)
            if lead_info_exist_check is None:
                validate_str(lead_name , "lead name")
                
                self.data_access.create_new_lead(phone_number=phone_number , name=lead_name)
                lead_info_exist_check = self.data_access.get_lead_base_info(phone_number)
            
            return lead_info_exist_check
        

    
    
    def ensure_user_tables_exist(self , lead_id):
        validate_int(lead_id , "lead id")

        lead_score_exist_check = self.data_access.get_lead_score_info(lead_id=lead_id)
        if lead_score_exist_check is None:
            self.data_access.create_new_lead_score(lead_id=lead_id)
            lead_score_exist_check = self.data_access.get_lead_score_info(lead_id=lead_id)
        
        
        lead_fields_data_check = self.data_access.get_all_lead_field_data(lead_id=lead_id)
        if lead_fields_data_check is None:
            self.data_access.create_new_fields_data(lead_id=lead_id)
            lead_fields_data_check = self.data_access.get_all_lead_field_data(lead_id=lead_id)

        
        return {
            "lead_scores_data" : lead_score_exist_check , 
            "lead_fields_data" : lead_fields_data_check
        }
    

    

    def build_base_lead_data(self , base_data):
        return {
            "phone_number" : base_data["phone_number"] , 
            "lead_id" : base_data["lead_id"] ,
            "name" : base_data["name"] , 
            "current_field" : base_data["current_field"] , 
            "attempt_number" : base_data["attempt_number"] , 
            "status" : base_data["status"] , 
            "summary" : base_data["summary"] 
            }
    

    def build_lead_scores_data(self , scores_data):
        return {
                "lead_id" : scores_data["lead_id"] ,
                "total_score" : scores_data["total_score"] , 
                "score_count" : scores_data["score_count"] ,
                "goal_score" : scores_data["goal_score"] , 
                "budget_score" : scores_data["budget_score"] ,
                "urgency_score" : scores_data["urgency_score"]
            }
    

    
    def build_lead_fields_data(self , fields_data):
        return {
        "lead_id" : fields_data["lead_id"] , 
        "goal_user" : fields_data["goal_user"] ,
        "budget_user" : fields_data["budget_user"] ,
        "urgency_user" : fields_data["urgency_user"]
    }


    
    def build_summary_data(self , base_data , fields_data , total_score):
        return {
            "phone_number" : base_data["phone_number"] , 
            "lead_id" : base_data["lead_id"] ,
            "name" : base_data["name"] , 
            "goal_user" : fields_data["goal_user"] , 
            "budget_user" : fields_data["budget_user"] ,
            "urgency_user" : fields_data["urgency_user"] ,
            "total_score" : total_score["total_score"] ,
        }
        




    def generate_analyze(self , lead_id , current_field , content):
        ai_input = self.conversation_builder.analyze_prompt(current_field=current_field , content=content)
        ai_response = self.open_ai_client.ai_reply(ai_input)
        
        self.data_access.add_lead_message(lead_id=lead_id , role="user" , content=content)
        
        print(ai_response)
        return ai_response

    
    
    def generate_question(self , lead_info , ai_response=None):
        validate_str(content , "content")


        if lead_info["status"] != "pending":
            return {"status" : "DONE"}
        
        #print(lead_info["current_field"])
        #print(lead_info["attempt_number"])

        
        if ai_response is None:
            question = self.questions.process_questions(mode=lead_info["current_field"] , attempt_number=lead_info["attempt_number"])
        
        elif ai_response["status"] == "missing":
            return {"status" : "invaild answer"}
        
        elif ai_response["status"] == "found":
            return {"status" : "valid answer" , "ai_response" : ai_response}
    

        elif ai_response["status"] == "confused":
            question = ai_response["clarify"]
            return {"status" : "confused" , "question" : question}
        
        self.data_access.add_lead_message(lead_id=lead_info["lead_id"] , role="bot" , content=question)

        



    def build_next_response(self , lead_info , ai_response=None , mode="regular"):
        if mode == "regular":
            return self.questions.process_questions(mode=lead_info["current_field"] , attempt_number=lead_info["attempt_number"])
        
        elif mode == "follow up":
            separators = [
            ". ",
            ", ",
            " - ",
            " — ",
            " "
            ]
            sep = random.choice(separators)

            build_question = self.questions.process_questions(mode=lead_info["current_field"] , attempt_number=lead_info["attempt_number"])
            return f"{ai_response['ack']}{sep} {build_question}"


    
    def apply_ai_result(self , ai_response , lead_info , content):
        if ai_response["status"] == "found":
            if lead_info["current_field"] == "goal":
                lead_info["current_field"] = "budget"
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="goal_user" , value=content)

            elif lead_info["current_field"] == "budget":
                lead_info["current_field"] = "urgency"
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="budget_user" , value=content)

            elif lead_info["current_field"] == "urgency":
                lead_info["current_field"] = None
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="urgency_user" , value=content)
            
            
            self.data_access.update_lead_current_field(lead_info["lead_id"] , updated_field=lead_info["current_field"])
            self.data_access.update_lead_attempt_number(lead_id=lead_info["lead_id"] , number=1)

    
        if ai_response["status"] == "missing":
            self.data_access.update_lead_attempt_number(lead_id=lead_info["lead_id"] , number=lead_info["attempt_number"] + 1)


    
    
    def apply_message_score(self , lead_info , current_field , ai_analyze_response):
        #print("here")
        lead_message_score = self.message_scorer.score_message(message_to_rank=ai_analyze_response , field=current_field)
        
        if lead_message_score["status"] == "missing":
            return

        self.lead_score_manager.update_lead_score_info(lead_score_info=lead_info , lead_message_score=lead_message_score["rank_score"] , message_field=f"{current_field}_score")
        self.data_access.update_lead_score_info(lead_id=lead_info["lead_id"] , score_count=lead_info["score_count"] , total_score=lead_info["total_score"] , score_field=f"{current_field}_score" , value=lead_message_score["rank_score"])


    
    def finalize_lead_status(self , lead_info):
        #print("here")
        if lead_info["score_count"] == 3:
            final_lead_status = self.lead_classifier.classify_lead_score(lead_info)
            
            if final_lead_status:
                self.data_access.set_lead_status(lead_info["lead_id"] , final_lead_status)
                return {"final_status" : final_lead_status}
            
        return 


    
    def process_lead_summary(self , summary_info):
        summary_info["budget_user"] = self.format_currency(summary_info=["budget_user"])

        final_summary = self.generate_lead_summary(summary_info)

        self.upload_lead_summary(summary=final_summary , lead_id=summary_info["lead_id"])

    
    
    def format_currency(self , budget_text):
        currency_symbols = ["₪", "שקל", "שח", 'ש"ח' , "שקלים"]

        if not any(symbol in budget_text for symbol in currency_symbols):
            budget_text = budget_text.strip() + " ₪"

        return budget_text



    def generate_lead_summary(self , summary_info):
        text = (
            f"🔥 ליד חם חדש:\n\n"
            f"{summary_info['name']} פנה לגבי אימונים.\n\n"
            f"מטרה: {summary_info['goal_user']}\n"
            f"תקציב: {summary_info['budget_user']} לחודש\n"
            f"זמן התחלה: {summary_info['urgency_user']}\n\n"
            f"ציון התאמה: {summary_info['total_score']}\n"
            f"טלפון: {summary_info['phone_number']}"
            )
        
        return text
    

    
    def upload_lead_summary(self , summary , lead_id):
        self.data_access.upload_summary(lead_summary=summary , lead_id=lead_id)
        




 




data_access = DataAccess()
conversation_builder = ConversationBuilder()
openai_client = OpenAIClient(ai_key)
message_scorer = MessageScorer()
lead_score_manager = LeadScoreManager()
lead_classifier = LeadClassifier()
questions = Questions()

service_layer = ServiceLayer(data_access=data_access , conversation_builder=conversation_builder , open_ai_client=openai_client , message_scorer=message_scorer , lead_score_manager=lead_score_manager , lead_classifier=lead_classifier , questions=questions)


data_access.create_leads_info_table()
data_access.create_leads_scores_table()
data_access.create_leads_messages_table()
data_access.create_leads_fields_data()



phone_number = None
new_lead = False
welcome_message = False

while True:
    #try:
    print("""
        =================================
                LEAD FILTER ENGINE
        =================================

            Analyze • Score • Classify
        """)
    
    
    system_choice = input("Please tap enter to procceed or type exit to close the system: ")
    if system_choice.lower() == "exit":
        break

    
    if phone_number is None:
        phone_number = input("כדי להתחיל או להמשיך מאיפה שעצרת, מה המספר שלך: ")


    message_process = service_layer.process_lead_message(phone_number=phone_number)
    print("did")
    if message_process["status"] == "new":
        lead_name = input("Please enter your name: ")
        validate_str(lead_name , "name")

        content = input("Please enter your message: ")
        validate_str(content , "content")
        
        message_process = service_layer.process_lead_message(phone_number=phone_number , content=content , name=lead_name , mode=2)
        

    #print(message_process)
    #print("here")
    if message_process["status"] == "exist":
        content = input("Please enter your message: ")
        validate_str(content , "content")
        message_process = service_layer.process_lead_message(phone_number=phone_number , content=content , mode=2)
    
    
    if message_process["status"] == "DONE":
        print(f"Thank you for your cooperation. We will contact you soon")
        break

    if message_process["status"] == "in process":
        raw_message = message_process["question"]
        print(get_display(raw_message))
        

    

    #except Exception as e:
        #print(f"Error: {e}")
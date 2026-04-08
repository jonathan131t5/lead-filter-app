import requests
from openai import OpenAI 
from dotenv import load_dotenv
import os
import json
import sqlite3
from bidi.algorithm import get_display
import time

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
        
    
   


class ConversationBuilder:
    def __init__(self):
        pass

    
    def build_regular_system_prompt(self , name , current_field , attempt , question_type):
        return [{
            "role": "system",
            "content": (
                f"אתה נציג מכירות בחדר כושר.\n"
                f"אתה מדבר עם לקוח בשם {name}.\n"
                f"נושא: {current_field}. ניסיון: {attempt}. סוג תגובה: {question_type}.\n\n"

                f"המשימה:\n"
                f"החזר רק הודעה אחת, טבעית, קצרה, עד 16 מילים, ורק על current_field.\n"
                f"התייחס תמיד להודעת ה-user האחרונה כהודעה הנוכחית של המשתמש.\n\n"

                f"פירוש סוג התגובה (question_type):\n"
                f"- info = המשתמש ניסה לענות על השאלה (גם אם התשובה לא טובה או חסרה).\n"
                f"- confused = המשתמש לא הבין, מבולבל, או שואל למה הכוונה.\n\n"

                f"חוק מרכזי:\n"
                f"- אם question_type הוא info -> שאל רק שאלה קצרה על current_field לפי attempt, בלי להגיב לתוכן לא קשור.\n"
                f"- אם question_type הוא confused -> הבהר בקצרה ובצורה טבעית למה אתה מתכוון, כמו שיחה רגילה, ואז שאל שוב על current_field.\n"                f"- בכל מצב, אסור לסטות מהנושא.\n\n"

                f"התנהגות:\n"
                f"- אם הודעת המשתמש רלוונטית וברורה, מותר להשתמש בה רק כדי לנסח שאלה טבעית יותר.\n"
                f"- אם הודעת המשתמש לא קשורה, מוזרה, שטותית, סלנג, בדיחה, או לא נותנת מידע שימושי — התעלם ממנה לחלוטין.\n"
                f"- במקרה כזה, פשוט שאל שוב רק על current_field.\n\n"

                f"חוקים קריטיים:\n"
                f"- אסור לשאול על נושא אחר.\n"
                f"- אסור להציע אפשרויות, רעיונות או פתרונות (גם לא בהבהרה).\n"
                f"- אסור להגיב חברתית להודעת המשתמש. אסור לומר שלום, מה שלומך, תודה, או תגובה חופשית אחרת.\n"
                f"- גם במצב confused, ההבהרה חייבת להיות ניטרלית בלבד ולא להכווין תשובה.\n"
                f"- אסור להסביר מעבר להבהרה קצרה כש-question_type הוא confused.\n"
                f"- אסור לחזור בדיוק על אותה שאלה.\n"
                f"- אם המשתמש לא ברור אבל ניסה לענות -> שאל שוב לפי attempt.\n"
                f"- במצב confused, אסור להשתמש במילים רשמיות או רובוטיות כמו 'הבהרה', 'הכוונה היא', או ניסוחים מערכתיים.\n"
                f"- אם המשתמש מבולבל -> אל תשאל על הבלבול עצמו. פשוט הבהר בקצרה למה אתה מתכוון בשדה הנוכחי, ואז שאל שוב.\n" 
                f"- אם הודעת המשתמש לא קשורה ל-current_field ואינה בקשת הבהרה אמיתית, אל תשלב את התוכן שלה בתגובה.\n"
                f"- במקרה כזה, פשוט שאל שוב בצורה טבעית על current_field.\n"
                f"- אל תחזור על מילים מוזרות, סלנג, בדיחות או תוכן לא קשור מהודעת המשתמש.\n\n"               
                
                f"תחילת שיחה:\n"
                f"- אם user_message הוא 'none', שאל שאלה ראשונה קצרה וטבעית רק על current_field.\n\n"

                f"חוקי behavior לפי field + attempt:\n\n"

                f"goal:\n"
                f"- תמיד שאלה פתוחה.\n"
                f"- attempt=1 -> שאלה כללית.\n"
                f"- attempt=2 -> שאלה ממוקדת קצרה.\n"
                f"- attempt>=3 -> שאלה ישירה שמבקשת פירוט.\n\n"

                f"budget:\n"
                f"- attempt=1 -> שאלה כללית על תקציב.\n"
                f"- attempt=2 -> בקש סכום או טווח.\n"
                f"- attempt>=3 -> בקש מספר ברור.\n\n"

                f"urgency:\n"
                f"- attempt=1 -> שאלה כללית על התחלה.\n"
                f"- attempt=2 -> שאל כמה מהר רוצה להתחיל.\n"
                f"- attempt>=3 -> נסה לקבל זמן יותר מדויק, אבל רק בצורה טבעית ולא נוקשה.\n\n"

                f"החזר רק את ההודעה עצמה. בלי הסברים ובלי טקסט נוסף."
            )
        }]
            

    

    def build_input(self , name , current_field , content ,  attempt , question_type):
        ai_content = []
        ai_content.extend(self.build_regular_system_prompt(name=name , current_field=current_field , attempt=attempt , question_type=question_type))
        
        ai_content.append({
            "role" : "user" , 
            "content" : content
        })
        
        return ai_content
    


    

    
    
    def analyze_prompt(self, current_field , content):
        return [
            {
                "role": "system",
                "content": (
                    "אתה ממיר את תשובת המשתמש לערך מספרי אחד בלבד עבור השדה הנוכחי.\n"
                    "בנוסף, עליך לזהות את סוג התגובה של המשתמש.\n\n"

                    "מצב מיוחד:\n"
                    "- אם User message הוא 'none' -> זו תחילת שיחה\n"
                    "- במצב כזה אסור לנתח או לדרג\n"
                    "- החזר תמיד:\n"
                    "{\"message\":\"THERE IS NO INFO\",\"result_type\":\"info\"}\n\n"
                    
                    
                    "סוגי תגובה (result_type):\n"
                    "- info = המשתמש ניסה לענות על השאלה או כתב משהו שאינו בקשת הבהרה\n"
                    "- confused = המשתמש מבולבל, לא הבין, או שואל על משמעות השאלה\n\n"

                    "חוקים לזיהוי:\n"
                    "- אם המשתמש מבקש הבהרה אמיתית על השאלה (למשל: 'לא הבנתי', 'למה הכוונה', 'מה זאת אומרת') → result_type = confused\n"
                    "- אם ההודעה אינה תשובה לשדה הנוכחי וגם אינה בקשת הבהרה אמיתית → result_type = info\n"
                    "- שטויות, בדיחות, סלנג, או תוכן לא קשור תמיד נחשבים info ולא confused\n\n"

                    "אם המשתמש אומר דברים כמו אלו ועוד:\n"
                    "'לא הבנתי', 'מה?', 'למה אתה מתכוון', 'על מה אתה מדבר'\n"
                    "→ result_type = confused\n\n"

                    "בכל מקרה אחר → result_type = info\n\n"

                    "חשוב:\n"
                    "result_type = info לא אומר שיש מידע תקין.\n"
                    "יכול להיות result_type = info ובאותו זמן:\n"
                    "{\"message\":\"THERE IS NO INFO\",\"result_type\":\"info\"}\n\n"

                    "המשתמש יכול לענות במספרים או בשפה טבעית בעברית.\n"
                    "נתח רק את השדה הנוכחי.\n\n"

                    "אם אין מידע ברור ורלוונטי לשדה הנוכחי, או שלא ניתן להמיר את ההודעה לערך אחד בביטחון סביר, החזר:\n"
                    "{\"message\":\"THERE IS NO INFO\",\"result_type\":\"TYPE\"}\n"
                    "TYPE חייב להיות info או confused.\n\n"

                    "החזר JSON בלבד.\n\n"

                    "חוקי השדות:\n"
                    "goal -> החזר מספר אחד בין 1 ל-10 לפי כמה המטרה ברורה, ספציפית ורצינית.\n"
                    "budget -> החזר מספר רק אם המשתמש נתן סכום ברור או טווח ברור. אם זה טווח, החזר את המספר הגבוה. אם אין סכום ברור, החזר THERE IS NO INFO. אסור לנחש ואסור להמציא מספר.\n"
                    "urgency -> החזר מספר אחד בין 1 ל-10 לפי כמה מהר המשתמש רוצה להתחיל.\n\n"

                    "מדריך urgency:\n"
                    "10 = עכשיו, מייד, בהקדם האפשרי\n"
                    "9 = היום, השבוע\n"
                    "8 = שבוע הבא, ממש בקרוב\n"
                    "7 = בתוך 2-3 שבועות\n"
                    "6 = חודש הבא\n"
                    "5 = בתוך חודש-חודשיים\n"
                    "4 = בעוד כמה חודשים\n"
                    "3 = בהמשך, אין לחץ\n"
                    "2 = דחיפות נמוכה\n"
                    "1 = לא דחוף, רק בודק\n\n"
                    
                    "הערה חשובה:\n"
                    "גם אם המשתמש משתמש בניסוח אחר, עלייך להבין את הכוונה ולהמיר אותה לרמת הדחיפות המתאימה.\n"
                    "אל תסתמך רק על המילים המדויקות במדריך\n\n"

                    "מדריך goal:\n"
                    "חוק סף:\n"
                    "אם המשתמש לא נתן שום התייחסות למטרה, או שההודעה לא קשורה בכלל למטרה כושרית, אסור להחזיר מספר.\n"
                    
                    "אם המשתמש כן התייחס למטרה אבל אמר שאין לו מטרה ברורה, לא יודע, לא בטוח, או שאין משהו ספציפי — זה עדיין נחשב מידע תקין לשדה goal ויש להחזיר 1.\n\n"
                    
                    "במקרה כזה החזר:\n"
                    "{\"message\":\"THERE IS NO INFO\",\"result_type\":\"TYPE\"}\n\n"
                    "10 = מטרה מאוד ברורה, ספציפית ורצינית\n"
                    "8-9 = מטרה ברורה עם כיוון טוב\n"
                    "6-7 = מטרה כללית אבל מובנת\n"
                    "4-5 = מטרה מעורפלת\n"
                    "2-3 = מטרה חלשה ולא ברורה\n"
                    "1 = המשתמש התייחס למטרה אבל אין לו מטרה ברורה, הוא לא יודע, לא בטוח, או שהמטרה הכושרית שלו חלשה מאוד, כללית מאוד, או ברמת רצינות נמוכה\n\n"

                    

                    "אם יש מידע תקין, החזר בדיוק בפורמט הזה:\n"
                    "{\"extracted_field\":\"CURRENT_FIELD\",\"extracted_data\":VALUE,\"result_type\":\"TYPE\"}\n"
                    "CURRENT_FIELD חייב להיות שם השדה הנוכחי.\n"
                    "VALUE חייב להיות מספר בלבד.\n"
                    "TYPE חייב להיות info או confused.\n\n"

                    "אל תחזיר שום טקסט נוסף."
                )
            },
            {
                "role": "user",
                "content": f"Current field: {current_field}\nUser message: {content}"
            }
        ]


    def main_prompt(self , current_field , attempt_number , name , content):
        return [
            {
                "role": "system",
                "content": (
                    "אתה נציג שירות של מאמן כושר אישי.\n"
                    "אתה מדבר עם לקוח אמיתי, ותמיד מתייחס להודעה האחרונה שלו כדי לענות בצורה טבעית.\n\n"

                    "המטרה שלך בכל תשובה:\n"
                    "1. לבדוק אם המשתמש נתן מידע תקין על השדה הנוכחי\n"
                    "2. להחזיר תגובה קצרה וטבעית להמשך השיחה\n\n"

                    "החזר JSON בלבד באחד משני הפורמטים:\n"
                    "אם יש מידע:\n"
                    "{\"extracted_field\":\"goal/budget/urgency\",\"extracted_data\":NUMBER,\"response\":\"TEXT\"}\n"
                    "אם אין מידע:\n"
                    "{\"message\":\"THERE IS NO INFO\",\"response\":\"TEXT\"}\n\n"

                    f"שדה נוכחי: {current_field} | ניסיון: {attempt_number} | שם: {name}\n\n"

                    "- איך לחשוב (שלב פנימי):\n"
                    "- valid = יש מידע ברור ורלוונטי לשדה הנוכחי שניתן להמיר למספר אחד.\n"
                    "- invalid = המשתמש ניסה לענות, אבל לא נתן מידע מספיק, ברור או תקין.\n"
                    "- confused = המשתמש לא הבין את השאלה או מבקש הבהרה אמיתית עליה.\n"
                    "- סלנג, בדיחות, צחוקים, ציניות, קללות או ניסוחים לא רציניים אינם confused אלא invalid,\n"
                    "  אלא אם המשתמש באמת מבקש הבהרה על השאלה.\n"
                    "- אם ההודעה כוללת גם שטויות וגם מידע ברור על השדה הנוכחי, התעלם מהשטויות וחלץ רק את המידע הברור.\n"
                    "- אם יש ספק אם המידע ברור מספיק להמרה למספר אחד, החזר THERE IS NO INFO.\n\n"

                    "זיהוי confused:\n"
                    "אם המשתמש מביע חוסר הבנה או מבקש הבהרה על השאלה — זה confused.\n"
                    "דוגמאות: 'לא הבנתי', 'מה?', 'למה אתה מתכוון', 'על מה אתה מדבר'\n"
                    "גם אם הניסוח שונה אבל המשמעות זהה (בלבול או בקשת הבהרה) — זה confused.\n\n"

                    "חוקים:\n"
                    "- אם אין ביטחון גבוה במידע → אין מידע\n"
                    "- אסור לנחש מספרים\n"
                    "- אסור להמציא מידע\n"
                    "- אם ההודעה לא קשורה → התעלם ושאל שוב\n\n"

                    "איך לבנות response:\n"
                    "- valid → המשך שיחה טבעי (לרוב השדה הבא)\n"
                    "- invalid → שאל שוב לפי attempt\n"
                    "- confused → הבהר בקצרה בטבעיות ואז שאל שוב\n"
                    "- תמיד להתבסס על הודעת המשתמש לניסוח טבעי\n\n"

                    "חוקי שדות:\n"
                    "budget → רק סכום ברור או טווח (קח גבוה). התקציב יכול להינתן במספרים או במילים, ויש להמיר תמיד לספרות.\n"
                    "אם המשתמש כותב סכום במילים (למשל: 'חמש מאות', 'אלף', 'אלפיים חמש מאות') → המר למספר.\n"
                    "אם זה טווח (גם במילים וגם במספרים) → קח את המספר הגבוה לאחר ההמרה.\n"
                    "urgency → 1-10 לפי כמה מהר רוצה להתחיל\n"
                    "goal → 1-10 לפי בהירות המטרה (אין מטרה ברורה = 1)\n\n"

                    "urgency mapping קצר:\n"
                    "10=מייד | 9=השבוע | 8=שבוע הבא | 7=2-3 שבועות | 6=חודש הבא\n"
                    "5=1-2 חודשים | 3-4=לא בקרוב | 1-2=רק בודק\n"
                    "אל תסתמך רק על המילים המדויקות במדריך.\n"
                    "הבן את הכוונה הכללית של המשתמש והמר אותה לרמת הדחיפות המתאימה.\n\n"

                    "attempt:\n"
                    "1=שאלה כללית\n"
                    "2=ממוקדת יותר\n"
                    "3+=ישירה וברורה\n\n"

                    "כללים:\n"
                    "- רק על השדה הנוכחי\n"
                    "- עד 16 מילים\n"
                    "- בלי הסברים מיותרים\n"
                    "- בלי תגובות חברתיות\n"
                    "- תמיד להחזיר response\n"
                    "- JSON בלבד"
                )
            },
            {
                "role": "user",
                "content": f"User message: {content}"
            }
        ]


    

    
    def build_closing_message_prompt(self , mode):
        return [
                {
                "role": "system",
                "content": (
                    f"You are generating a final closing message to a lead.\n\n"

                    f"Mode: {mode}\n\n"

                    f"Your task:\n"
                    f"Write ONE closing message.\n\n"

                    f"General rules:\n"
                    f"- Output ONLY the message\n"
                    f"- No explanations\n"
                    f"- Sound natural and human\n"
                    f"- Keep it clear and simple\n\n"

                    f"If mode = cold:\n"
                    f"- 1-2 sentences\n"
                    f"- Neutral and slightly distant tone\n"
                    f"- No excitement\n"
                    f"- No persuasion\n"
                    f"- Content:\n"
                    f"  • A simple acknowledgment\n"
                    f"  • A polite closing\n"
                    f"- Do NOT invite continuation\n\n"

                    f"If mode = hot:\n"
                    f"- 2 sentences\n"
                    f"- Friendly and warm tone\n"
                    f"- Positive but not pushy\n"
                    f"- Content:\n"
                    f"  • A short positive acknowledgment\n"
                    f"  • A warm, natural closing\n"
                    f"- Do NOT invite continuation\n\n"

                    f"Do not mention the word 'mode'.\n"
                )
            }
        ] 
    



    def build_hot_lead_summary(self, all_info):
        return [
            {
                "role": "system",
                "content": (
                    f"You are writing a short summary of a HOT lead for a business owner.\n\n"

                    f"Lead data:\n{all_info}\n\n"

                    f"Your job:\n"
                    f"Write ONE short, natural-sounding paragraph that summarizes the lead.\n\n"

                    f"Rules:\n"
                    f"- Include: name, id, phone number\n"
                    f"- Include: budget, experience, urgency\n"
                    f"- Include: the lead’s final answer about next steps\n"
                    f"- Keep it concise (3-5 sentences)\n"
                    f"- Use natural, human business language\n"
                    f"- Write as a flowing paragraph (NOT a list or report)\n"
                    f"- Do NOT use labels like 'Question:' or 'Answer:'\n"
                    f"- Do NOT quote the original question or answer\n"
                    f"- Always use the lead’s name\n"
                    f"- Never use pronouns (he/she)\n"
                    f"- Do NOT invent information\n"
                    f"- Do NOT ask questions\n\n"

                    f"Style:\n"
                    f"- Write like a short business note a human would send\n"
                    f"- Avoid robotic or structured phrasing\n"
                    f"- Connect the information smoothly in sentences\n"
                )
            }
        ]


class OpenAIClient:
    def __init__(self):
        self.client = OpenAI(api_key=ai_key)


    def regular_ai_reply(self , content):
        ai_api = self.client.responses.create(
            model="gpt-5-mini" ,
            input=content
        )
        ai_response = ai_api.output_text

        if not ai_response:
            raise ValueError("The AI returned empty response")
        
        if not isinstance(ai_response , str):
            raise TypeError("AI resonse must be string")
        
        return ai_response
    

    
    def analyze_ai_reply(self , content):
        ai_analyze_api = self.client.responses.create(
            model="gpt-5-mini" ,
            input=content
        )
        ai_response = ai_analyze_api.output_text

        if not ai_response:
            raise ValueError("AI returned empty resonse")
        
        try:
            data = json.loads(ai_response)

        except:
            raise ValueError("AI retrurned invaild JSON")
        

        has_analyze_content = "extracted_data" in data or "message" in data
        has_follow_up_analyze = "lead_signal" in data
        
        if not has_analyze_content:
            raise ValueError("Invalid AI response structure")
  
        return data



class MessageScorer:
    def __init__(self):
        pass
    
    
    def score_message(self , message_to_rank):
        rank_score = 0

        if "extracted_field" in message_to_rank:
            if message_to_rank["extracted_field"] == "budget":
                if float(message_to_rank["extracted_data"]) >= 450:
                    rank_score += 3
                elif 250 <= float(message_to_rank["extracted_data"]) <= 449:
                    rank_score += 2
                else:
                    rank_score += 1

            
            
            elif message_to_rank["extracted_field"] == "goal":
                if 8 <= float(message_to_rank["extracted_data"]) <= 10:
                    rank_score += 3
                elif 5 <= float(message_to_rank["extracted_data"]) <= 7:
                    rank_score += 2
                else:
                    rank_score += 1
            
            
            elif message_to_rank["extracted_field"] == "urgency":
                if 8 <= float(message_to_rank["extracted_data"]) <= 10:
                    rank_score += 3
                elif 5 <= float(message_to_rank["extracted_data"])  <= 7:
                    rank_score += 2
                else:
                    rank_score += 1
            

        
            return {"field" :  message_to_rank["extracted_field"] , "rank_score" : rank_score}
        
        return {"field" : None , "rank_score" : rank_score}
    



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
            print(message_field)
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
    def __init__(self , conversation_builder , open_ai_client , data_access , message_scorer , lead_score_manager , lead_classifier):
        self.conversation_builder = conversation_builder
        self.open_ai_client = open_ai_client
        self.data_access = data_access
        self.message_scorer = message_scorer
        self.lead_score_manager = lead_score_manager
        self.lead_classifier = lead_classifier


        
        
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
    



    
    
    def ensure_lead_info_ready(self , phone_number , name=None):
        lead_info = self.data_access.get_lead_base_info(phone_number)
        if lead_info is None:
            return {"result" : "not exist"}
        
        return {"result" : lead_info}
    

    
    def ensure_lead_score_ready(self , lead_id):
        lead_score_info = self.data_access.get_lead_score_info(lead_id)
        if lead_score_info is None:
            return {"result" : "not exist"}
        
        return {"result" : lead_score_info}
    


    def ensure_lead_fields_ready(self , lead_id):
        lead_fields_info = self.data_access.get_all_lead_field_data(lead_id=lead_id)
        if lead_fields_info is None:
            return {"result" : "not exist"}
        
        return {"result" : lead_fields_info}

    

    def ensure_status_submitted(self , lead_id):
        status_check = self.data_access.get_lead_status(lead_id)
        if status_check is None:
            return "status crashed"
        
        return "done"

    
    
    def submit_status(self , lead_id , status=None):
        if status == None:
            return "status empty"
        
        status_check = self.ensure_status_submitted(lead_id=lead_id)
        if status_check == "status crashed":
            self.data_access.set_lead_status(lead_id=lead_id , status=status)
        
        else:
            return "done"
        


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
        


    def process_lead_message(self , phone_number , content , name=None):
        get_or_create_lead = self.lead_exists_check(phone_number=phone_number)
        if get_or_create_lead is None:
            get_or_create_lead = self.lead_exists_check(phone_number=phone_number , name=name , new=True)

        ensure_lead_tables = self.ensure_user_tables_exist(get_or_create_lead["lead_id"])

        lead_all_data = {
            "lead_base_data" : get_or_create_lead ,
            "lead_external_data"
        }

        generate_ai_response = self.generate_ai_response(lead_info=get_or_create_lead , content=content)
        if generate_ai_response is None:
            return "DONE"
        
        apply_ai_result = self.apply_ai_result(ai_response=generate_ai_response , lead_info=)




    def generate_ai_response(self , lead_info , content):
        validate_str(content , "content")

        if lead_info["status"] != "pending":
            return
        
        ai_response = self.conversation_builder.main_prompt(current_field=lead_info["current_field"] , attempt_number=lead_info["attempt_number"] , name=lead_info["name"] , content=content)

        self.data_access.add_lead_message(lead_id=lead_info["lead_id"] , role="user" , content=content)

        self.data_access.add_lead_message(lead_id=lead_info["lead_id"] , role="assistant" , content=ai_response["response"])

        return ai_response
    
#
    
    def apply_ai_result(self , ai_response , lead_info , content):
        if "extracted_field" in ai_response:
            if ai_response["extracted_field"] == "goal":
                lead_info["current_field"] = "budget"
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="goal_user" , value=content)

            elif ai_response["extracted_field"] == "budget":
                lead_info["current_field"] = "urgency"
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="budget_user" , value=content)

            elif ai_response["extracted_field"] == "urgency":
                lead_info["current_field"] = None
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="urgency_user" , value=content)
            
            
            self.data_access.update_lead_current_field(lead_info["lead_id"] , updated_field=lead_info["current_field"])
            self.data_access.update_lead_attempt_number(lead_id=lead_info["lead_id"] , number=1)

        
        if "message" in ai_response:
            self.data_access.update_lead_attempt_number(lead_id=lead_info["lead_id"] , number=lead_info["attempt_number"] + 1)


    
    
    
    def apply_message_score(self , lead_info , ai_analyze_response):
        lead_message_score = self.message_scorer.score_message(ai_analyze_response)
        
        if lead_message_score["field"] is None:
            return

        lead_score_info = {"total_score" : lead_info["total_score"] , "score_count" : lead_info["score_count"] , "goal_score" : lead_info["goal_score"] , "budget_score" : lead_info["budget_score"] , "urgency_score" : lead_info["urgency_score"]}
        self.lead_score_manager.update_lead_score_info(lead_score_info=lead_score_info , lead_message_score=lead_message_score["rank_score"] , message_field=f"{lead_message_score["field"]}_score")
        self.data_access.update_lead_score_info(lead_id=lead_info["lead_id"] , score_count=lead_score_info["score_count"] , total_score=lead_score_info["total_score"] , score_field=f"{lead_message_score["field"]}_score" , value=lead_message_score["rank_score"])


    

    
    def finalize_lead_status(self , lead_id):
        validate_int(lead_id , "lead id")

        lead_score_info = self.data_access.get_lead_score_info(lead_id)
        if lead_score_info["score_count"] == 3:
            final_lead_status = self.lead_classifier.classify_lead_score(lead_score_info)
            
            if final_lead_status:
                self.data_access.set_lead_status(lead_id , final_lead_status)
                return {"status" : "final_status" , "final_status" : final_lead_status}
            
        return {"status" : "not enough information"}

    


    
    
    
    def conversation_chat(self  , lead_info , content , question_type):
        validate_str(content , "content")

        #t = time.time()
        
        #print(lead_info["current_field"])
        #print(lead_info["attempt_number"])
        #print(question_type)
        if lead_info["current_field"] is None:
            self.data_access.add_lead_message(lead_id=lead_info["lead_id"] , role="user" , content=content)
            return {"status" : "all info provided include final status"}
        
        
        ai_content = self.conversation_builder.build_input(name=lead_info["name"] , content=content , current_field=lead_info["current_field"] , attempt=lead_info["attempt_number"] , question_type=question_type)
        #print("ai content:" , round(time.time() - t , 2) , "seconds")
        
        #t = time.time()
        ai_response = self.open_ai_client.regular_ai_reply(ai_content)
        #print("ai_response" , round(time.time() - t , 2) , "seconds")

        
        #t = time.time()
        self.data_access.add_lead_message(lead_id=lead_info["lead_id"] , role="user" , content=content)
        #print("add_message_1" , round(time.time() - t , 2) , "seconds")

        #t = time.time()
        self.data_access.add_lead_message(lead_id=lead_info["lead_id"] , role="assistant" , content=ai_response)
        #print("add_message_2" , round(time.time() - t , 2) , "seconds")
        
        
        #t = time.time()
        self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field=f"{lead_info["current_field"]}_bot" , value=ai_response)
        #print("update_field_message" , round(time.time() - t , 2) , "seconds")


        return {"status" : "ok" , "response" : ai_response}
    



    def build_analyze_input(self , lead_info , content):
        validate_str(content , "content")

        #print(lead_info["current_field"])
        prompt_content = self.conversation_builder.analyze_prompt(current_field=lead_info["current_field"] , content=content)
        ai_analyze_response = self.open_ai_client.analyze_ai_reply(prompt_content)
        return ai_analyze_response


        
        
    def process_analysis_result(self , lead_info , ai_analyze_response , user_answer):    
        if "extracted_field" in ai_analyze_response:
            if ai_analyze_response["extracted_field"] == "goal":
                lead_info["current_field"] = "budget"
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="goal_user" , value=user_answer)
                
            
            elif ai_analyze_response["extracted_field"] == "budget":
                lead_info["current_field"] = "urgency"
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="budget_user" , value=user_answer)

            
            elif ai_analyze_response["extracted_field"] == "urgency":
                lead_info["current_field"] = None
                self.data_access.update_lead_field_data(lead_id=lead_info["lead_id"] , field="urgency_user" , value=user_answer)


            lead_info["attempt_number"] = 1
            
            self.data_access.update_lead_current_field(lead_info["lead_id"] , updated_field=lead_info["current_field"])
            self.data_access.update_lead_attempt_number(lead_id=lead_info["lead_id"] , number=1)
            
            return {"status" : "info provided" , "updated_attempt" : lead_info["attempt_number"] , "updated_field" : lead_info["current_field"] , "question_type" : ai_analyze_response["result_type"]}
        
        if "message" in ai_analyze_response and "result_type" in ai_analyze_response:
            lead_info["attempt_number"] += 1
            #print(lead_info["attempt_number"])
            #print("here")
            #print(lead_info["attempt_number"])
            self.data_access.update_lead_attempt_number(lead_id=lead_info["lead_id"] , number=lead_info["attempt_number"])
            #print("here")
            return {"status" : "info didnt provided" , "updated_attempt" : lead_info["attempt_number"] , "question_type" : ai_analyze_response["result_type"]}
        
            
            
            
    def classify_lead(self , lead_info , ai_analyze_response):
        lead_message_score = self.message_scorer.score_message(ai_analyze_response)
        
        if lead_message_score["field"] != "none":
        
            lead_score_info = {"total_score" : lead_info["total_score"] , "score_count" : lead_info["score_count"] , "goal_score" : lead_info["goal_score"] , "budget_score" : lead_info["budget_score"] , "urgency_score" : lead_info["urgency_score"]}
            #print(lead_score_info)
            self.lead_score_manager.update_lead_score_info(lead_score_info=lead_score_info , lead_message_score=lead_message_score["rank_score"] , message_field=f"{lead_message_score["field"]}_score")
            #print(f"{lead_message_score["field"]}_score")
            self.data_access.update_lead_score_info(lead_id=lead_info["lead_id"] , score_count=lead_score_info["score_count"] , total_score=lead_score_info["total_score"] , score_field=f"{lead_message_score["field"]}_score" , value=lead_message_score["rank_score"])
            #print(lead_score_info)
            #print(lead_info)
            final_lead_status = self.lead_classifier.classify_lead_score(lead_score_info)
        
            if final_lead_status:
                self.data_access.set_lead_status(lead_info["lead_id"] , final_lead_status)
                return {"status" : "final_status" , "final_status" : final_lead_status}
        



    def collect_lead_summary_data(self , lead_id , phone_number):
        summary = {}
        
        base_info = self.data_access.get_lead_base_info(phone_number)
        
        goal = self.data_access.get_lead_specific_field_data(lead_id=lead_id , field="goal_user")
        budget = self.data_access.get_lead_specific_field_data(lead_id=lead_id , field="budget_user")
        urgency = self.data_access.get_lead_specific_field_data(lead_id=lead_id , field="urgency_user")

        total_score = self.data_access.get_lead_total_score(lead_id=lead_id)
        
        summary["lead_id"] = base_info["lead_id"]
        summary["name"] = base_info["name"]
        summary["phone_number"] = phone_number
        summary["goal_data"] = goal
        summary["budget_data"] = budget
        summary["urgency_data"] = urgency
        summary["total_score"] = total_score


        return {"summary_info" : summary , "lead_id" : base_info["lead_id"]}
    

    
    def format_currency(self , budget_text):
        currency_symbols = ["₪", "שקל", "שח", 'ש"ח' , "שקלים"]

        if not any(symbol in budget_text for symbol in currency_symbols):
            budget_text = budget_text.strip() + " ₪"

        return budget_text



    def generate_lead_summary(self , summary_info):
        text = (
            f"🔥 ליד חם חדש:\n\n"
            f"{summary_info["name"]} פנה לגבי אימונים.\n\n"
            f"מטרה: {summary_info["goal_data"]}\n"
            f"תקציב: {summary_info["budget_data"]} לחודש\n"
            f"זמן התחלה: {summary_info["urgency_data"]}\n\n"
            f"ציון התאמה: {summary_info["total_score"]}\n"
            f"טלפון: {summary_info["phone_number"]}"
            )
        
        return text
    

    
    def upload_lead_summary(self , summary , lead_id):
        self.data_access.upload_summary(lead_summary=summary , lead_id=lead_id)
        


    def process_lead_summary(self , lead_id , phone_number):
        data = self.collect_lead_summary_data(lead_id, phone_number)

        data["summary_info"]["budget_data"] = self.format_currency(data["summary_info"]["budget_data"])

        final_summary = self.generate_lead_summary(data["summary_info"])

        self.upload_lead_summary(summary=final_summary , lead_id=data["lead_id"])


 




data_access = DataAccess()
conversation_builder = ConversationBuilder()
openai_client = OpenAIClient()
message_scorer = MessageScorer()
lead_score_manager = LeadScoreManager()
lead_classifier = LeadClassifier()

service_layer = ServiceLayer(data_access=data_access , conversation_builder=conversation_builder , open_ai_client=openai_client , message_scorer=message_scorer , lead_score_manager=lead_score_manager , lead_classifier=lead_classifier)


data_access.create_leads_info_table()
data_access.create_leads_scores_table()
data_access.create_leads_messages_table()
data_access.create_leads_fields_data()


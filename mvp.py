
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
        attempt_number INTEGER DEFAULT 1 ,
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
        
    
   


class Questions:
    def __init__(self):
        pass



    def goal_questions(self , attempt_number=1):
        if attempt_number == 1:
            return ["מה היית רוצה להשיג בכושר?" ," מה המטרה שלך באימונים?" , "מה היעד שלך כרגע?" , "על מה אתה רוצה לעבוד בעיקר?"]
        
        elif attempt_number == 2:
            return ["מה הכי חשוב לך לשפר בגוף?" , "לאן אתה מכוון עם האימונים?"]
        
        elif attempt_number == 3:
            return ["תן כיוון כללי, מה בא לך להשיג?" , "אפילו בגדול, מה המטרה שלך?"]

    

    def budget_quesitons(self , attempt_number=1):  
        if attempt_number == 1:
            return ["מה התקציב שלך?" , "כמה בערך נוח לך להשקיע?" , "יש לך טווח תקציב בראש?" , "כמה מתאים לך לשים על זה?"]
        
        elif attempt_number == 2:
            return ["בערך, כמה חשבת להשקיע?" , "איזה סכום מתאים לך?"]
        
        elif attempt_number == 3:
            return ["אפילו בערך, איזה תקציב יש לך?" , "מה התקציב המקסימלי שמתאים לך?"]



    def urgency_quesitons(self , attempt_number=1):
        if attempt_number == 1:
            return ["מתי תרצה להתחיל?" , "מתי אתה מתכנן להתחיל את האימונים?" , "מתי זה מתאים לך להתחיל?" , "מתי היית רוצה להתחיל בפועל?"]

        elif attempt_number == 2:
            return ["תוך כמה זמן אתה רואה את עצמך מתחיל?" , "מתי בערך היית רוצה להתחיל?"]
        
        elif attempt_number == 3:
            return ["אפילו בערך, מתי תרצה להתחיל?" , "אפילו בגדול, מתי מתאים לך להתחיל?"]

    

    def process_questions(self , mode , attempt_number):
        if mode == "goal":
            questions = self.goal_questions(attempt_number=attempt_number)

        elif mode == "budget":
            questions = self.budget_quesitons(attempt_number=attempt_number)

        elif mode == "urgency":
            questions = self.urgency_quesitons(attempt_number=attempt_number)

        else:
            raise ValueError("Invalid mode")

        return random.choice(questions)





class ConversationBuilder:
    def __init__(self):
        pass



    def analyze_prompt(current_field , content):
        return [
            {
                "role": "system",
                "content": (
                    "אתה מנתח הודעת משתמש ומחזיר JSON בלבד.\n\n"

                    "מטרתך:\n"
                    "לבדוק האם יש מידע רלוונטי לשדה הנוכחי.\n\n"

                    "החזר JSON באחד מהפורמטים בלבד:\n\n"

                    "אם יש מידע:\n"
                    "{"
                    "\"status\":\"found\","
                    "\"value\":NUMBER,"
                    "\"ack\":\"TEXT\""
                    "}\n\n"

                    "אם אין מידע:\n"
                    "{"
                    "\"status\":\"missing\","
                    "}\n\n"

                    "אם המשתמש מבולבל:\n"
                    "{"
                    "\"status\":\"confused\","
                    "\"clarify\":\"TEXT\""
                    "}\n\n"

                    "חוקים:\n"
                    "- נתח רק את ההודעה האחרונה\n"
                    "- התייחס רק לשדה: " + current_field + "\n"
                    "- אל תשאל שאלות\n"
                    "- אל תנהל שיחה\n"
                    "- אל תחזיר הסברים\n"
                    "- החזר JSON בלבד ללא טקסט נוסף\n\n"

                    "====================\n"

                    "goal:\n"
                    "החזר מספר 1-10 לפי כמה המטרה ברורה.\n"
                    "אם המשתמש נתן מטרה כלשהי → זה מידע.\n"
                    "רק אם אין בכלל מטרה → missing.\n\n"

                    "budget:\n"
                    "החזר סכום מספרי.\n"
                    "אם יש טווח → קח את הגבוה.\n"
                    "אם אין סכום ברור → missing.\n\n"

                    "urgency:\n"
                    "החזר מספר 1-10 לפי זמן התחלה.\n"
                    "10 = מיידי, 1 = רחוק מאוד\n"
                    "אם אין זמן ברור → missing.\n\n"

                    "====================\n"

                    "missing:\n"
                    "אם המשתמש ענה משהו כללי כמו:\n"
                    "'לא יודע', 'לא בטוח', 'אולי'\n"
                    "→ missing\n\n"

                    "confused:\n"
                    "אם המשתמש כתב:\n"
                    "'מה?', 'לא הבנתי', 'אה?'\n"
                    "או שהתשובה לא קשורה לשאלה\n"
                    "→ confused\n\n"

                    "ack:\n"
                    "- 2 עד 4 מילים בלבד\n"
                    "- תגובה טבעית קצרה\n"
                    "- לא לשאול שאלה\n"
                    "- דוגמאות:\n"
                    "  'סבבה'\n"
                    "  'מעולה'\n"
                    "  'הבנתי'\n"
                    "  'לא ברור עדיין'\n\n"

                    "clarify:\n"
                    "- עד 8 מילים בלבד\n"
                    "- הסבר פשוט למה התכוונת\n"
                    "- בלי חפירות\n"
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
            max_completion_tokens=60,
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
            return {"status" : "exist"}

        validate_str(content , "content")

        lead_id = get_or_create_lead["lead_id"]
        
        ensure_lead_tables = self.ensure_user_tables_exist(lead_id)
        
        lead_base_data = self.build_base_lead_data(base_data=get_or_create_lead)
        lead_scores_data = self.build_lead_scores_data(scores_data=ensure_lead_tables["lead_scores_data"])
        lead_fields_data = self.build_lead_fields_data(fields_data=ensure_lead_tables["lead_fields_data"])
        
        current_field = lead_base_data["current_field"]
        total_score = lead_scores_data["total_score"]
                
        generate_ai_question = self.generate_question(lead_info=lead_base_data , content=content)
        if generate_ai_question is None:
            return {"status" : "DONE"}
        
        ai_response = self.generate_analyze(content=content , current_field=current_field)
        
        
        self.apply_ai_result(ai_response=ai_response , lead_info=lead_base_data , content=content)

        self.apply_message_score(lead_info=lead_scores_data , current_field=current_field , ai_analyze_response=ai_response)
        

        finalize_lead_status = self.finalize_lead_status(lead_scores_data)
        if finalize_lead_status is not None:
            final_lead_status = finalize_lead_status["final_status"]

            if final_lead_status == "Hot Lead":
                summary_data = self.build_summary_data(base_data=lead_base_data , fields_data=lead_fields_data , total_score=total_score)
                self.process_lead_summary(summary_data)

        answer = self.build_user_response(ai_response=ai_response , question=generate_ai_question)
        return {"status" : "in process" , "response" : answer}
    
    

    
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
        



    def generate_question(self , lead_info , content):
        validate_str(content , "content")

        if lead_info["status"] != "pending":
            return
        
        
        question = self.questions.process_questions(mode=lead_info["current_field"] , attempt_number=lead_info["attempt_number"])

        self.data_access.add_lead_message(lead_id=lead_info["lead_id"] , role="user" , content=content)

        self.data_access.add_lead_message(lead_id=lead_info["lead_id"] , role="bot" , content=question)

        return question
    



    def generate_analyze(self , current_field , content):
        ai_input = self.conversation_builder.analyze_prompt(current_field=current_field , content=content)
        return self.open_ai_client.ai_reply(ai_input)
    

    
    def build_user_response(self , ai_response , question):
        if ai_response["status"] == "found":
            return f"{ai_response['ack']}. {question}"

        elif ai_response["status"] == "missing":
            return question

        elif ai_response["status"] == "confused":
            return ai_response["clarify"]


    
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
        lead_message_score = self.message_scorer.score_message(message_to_rank=ai_analyze_response , field=current_field)
        
        if lead_message_score["status"] == "missing":
            return

        self.lead_score_manager.update_lead_score_info(lead_score_info=lead_info , lead_message_score=lead_message_score["rank_score"] , message_field=f"{current_field}_score")
        self.data_access.update_lead_score_info(lead_id=lead_info["lead_id"] , score_count=lead_info["score_count"] , total_score=lead_info["total_score"] , score_field=f"{current_field}_score" , value=lead_message_score["rank_score"])


    
    def finalize_lead_status(self , lead_info):
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
    if message_process["status"] == "new":
        lead_name = input("Please enter your name: ")
        validate_str(lead_name , "name")

        content = input("Please enter your message: ")
        validate_str(content , "content")
        
        message_process = service_layer.process_lead_message(phone_number=phone_number , content=content , name=lead_name , mode=2)
        
    
    
    if message_process["status"] == "exist":
        content = input("Please enter your message: ")
        validate_str(content , "content")
        message_process = service_layer.process_lead_message(phone_number=phone_number , content=content , mode=2)
    
    
    if message_process["status"] == "DONE":
        print(f"Thank you for your cooperation. We will contact you soon")
        break

    if message_process["status"] == "in process":
        raw_message = message_process["response"]
        print(get_display(raw_message))
        

    

    #except Exception as e:
        #print(f"Error: {e}")
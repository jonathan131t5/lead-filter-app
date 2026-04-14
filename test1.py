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


def main_prompt(current_field, attempt_number, content):
        return [
            {
                "role": "system",
                "content": f"""
    אתה מנוע ניתוח שיחה.
    החזר JSON בלבד.
    ללא הסברים.
    ללא Markdown.

    יש 2 מצבים בלבד:

    1. יש מידע עבור השדה הנוכחי:
    {{"extracted_field":"{current_field}","extracted_data":NUMBER,"response":"מעולה"}}

    2. אין מידע:
    {{"message":"THERE IS NO INFO","response":"TEXT"}}

    חוקים:
    - נתח רק את ההודעה האחרונה
    - התייחס רק לשדה: {current_field}
    - אם יש מידע ברור → תמיד החזר extracted
    - אחרת → החזר THERE IS NO INFO

    response מותר רק מהבאים:

    goal:
    - attempt 1: "מה אתה רוצה להשיג בכושר?"
    - attempt 2: "מה המטרה שלך בכושר?"
    - attempt 3+: "מה היעד שלך בכושר?"

    budget:
    - attempt 1: "מה התקציב שלך?"
    - attempt 2: "כמה אתה מוכן לשלם?"
    - attempt 3+: "איזה תקציב יש לך?"

    urgency:
    - attempt 1: "מתי תרצה להתחיל?"
    - attempt 2: "תוך כמה זמן תרצה להתחיל?"
    - attempt 3+: "מתי נוח לך להתחיל?"

    אם המשתמש מבולבל:
    - goal: "אני שואל מה אתה רוצה להשיג בכושר?"
    - budget: "אני שואל מה התקציב שלך?"
    - urgency: "אני שואל מתי תרצה להתחיל?"

    חילוץ:

    goal → מספר 1-10 לפי בהירות  
    budget → סכום בשקלים  
    urgency → מספר 1-10 לפי דחיפות  

    אם אין מספר ברור → אין מידע

    attempt_number: {attempt_number}

    החזר JSON בלבד.
    """.strip()
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
            max_completion_tokens=120,
            response_format={"type": "json_object"}
        )

        text = res.choices[0].message.content
        fixed_text = get_display(text)
        print(fixed_text)

        data = json.loads(text)

        # validation קצר
        if "response" not in data:
            raise ValueError("no response")

        if not (
            ("message" in data and data["message"] == "THERE IS NO INFO") or
            ("extracted_field" in data and "extracted_data" in data)
        ):
            raise ValueError("bad structure")

        return data



open_ai = OpenAIClient(ai_key)

ai_input = main_prompt("budget" , 1 , "hi")
open_ai.ai_reply(ai_input)
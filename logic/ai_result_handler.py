import json
from openai import OpenAI
from dotenv import load_dotenv
import os

class OpenAIClient:
    def __init__(self):
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
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
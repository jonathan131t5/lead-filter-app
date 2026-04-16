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
            top_p=1,
            max_completion_tokens=40,
            response_format={"type": "json_object"}
        )

        text = res.choices[0].message.content
        #print("RAW:", text)

        data = json.loads(text)

        # validation קצר
        if "status" not in data:
            raise ValueError("AI returned invalid JSON structure")

        if not any(key in data for key in ["ack", "clarify", "value", "reason"]):
            raise ValueError("AI returned invalid JSON structure")

        return data
import json
from openai import OpenAI
from dotenv import load_dotenv
import os
import logging


class OpenAIClient:
    def __init__(self):
        load_dotenv()

        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key)
    
    def ai_reply(self, messages):
        import time
        start = time.time()
        res = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0,
            top_p=1,
            max_completion_tokens=15,
            presence_penalty=0,
            frequency_penalty=0,
            response_format={"type": "json_object"}
        )


        logging.info(f"OpenAI took: {time.time() - start:.2f}s")

        text = res.choices[0].message.content
        #print("RAW:", text)

        data = json.loads(text)
        #print(data, flush=True)
        # validation קצר
        if "status" not in data:
            raise ValueError("AI returned invalid JSON structure")
        return data
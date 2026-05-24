import json
from openai import OpenAI 
from dotenv import load_dotenv
import os
import time

#from logic.ai_result_handler import OpenAIClient


class ConversationBuilder:
    def __init__(self):
        #self.open_ai_client = OpenAIClient()
        pass

    def build_prompt(self , current_field , content): 
        if current_field == "goal":
            prompt = self.goal_analyze_prompt(content=content)


        elif current_field == "urgency":
            prompt = self.urgency_analyze_prompt(content=content)
        
        return prompt
    



    
    def goal_analyze_prompt(self, content):
        return [
            {
                "role": "system",
                "content": (
                    "Classify the user's answer for the GOAL field.\n"
                    "Return ONLY valid JSON.\n\n"

                    "Allowed formats only:\n"
                    "{\"status\":\"found\",\"value\":number}\n"
                    "{\"status\":\"missing\",\"reason\":\"no_info|vague|avoid\"}\n"
                    "{\"status\":\"confused\",\"reason\":\"meaning|answer_type|focus\"}\n\n"

                    "Rules:\n"
                    "- Symbols/no real words like '???', '...' or '-' -> missing no_info\n"
                    "- User confused about the question -> confused meaning\n"
                    "- User asks how to answer -> confused answer_type\n"
                    "- Time/start-date answer -> confused focus\n"
                    "- Money/budget answer -> confused focus\n"
                    "- Uncertain answers like 'we'll see', 'depends' -> missing vague\n"
                    "- Refusal/avoidance like 'not sure yet', 'prefer not to say' -> missing avoid\n"
                    "- Clear desired outcome -> found\n\n"

                    "Goal = what the user wants to achieve.\n"
                    "Short clear goals are valid.\n\n"

                    "Scoring:\n"
                    "- 8-10 = strong/specific/serious goal\n"
                    "- 5-7 = normal clear goal, even if short\n"
                    "- 3-4 = weak unclear direction\n"
                    "- 1-2 = almost no goal\n"
                    "- Most clear goals should be 5-7, not 3-4.\n"
                    "- Do not give 8+ unless the goal is clearly strong or specific.\n\n"

                    "Examples:\n"
                    "??? -> {\"status\":\"missing\",\"reason\":\"no_info\"}\n"
                    "tomorrow -> {\"status\":\"confused\",\"reason\":\"focus\"}\n"
                    "450 dollars -> {\"status\":\"confused\",\"reason\":\"focus\"}\n"
                    "what do you mean -> {\"status\":\"confused\",\"reason\":\"meaning\"}\n"
                    "we'll see -> {\"status\":\"missing\",\"reason\":\"vague\"}\n"
                    "not sure yet -> {\"status\":\"missing\",\"reason\":\"avoid\"}\n"
                    "I want more clients -> {\"status\":\"found\",\"value\":6}\n"
                )
            },
            {
                "role": "user",
                "content": content
            }
        ]
    
    

    
    def urgency_analyze_prompt(self, content):
        return [
            {
                "role": "system",
                "content": (
                    "You are an information extraction engine for the urgency field only.\n"
                    "Return JSON only. No extra text, no questions, no explanations.\n"

                    "\nTop priority rules:\n"
                    "- If the message contains only symbols or no words, for example '???', '...', '-' -> missing:no_info.\n"
                    "- If the user explicitly says they did not understand, for example 'I didn't understand', 'what do you mean' -> confused:meaning.\n"
                    "- If the user asks how to answer, for example 'what should I write', 'how should I answer' -> confused:answer_type.\n"
                    "- If the answer is a fitness goal, for example 'get toned', 'build muscle', 'fitness' -> confused:focus.\n"
                    "- If the answer is money, for example '450', '300 dollars', 'up to 400' -> confused:focus.\n"
                    "- If the user refuses to answer, for example 'I don't want to answer', 'I'd rather not say' -> missing:avoid.\n"

                    "\nResponse format:\n"
                    '{"status":"found","value":<number>}\n'
                    '{"status":"missing","reason":"no_info"}\n'
                    '{"status":"missing","reason":"vague"}\n'
                    '{"status":"missing","reason":"avoid"}\n'
                    '{"status":"confused","reason":"meaning"}\n'
                    '{"status":"confused","reason":"answer_type"}\n'
                    '{"status":"confused","reason":"focus"}\n'

                    "\nDefinition of urgency:\n"
                    "- urgency is how soon the user wants to start.\n"
                    "- Convert the answer into a score from 1-10 based on the level of urgency.\n"

                    "\nNormal decision order:\n"
                    "1. If there is a clear intention about start time -> found\n"
                    "2. If there is no information at all -> missing:no_info\n"
                    "3. If the answer is too general -> missing:vague\n"
                    "4. If the answer is clearly not time, but a goal or money -> confused:focus\n"

                    "\nValue scoring rules:\n"
                    "- Return a number from 1-10 based on the level of urgency and closeness in time.\n"
                    "- 8-10: High urgency. For example, the user wants to start now, immediately, today, tomorrow, this week, or as soon as possible.\n"
                    "- 5-7: Medium urgency. The user wants to start soon, within the next month, or at a relatively close time but not immediately.\n"
                    "- 1-4: Low urgency. The user is not in a rush, talks about later, someday, or does not give a clear time.\n"
                    "- Do not give 8 or higher just because the answer is positive. For 8+, there must be a close start time or clear urgency.\n"
                    "- If the user says 'soon' without details, give 6-7 and not 8-10.\n"
                    "- If the user says 'in a few weeks', give 5-6.\n"
                    "- If the user says 'in a month', 'next month', 'within the next month' or 'in the next month', give 6-7.\n"
                    "- If the user says 'in the next few days', give 8.\n"
                    "- If the user says something meaning immediate or very soon start, for example 'this week', 'tomorrow', 'today', 'now', 'immediately', or 'as soon as possible', give 9-10.\n"
                    "- If the user says something meaning low urgency, for example 'not urgent', 'later', or 'someday', give 2-4 depending on the urgency level.\n"
                    "- In a few months / in 3-6 months -> 3\n"
                    "- In six months or more -> 1-2\n"

                    "\nImportant rules:\n"
                    "- Identify by meaning, not only by exact words.\n"
                    "- Account for typos, slang, and short answers.\n"
                    "- If the answer is too general, like 'we'll see', 'I don't know', 'depends' -> missing:vague.\n"
                    "- Do not return focus because of a weak answer.\n"
                    "- focus only if it is clearly an answer to another field.\n"

                    "\nExamples:\n"
                    "- 'now' -> found, value=10\n"
                    "- 'tomorrow' -> found, value=9\n"
                    "- 'this week' -> found, value=9\n"
                    "- 'soon' -> found, value=6\n"
                    "- 'in a month' -> found, value=6\n"
                    "- 'not urgent' -> found, value=3\n"
                    "- 'someday' -> found, value=2\n"
                    "- 'we'll see' -> missing:vague\n"
                    "- '???' -> missing:no_info\n"
                    "- '450' -> confused:focus\n"
                    "- 'get toned' -> confused:focus\n"
                    "- 'I didn't understand what you mean' -> confused:meaning\n"
                    "- 'how do I answer this' -> confused:answer_type\n"
                )
            },
            {
                "role": "user",
                "content": content
            }
        ]
    








    #def test_goal_prompt(self):
        test_cases = [
            "I want more clients",
            "I want to scale my coaching business",
            "tomorrow",
            "450 dollars",
            "we'll see",
            "???",
            "what do you mean",
            "I want to lose weight",
            "I want to grow my online business",
            "not sure yet"
        ]

        for text in test_cases:
            print("\n------------------")
            print("INPUT:", text)

            prompt = self.goal_analyze_prompt(text)

            result = self.open_ai_client.ai_reply(messages=prompt)

            print("OUTPUT:", result)




#conve = ConversationBuilder()

#print(conve.test_goal_prompt())
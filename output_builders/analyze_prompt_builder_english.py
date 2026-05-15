import json
from openai import OpenAI 
from dotenv import load_dotenv
import os
import time



class ConversationBuilder:
    def __init__(self):
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
                    "You are an information extraction engine for the goal field only.\n"
                    "Return JSON only. No extra text, no questions, no explanations.\n"

                    "\nTop priority rules:\n"
                    "- If the message contains only symbols or no words, for example '???', '...', '-' -> missing:no_info.\n"
                    "- If the user expresses confusion or did not understand the question, for example 'what?', 'what', 'I didn't understand', 'what do you mean', 'what does that mean' -> confused:meaning.\n"
                    "- If the user asks how to answer, for example 'what should I write', 'how should I answer' -> confused:answer_type.\n"
                    "- If the answer is a start time, for example 'today', 'tomorrow', 'this week', 'soon', 'in a month', 'as soon as possible' -> confused:focus.\n"
                    "- If the answer is money, for example '450', '300 dollars', 'up to 400' -> confused:focus.\n"
                    "- If the answer is avoidance/uncertainty, for example 'we'll see', 'I don't know', 'not sure', 'depends' -> missing:vague.\n"
                    "- If the user refuses to answer, for example 'I don't want to answer', 'I'd rather not say' -> missing:avoid.\n"

                    "\nResponse format:\n"
                    '{"status":"found","value":<number>}\n'
                    '{"status":"missing","reason":"no_info"}\n'
                    '{"status":"missing","reason":"vague"}\n'
                    '{"status":"missing","reason":"avoid"}\n'
                    '{"status":"confused","reason":"meaning"}\n'
                    '{"status":"confused","reason":"answer_type"}\n'
                    '{"status":"confused","reason":"focus"}\n'

                    "\nDefinition of goal:\n"
                    "- goal is the main objective the user wants to achieve.\n"
                    "- The goal can be short, general, or specific, as long as it is clear what the user wants.\n"

                    "\nNormal decision order:\n"
                    "1. If there is a clear enough goal -> found\n"
                    "2. If there is no information at all -> missing:no_info\n"
                    "3. If there is a direction that is too weak or too general -> missing:vague\n"
                    "4. If the answer is clearly not a goal but money or time -> confused:focus\n"

                    "\nValue scoring rules:\n"
                    "- Return a number from 1-10 based on clarity, specificity, and strength of the goal.\n"
                    "- 8-10: Very strong goal. It is clear what the user wants, and there is a sharp, specific, or serious enough direction. Do not give 8 or higher just because the answer is understandable.\n"
                    "- 5-7: Understandable and clear goal, but relatively general or without much detail. Most short and normal answers should be here.\n"
                    "- 3-4: Weak or vague goal, but there is still some direction.\n"
                    "- 1-2: Almost no goal at all.\n"
                    "- A short answer can get 8-10 only if it is very strong and clear by itself.\n"
                    "- If the answer is clear but general, prefer 5-7 and not 8-10.\n"

                    "\nImportant rules:\n"
                    "- Identify by meaning, not only by exact words.\n"
                    "- Account for typos, slang, and short answers.\n"
                    "- General but understandable answers can still be found.\n"
                    "- Do not return confused:meaning unless the user is actually expressing confusion.\n"
                    "- Do not return focus because of a short or weak answer.\n"

                    "\nExamples:\n"
                    "- '???' -> missing:no_info\n"
                    "- 'we'll see' -> missing:vague\n"
                    "- '450' -> confused:focus\n"
                    "- 'this week' -> confused:focus\n"
                    "- 'what?' -> confused:meaning\n"
                    "- 'I didn't understand what you mean' -> confused:meaning\n"
                    "- 'what should I answer' -> confused:answer_type\n"
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
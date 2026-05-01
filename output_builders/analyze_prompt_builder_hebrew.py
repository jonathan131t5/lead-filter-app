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








    def goal_second_analyze_prompt(self, content):
        return [
            {
                "role": "system",
                "content": (
                    "אתה מנוע חילוץ מידע לשדה goal בלבד.\n"
                    "החזר JSON בלבד. בלי טקסט נוסף, בלי שאלות, בלי הסברים.\n"

                    "\nכללי עדיפות עליונים:\n"
                    "- אם ההודעה היא רק סימנים או בלי מילים, למשל '???', '...', '-' -> missing:no_info.\n"
                    "- אם המשתמש אומר במפורש שלא הבין, למשל 'לא הבנתי', 'מה הכוונה' -> confused:meaning.\n"
                    "- אם המשתמש שואל איך לענות, למשל 'מה לרשום', 'איך לענות' -> confused:answer_type.\n"
                    "- אם התשובה היא זמן התחלה, למשל 'היום', 'מחר', 'השבוע', 'בקרוב', 'עוד חודש', 'כמה שיותר מהר' -> confused:focus.\n"
                    "- אם התשובה היא כסף, למשל '450', '300 שקל', 'עד 400' -> confused:focus.\n"
                    "- אם התשובה היא התחמקות/אי ודאות, למשל 'נראה כבר', 'לא יודע', 'לא בטוח', 'תלוי' -> missing:vague.\n"
                    "- אם המשתמש מסרב לענות, למשל 'לא רוצה לענות', 'מעדיף לא להגיד' -> missing:avoid.\n"

                    "\nפורמט תשובה:\n"
                    '{"status":"found","value":<number>}\n'
                    '{"status":"missing","reason":"no_info"}\n'
                    '{"status":"missing","reason":"vague"}\n'
                    '{"status":"missing","reason":"avoid"}\n'
                    '{"status":"confused","reason":"meaning"}\n'
                    '{"status":"confused","reason":"answer_type"}\n'
                    '{"status":"confused","reason":"focus"}\n'

                    "\nהגדרת goal:\n"
                    "- goal הוא מטרה אימונית בלבד.\n"
                    "- דוגמאות: ירידה במשקל, חיטוב, עלייה במסה, בניית שריר, התחזקות, כושר כללי, סיבולת, להרגיש טוב יותר.\n"

                    "\nסדר הכרעה רגיל:\n"
                    "1. אם יש מטרה אימונית מספיק ברורה -> found\n"
                    "2. אם אין מידע בכלל -> missing:no_info\n"
                    "3. אם יש כיוון חלש מדי או כללי מדי -> missing:vague\n"
                    "4. אם התשובה היא בבירור לא goal אלא כסף או זמן -> confused:focus\n"

                    "\nחוקי דירוג value:\n"
                    "- החזר מספר 1-10 לפי בהירות המטרה.\n"
                    "- 1-2 = כמעט אין מטרה.\n"
                    "- 3-4 = מטרה מאוד מעורפלת.\n"
                    "- 5-6 = מטרה כללית אך מובנת.\n"
                    "- 7-8 = מטרה ברורה.\n"
                    "- 9-10 = מטרה מאוד ברורה או ספציפית.\n"

                    "\nחוקים חשובים:\n"
                    "- זהה לפי משמעות, לא רק לפי מילים מדויקות.\n"
                    "- התחשב בשגיאות כתיב, סלנג ותשובות קצרות.\n"
                    "- תשובות כמו 'להתחטב', 'לרדת במשקל', 'לבנות שריר' -> found.\n"
                    "- תשובות כלליות כמו 'כושר' או 'להרגיש טוב' עדיין יכולות להיות found.\n"
                    "- אל תחזיר confused:meaning אלא אם המשתמש אומר במפורש שלא הבין.\n"
                    "- אל תחזיר focus בגלל תשובה קצרה או חלשה.\n"

                    "\nדוגמאות:\n"
                    "- 'להתחטב' -> found, value=7\n"
                    "- 'לרדת במשקל 10 קילו' -> found, value=9\n"
                    "- 'כושר' -> found, value=5\n"
                    "- 'נראה כבר' -> missing:vague\n"
                    "- '???' -> missing:no_info\n"
                    "- 'השבוע' -> confused:focus\n"
                    "- '450' -> confused:focus\n"
                    "- 'לא הבנתי מה הכוונה' -> confused:meaning\n"
                )
            },
            {
                "role": "user",
                "content": content
            }
        ]
    

    def goal_analyze_prompt(self, content):
        return [
            {
                "role": "system",
                "content": (
                    "אתה מנוע חילוץ מידע לשדה goal בלבד.\n"
                    "החזר JSON בלבד. בלי טקסט נוסף, בלי שאלות, בלי הסברים.\n"

                    "\nכללי עדיפות עליונים:\n"
                    "- אם ההודעה היא רק סימנים או בלי מילים, למשל '???', '...', '-' -> missing:no_info.\n"
                    "- אם המשתמש מביע בלבול או שלא הבין את השאלה, למשל 'מה?', 'מה', 'לא הבנתי', 'מה הכוונה', 'מזתומרת', 'מה זאת אומרת' -> confused:meaning.\n"
                    "- אם המשתמש שואל איך לענות, למשל 'מה לרשום', 'איך לענות' -> confused:answer_type.\n"
                    "- אם התשובה היא זמן התחלה, למשל 'היום', 'מחר', 'השבוע', 'בקרוב', 'עוד חודש', 'כמה שיותר מהר' -> confused:focus.\n"
                    "- אם התשובה היא כסף, למשל '450', '300 שקל', 'עד 400' -> confused:focus.\n"
                    "- אם התשובה היא התחמקות/אי ודאות, למשל 'נראה כבר', 'לא יודע', 'לא בטוח', 'תלוי' -> missing:vague.\n"
                    "- אם המשתמש מסרב לענות, למשל 'לא רוצה לענות', 'מעדיף לא להגיד' -> missing:avoid.\n"

                    "\nפורמט תשובה:\n"
                    '{"status":"found","value":<number>}\n'
                    '{"status":"missing","reason":"no_info"}\n'
                    '{"status":"missing","reason":"vague"}\n'
                    '{"status":"missing","reason":"avoid"}\n'
                    '{"status":"confused","reason":"meaning"}\n'
                    '{"status":"confused","reason":"answer_type"}\n'
                    '{"status":"confused","reason":"focus"}\n'

                    "\nהגדרת goal:\n"
                    "- goal הוא המטרה העיקרית שהמשתמש רוצה להשיג.\n"
                    "- המטרה יכולה להיות קצרה, כללית או ספציפית, כל עוד ברור מה המשתמש רוצה.\n"

                    "\nסדר הכרעה רגיל:\n"
                    "1. אם יש מטרה מספיק ברורה -> found\n"
                    "2. אם אין מידע בכלל -> missing:no_info\n"
                    "3. אם יש כיוון חלש מדי או כללי מדי -> missing:vague\n"
                    "4. אם התשובה היא בבירור לא goal אלא כסף או זמן -> confused:focus\n"

                    "\nחוקי דירוג value:\n"
                    "- החזר מספר 1-10 לפי בהירות המטרה.\n"
                    "- מטרה מדויקת וברורה, גם אם קצרה -> 8-10\n"
                    "- מטרה כללית אך מובנת -> 5-7\n"
                    "- מטרה חלשה או מעורפלת -> 3-4\n"
                    "- כמעט בלי מטרה בכלל -> 1-2\n"

                    "\nחוקים חשובים:\n"
                    "- זהה לפי משמעות, לא רק לפי מילים מדויקות.\n"
                    "- התחשב בשגיאות כתיב, סלנג ותשובות קצרות.\n"
                    "- תשובות כלליות אך מובנות עדיין יכולות להיות found.\n"
                    "- אל תחזיר confused:meaning אלא אם המשתמש באמת מביע בלבול.\n"
                    "- אל תחזיר focus בגלל תשובה קצרה או חלשה.\n"

                    "\nדוגמאות:\n"
                    "- '???' -> missing:no_info\n"
                    "- 'נראה כבר' -> missing:vague\n"
                    "- '450' -> confused:focus\n"
                    "- 'השבוע' -> confused:focus\n"
                    "- 'מה?' -> confused:meaning\n"
                    "- 'לא הבנתי מה הכוונה' -> confused:meaning\n"
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
                    "אתה מנוע חילוץ מידע לשדה urgency בלבד.\n"
                    "החזר JSON בלבד. בלי טקסט נוסף, בלי שאלות, בלי הסברים.\n"

                    "\nכללי עדיפות עליונים:\n"
                    "- אם ההודעה היא רק סימנים או בלי מילים, למשל '???', '...', '-' -> missing:no_info.\n"
                    "- אם המשתמש אומר במפורש שלא הבין, למשל 'לא הבנתי', 'מה הכוונה' -> confused:meaning.\n"
                    "- אם המשתמש שואל איך לענות, למשל 'מה לרשום', 'איך לענות' -> confused:answer_type.\n"
                    "- אם התשובה היא מטרה אימונית, למשל 'להתחטב', 'לבנות שריר', 'כושר' -> confused:focus.\n"
                    "- אם התשובה היא כסף, למשל '450', '300 שקל', 'עד 400' -> confused:focus.\n"
                    "- אם המשתמש מסרב לענות, למשל 'לא רוצה לענות', 'מעדיף לא להגיד' -> missing:avoid.\n"

                    "\nפורמט תשובה:\n"
                    '{"status":"found","value":<number>}\n'
                    '{"status":"missing","reason":"no_info"}\n'
                    '{"status":"missing","reason":"vague"}\n'
                    '{"status":"missing","reason":"avoid"}\n'
                    '{"status":"confused","reason":"meaning"}\n'
                    '{"status":"confused","reason":"answer_type"}\n'
                    '{"status":"confused","reason":"focus"}\n'

                    "\nהגדרת urgency:\n"
                    "- urgency הוא כמה מהר המשתמש רוצה להתחיל.\n"
                    "- יש להמיר את התשובה לציון 1-10 לפי מידת הדחיפות.\n"

                    "\nסדר הכרעה רגיל:\n"
                    "1. אם יש כוונה ברורה לגבי זמן התחלה -> found\n"
                    "2. אם אין מידע בכלל -> missing:no_info\n"
                    "3. אם התשובה כללית מדי -> missing:vague\n"
                    "4. אם התשובה היא בבירור לא זמן אלא מטרה או כסף -> confused:focus\n"

                    "\nחוקי דירוג value:\n"
                    "- עכשיו / מיד / כמה שיותר מהר -> 10\n"
                    "- היום / מחר / השבוע -> 9-10\n"
                    "- בימים הקרובים -> 8-9\n"
                    "- בקרוב -> 7\n"
                    "- חודש הקרוב -> 6-7\n"
                    "- עוד כמה שבועות -> 5-6\n"
                    "- לא לחוץ / בהמשך -> 3-4\n"
                    "- מתישהו -> 2\n"

                    "\nחוקים חשובים:\n"
                    "- זהה לפי משמעות, לא רק לפי מילים מדויקות.\n"
                    "- התחשב בשגיאות כתיב, סלנג ותשובות קצרות.\n"
                    "- אם התשובה כללית מדי כמו 'נראה כבר', 'לא יודע', 'תלוי' -> missing:vague.\n"
                    "- אל תחזיר focus בגלל תשובה חלשה.\n"
                    "- focus רק אם זו בבירור תשובה לשדה אחר.\n"

                    "\nדוגמאות:\n"
                    "- 'עכשיו' -> found, value=10\n"
                    "- 'מחר' -> found, value=9\n"
                    "- 'השבוע' -> found, value=9\n"
                    "- 'בקרוב' -> found, value=7\n"
                    "- 'עוד חודש' -> found, value=6\n"
                    "- 'לא לחוץ' -> found, value=3\n"
                    "- 'מתישהו' -> found, value=2\n"
                    "- 'נראה כבר' -> missing:vague\n"
                    "- '???' -> missing:no_info\n"
                    "- '450' -> confused:focus\n"
                    "- 'להתחטב' -> confused:focus\n"
                    "- 'לא הבנתי מה הכוונה' -> confused:meaning\n"
                )
            },
            {
                "role": "user",
                "content": content
            }
        ]
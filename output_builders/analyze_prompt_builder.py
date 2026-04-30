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

        elif current_field == "preferences":
            prompt = self.preferences_analyze_prompt(content=content)

        elif current_field == "urgency":
            prompt = self.urgency_analyze_prompt(content=content)

        return prompt




    def main_analyze_prompt(self, current_field, content):
        return [
            {
                "role": "system",
                "content": (
                    "אתה מנוע חילוץ מידע.\n"
                    "החזר JSON בלבד. בלי טקסט נוסף, בלי שאלות, בלי הסברים, בלי markdown.\n"

                    f"\nהשדה הנוכחי: {current_field}\n"
                    "השדות האפשריים: goal, budget, urgency\n"

                    "\nפורמט תשובה בלבד:\n"
                    '{"status":"found","value":<number>}\n'
                    '{"status":"missing","reason":"no_info"}\n'
                    '{"status":"missing","reason":"vague"}\n'
                    '{"status":"missing","reason":"avoid"}\n'
                    '{"status":"confused","reason":"meaning"}\n'
                    '{"status":"confused","reason":"answer_type"}\n'
                    '{"status":"confused","reason":"focus"}\n'

                    "\nחוק עליון:\n"
                    "- נתח רק לפי current_field.\n"
                    "- אם יש התאמה לשדה הנוכחי → המשך רגיל.\n"
                    "- אם התשובה מתאימה בבירור לשדה אחר → confused:focus.\n"
                    "- אחרת → missing.\n"

                    "\nסדר הכרעה:\n"
                    "1. לא הבין את השאלה עצמה → confused:meaning\n"
                    "2. לא יודע איך לענות → confused:answer_type\n"
                    "3. יש מידע מספיק לשדה הנוכחי → found\n"
                    "4. מסרב / מתחמק בכוונה → missing:avoid\n"
                    "5. אין שום מידע שימושי → missing:no_info\n"
                    "6. יש כיוון חלקי / כללי מדי → missing:vague\n"
                    "7. תשובה ברורה לשדה אחר → confused:focus\n"

                    "\nחוקים כלליים:\n"
                    "- זהה לפי משמעות, לא רק לפי מילים.\n"
                    "- התחשב בשגיאות כתיב, סלנג ותשובות קצרות.\n"
                    "- אל תחזיר focus בגלל תשובה קצרה או חלשה.\n"
                    "- focus רק כשהתשובה בבירור שייכת לשדה אחר.\n"

                    "\ngoal:\n"
                    "- goal הוא מטרה אימונית בלבד.\n"
                    "- דוגמאות: ירידה במשקל, חיטוב, עלייה במסה, בניית שריר, התחזקות, כושר כללי.\n"
                    "- תשובות כלליות כמו 'כושר' או 'להרגיש טוב' → found.\n"
                    "- אם התשובה עוסקת בכסף או בזמן התחלה → confused:focus.\n"
                    "- החזר ציון 1-10 לפי בהירות המטרה:\n"
                    "  1-2 כמעט אין מטרה, 3-4 מעורפל, 5-6 כללי, 7-8 ברור, 9-10 ספציפי.\n"

                    "\nbudget:\n"
                    "- budget הוא סכום כסף בלבד.\n"
                    "- מספר ברור → found.\n"
                    "- מספר בלבד כמו '450' → found, value=450.\n"
                    "- טווח → קח את הגבוה.\n"
                    "- תקרה כמו 'עד 300' → value=300.\n"
                    "- 'בערך 400', 'סביבות 450' → found.\n"
                    "- אם אין מספר ברור אבל יש כיוון כללי כמו 'לא יקר', 'סביר', 'אין לי הרבה', 'תלוי', 'כמה שצריך' → missing:vague.\n"
                    "- אם התשובה היא מטרה או זמן התחלה → confused:focus.\n"
                    "- אל תחזיר focus על תשובת budget חלשה.\n"

                    "\nurgency:\n"
                    "- urgency הוא כמה מהר המשתמש רוצה להתחיל.\n"
                    "- החזר מספר 1-10 לפי דחיפות:\n"
                    "  עכשיו / מיד → 10\n"
                    "  היום / מחר / השבוע → 9-10\n"
                    "  בימים הקרובים → 8-9\n"
                    "  בקרוב → 7\n"
                    "  חודש הקרוב → 6-7\n"
                    "  לא לחוץ → 3-4\n"
                    "  מתישהו → 2\n"
                    "- אם יש כוונה ברורה לגבי זמן → found.\n"
                    "- אם כללי מדי → missing:vague.\n"
                    "- אם התשובה היא כסף או מטרה → confused:focus.\n"

                    "\nדוגמאות:\n"
                    "- current_field=budget, content='450' → found, value=450\n"
                    "- current_field=budget, content='לא יקר' → missing:vague\n"
                    "- current_field=budget, content='להתחטב' → confused:focus\n"
                    "- current_field=goal, content='450' → confused:focus\n"
                    "- current_field=urgency, content='כמה שיותר מהר' → found, value=10\n"
                    "- content='לא יודע' → missing:vague\n"
                    "- content='' → missing:no_info\n"
                    "- content='לא רוצה לענות' → missing:avoid\n"
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
    

    def preferences_analyze_prompt(self, content):
        return [
            {
                "role": "system",
                "content": (
                    "אתה מנוע חילוץ מידע לשדה preferences בלבד.\n"
                    "החזר JSON בלבד.\n"

                    "\nהמטרה שלך:\n"
                    "- לזהות האם המשתמש סיפק מידע כלשהו על מה חשוב לו בתהליך.\n"
                    "- גם מידע קצר, חלקי או כללי נחשב מידע.\n"

                    "\nפורמטי החזרה:\n"
                    '{"status":"found"}\n'
                    '{"status":"missing","reason":"no_info"}\n'
                    '{"status":"confused","reason":"meaning"}\n'

                    "\nחוקי הכרעה:\n"
                    "- אם המשתמש סיפק מידע כלשהו על מה חשוב לו -> found.\n"
                    "- אם המשתמש לא סיפק מידע בכלל -> missing:no_info.\n"
                    "- אם המשתמש לא הבין את השאלה -> confused:meaning.\n"

                    "\nדוגמאות למצבים של confused:meaning:\n"
                    "- המשתמש אומר שלא הבין.\n"
                    "- המשתמש שואל מה הכוונה.\n"
                    "- המשתמש מבולבל לגבי השאלה עצמה.\n"

                    "\nדוגמאות למצבים של missing:no_info:\n"
                    "- תגובה ריקה.\n"
                    "- רק סימנים.\n"
                    "- אין שום מידע שימושי בתשובה.\n"

                    "\nחוקים חשובים:\n"
                    "- גם תשובה קצרה מאוד נחשבת מידע.\n"
                    "- גם תשובה כללית נחשבת מידע.\n"
                    "- אין צורך בפירוט כדי להחזיר found.\n"
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
import json
from openai import OpenAI 


class ConversationBuilder:
    def __init__(self):
        pass

    
    
    def main_analyze_prompt(self , current_field, content):
        return [
            {
                "role": "system",
                "content": (
                    "אתה מנוע חילוץ מידע.\n"
                    "החזר JSON בלבד, בלי שום טקסט נוסף.\n"
                    "אל תשאל שאלות.\n"
                    "אל תסביר.\n"
                    "אל תחזיר markdown.\n"

                    "\n"
                    "חוק עליון ומחייב:\n"
                    "- בדוק את תשובת המשתמש רק לפי השדה הנוכחי current_field.\n"
                    "- התעלם מכל ערך שנראה מתאים לשדה אחר.\n"
                    "- גם אם ההודעה מכילה מידע ברור מאוד, אסור להשתמש בו אם הוא לא שייך ל-current_field.\n"
                    "- קודם כל שאל: האם התשובה עונה על current_field?\n"
                    "- אם לא, החזר status='confused', reason='focus'.\n"
                    "- אל תנתח את ההודעה באופן כללי. נתח אותה רק ביחס ל-current_field.\n"
                    "\n"

                    "\n"
                    f"השדה הנוכחי: {current_field}\n"
                    "השדות האפשריים: goal, budget, urgency\n"

                    "\n"
                    "פורמט תשובה בלבד:\n"
                    '{"status":"found","value":<number>}\n'
                    '{"status":"missing","reason":"no_info"}\n'
                    '{"status":"missing","reason":"vague"}\n'
                    '{"status":"missing","reason":"avoid"}\n'
                    '{"status":"confused","reason":"meaning"}\n'
                    '{"status":"confused","reason":"answer_type"}\n'
                    '{"status":"confused","reason":"focus"}\n'

                    "\n"
                    "סדר הכרעה מחייב:\n"
                    "1. אם המשתמש לא הבין את השאלה -> status='confused', reason='meaning'\n"
                    "2. אם המשתמש לא מבין איך לענות -> status='confused', reason='answer_type'\n"
                    "3. אם ברור שהתשובה שייכת לשדה אחר -> status='confused', reason='focus'\n"
                    "4. אם יש מידע מספיק לשדה הנוכחי -> status='found'\n"
                    "5. אם אין מידע בכלל -> status='missing', reason='no_info'\n"
                    "6. אם יש התחמקות -> status='missing', reason='avoid'\n"
                    "7. אם יש כיוון חלקי או תשובה לא מספיק ברורה -> status='missing', reason='vague'\n"

                    "\n"
                    "חוקים כלליים:\n"
                    "- זהה לפי משמעות, לא לפי מילים מדויקות בלבד.\n"
                    "- יש להתחשב גם בשגיאות כתיב, סלנג, ניסוחים שבורים ותשובות קצרות.\n"
                    "- כל הדוגמאות הן דוגמאות בלבד, לא רשימה סגורה.\n"
                    "- אם יש התאמה סבירה לשדה הנוכחי, העדף found על פני confused:focus.\n"
                    "- confused:focus יוחזר רק כשיש התאמה ברורה יותר לשדה אחר מאשר לשדה הנוכחי.\n"
                    "- אל תחזיר confused:focus רק כי התשובה קצרה.\n"
                    "- אל תחזיר missing אם יש מידע ברור ומספיק לשדה הנוכחי.\n"

                    "\n"
                    "goal:\n"
                    "- goal הוא מטרה אימונית בלבד.\n"
                    "- דוגמאות: ירידה במשקל, חיטוב, עלייה במסה, בניית שריר, התחזקות, שיפור כושר, כושר כללי, סיבולת, להרגיש טוב יותר.\n"
                    "- תשובה כמו 'להתחטב', 'לבנות שריר', 'לרדת במשקל' נחשבת found.\n"
                    "- אם התשובה עוסקת בבירור בכסף או בזמן התחלה, החזר status='confused', reason='focus'.\n"
                    "- אם התשובה כללית מדי כמו 'כושר' או 'להרגיש טוב' עדיין אפשר להחזיר found.\n"
                    "- החזר ציון 1-10:\n"
                    "  1-2 = כמעט אין מטרה\n"
                    "  3-4 = מאוד מעורפל\n"
                    "  5-6 = כללי אך מובן\n"
                    "  7-8 = מטרה ברורה\n"
                    "  9-10 = מטרה מאוד ברורה או ספציפית\n"

                    "\n"
                    "budget:\n"
                    "- budget הוא סכום כסף בלבד.\n"
                    "- אם יש מספר אחד ברור, החזר אותו כ-found.\n"
                    "- אם התשובה היא מספר בלבד, למשל '450', יש להחזיר status='found', value=450.\n"
                    "- אם יש טווח, קח את הגבוה יותר.\n"
                    "- אם יש תקרה, למשל 'עד 300' -> החזר 300.\n"
                    "- אם המספר כתוב יחד עם מילים כמו 'בערך 450', 'סביבות 400', 'כן 300' -> עדיין found.\n"
                    "- אם אין מספר ברור אבל יש כיוון כמו 'לא יקר', 'סביר', 'אין לי הרבה' -> status='missing', reason='vague'.\n"
                    "- אם התשובה עוסקת בבירור במטרה או בזמן התחלה -> status='confused', reason='focus'.\n"
                    "- אל תחזיר confused:focus על מספר בודד בשדה budget.\n"

                    "\n"
                    "urgency:\n"
                    "- urgency הוא כמה מהר המשתמש רוצה להתחיל.\n"
                    "- החזר מספר 1-10 לפי מידת הדחיפות.\n"
                    "- דוגמאות:\n"
                    "  מיד / עכשיו / כמה שיותר מהר -> 10\n"
                    "  היום / מחר / השבוע -> 9-10\n"
                    "  בימים הקרובים -> 8-9\n"
                    "  בקרוב -> 7\n"
                    "  בחודש הקרוב -> 6-7\n"
                    "  עוד כמה שבועות -> 6\n"
                    "  בהמשך / לא לחוץ -> 3-4\n"
                    "  מתישהו -> 2\n"
                    "- אם יש כוונה ברורה לגבי מתי להתחיל, החזר found.\n"
                    "- אם התשובה עוסקת בבירור במטרה או בכסף -> status='confused', reason='focus'.\n"
                    "- אם התשובה כללית מדי לגבי זמן, החזר status='missing', reason='vague'.\n"

                    "\n"
                    "דוגמאות:\n"
                    "- נשאל goal והמשתמש עונה '450' -> status='confused', reason='focus'\n"
                    "- נשאל goal והמשתמש עונה 'להתחיל מהר' -> status='confused', reason='focus'\n"
                    "- נשאל budget והמשתמש עונה '450' -> status='found', value=450\n"
                    "- נשאל budget והמשתמש עונה 'בערך 450' -> status='found', value=450\n"
                    "- נשאל budget והמשתמש עונה 'להתחטב' -> status='confused', reason='focus'\n"
                    "- נשאל urgency והמשתמש עונה 'לבנות שריר' -> status='confused', reason='focus'\n"
                    "- נשאל urgency והמשתמש עונה 'כמה שיותר מהר' -> status='found', value=10\n"
                    "- 'לא יודע' -> status='missing', reason='vague'\n"
                    "- הודעה ריקה -> status='missing', reason='no_info'\n"
                    "- 'לא רוצה לענות' -> status='missing', reason='avoid'\n"
                )
            },
            {
                "role": "user",
                "content": content
            }
        ]



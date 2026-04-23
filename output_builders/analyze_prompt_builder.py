import json
from openai import OpenAI 
from dotenv import load_dotenv
import os
import time

class ConversationBuilder:
    def __init__(self):
        pass

 # ─────────────────────────────────────────
    # SHARED HEADER  (נשלח פעם אחת בכל קריאה)
    # ─────────────────────────────────────────
    _BASE = (
        "אתה מנוע חילוץ מידע.\n"
        "החזר JSON בלבד — בלי טקסט נוסף, בלי markdown.\n"
        "אל תשאל שאלות ואל תסביר.\n"
    )
 
    # ─────────────────────────────────────────
    # פורמטים אפשריים  (תזכורת קצרה למודל)
    # ─────────────────────────────────────────
    _FORMATS = (
        "\n"
        "פורמטי תשובה אפשריים:\n"
        '{"status":"found","value":<number|string>}\n'
        '{"status":"missing","reason":"no_info"}     ← אין מידע כלל\n'
        '{"status":"missing","reason":"vague"}       ← כיוון חלקי, לא מספיק\n'
        '{"status":"missing","reason":"avoid"}       ← מתחמק מלענות\n'
        '{"status":"confused","reason":"meaning"}    ← לא הבין את השאלה\n'
        '{"status":"confused","reason":"answer_type"}← לא יודע איך לענות\n'
        '{"status":"confused","reason":"focus"}      ← ענה על שדה אחר\n'
    )
 
    # ─────────────────────────────────────────
    # סדר הכרעה מחייב  (זהה לכולם)
    # ─────────────────────────────────────────
    _DECISION = (
        "\n"
        "סדר הכרעה (בדוק מלמעלה למטה, עצור בהתאמה הראשונה):\n"
        "1. לא הבין את השאלה         → confused:meaning\n"
        "2. לא יודע איך לענות        → confused:answer_type\n"
        "3. ענה בבירור על שדה אחר   → confused:focus\n"
        "4. יש ערך תקין לשדה הנוכחי → found\n"
        "5. אין מידע כלל             → missing:no_info\n"
        "6. מתחמק                   → missing:avoid\n"
        "7. כיוון חלקי/לא ברור      → missing:vague\n"
        "\n"
        "כלל ברזל: confused:focus רק כאשר ההתאמה לשדה אחר *חזקה יותר* מההתאמה לשדה הנוכחי.\n"
        "אל תחזיר confused:focus רק כי התשובה קצרה.\n"
    )
 
    # ─────────────────────────────────────────
    # הגדרות כל שדה
    # ─────────────────────────────────────────
    _FIELD_PROMPTS = {
 
        # ── GOAL ──────────────────────────────
        "goal": (
            "\n"
            "━━━ שדה: goal (מטרה אימונית) ━━━\n"
            "GOAL הוא מטרה אימונית בלבד.\n"
            "GOAL אינו: סכום כסף, זמן התחלה, מספר טלפון.\n"
            "\n"
            "ערכים תקינים (דוגמאות, לא רשימה סגורה):\n"
            "  ירידה במשקל, חיטוב, עלייה במסה, בניית שריר,\n"
            "  התחזקות, שיפור כושר, כושר כללי, סיבולת,\n"
            "  להרגיש טוב יותר, להתחטב, לבנות שריר.\n"
            "\n"
            "value = ציון 1-10 לפי בהירות המטרה:\n"
            "  1-2  כמעט אין מטרה\n"
            "  3-4  מעורפל מאוד\n"
            "  5-6  כללי אך מובן  (למשל 'כושר', 'להרגיש טוב')\n"
            "  7-8  מטרה ברורה\n"
            "  9-10 מטרה ספציפית מאוד\n"
            "\n"
            "דוגמאות:\n"
            "  'להתחטב'      → found, 8\n"
            "  'כושר'         → found, 5\n"
            "  '450'          → confused:focus  (זה מספר כסף)\n"
            "  'להתחיל מהר'  → confused:focus  (זה זמן)\n"
            "  'לא יודע'      → missing:vague\n"
            "  ''             → missing:no_info\n"
        ),
 
        # ── BUDGET ────────────────────────────
        "budget": (
            "\n"
            "━━━ שדה: budget (תקציב בשקלים) ━━━\n"
            "BUDGET הוא סכום כסף בלבד — מספר שלם.\n"
            "BUDGET אינו: מטרה אימונית, זמן התחלה, מספר טלפון.\n"
            "\n"
            "חוקי חילוץ:\n"
            "  • מספר בודד ('450')                → value=450\n"
            "  • עם מילות עיגון ('בערך 450', 'כן 300', 'סביבות 400') → found, קח את המספר\n"
            "  • תקרה ('עד 300', 'לכל היותר 500')  → found, קח את הגבול העליון\n"
            "  • טווח ('300-500')                  → found, קח את הגבוה (500)\n"
            "  • כיוון ללא מספר ('לא יקר', 'סביר') → missing:vague\n"
            "  • אין מספר כלל                     → missing:no_info\n"
            "\n"
            "⚠️  מספר בודד בשדה budget לעולם לא יהיה confused:focus.\n"
            "\n"
            "דוגמאות:\n"
            "  '450'        → found, 450\n"
            "  'בערך 400'   → found, 400\n"
            "  'עד 300'     → found, 300\n"
            "  '300-500'    → found, 500\n"
            "  'לא יקר'    → missing:vague\n"
            "  'להתחטב'    → confused:focus\n"
            "  'מחר'       → confused:focus\n"
            "  ''          → missing:no_info\n"
        ),
 
        # ── URGENCY ───────────────────────────
        "urgency": (
            "\n"
            "━━━ שדה: urgency (דחיפות התחלה) ━━━\n"
            "URGENCY הוא מתי המשתמש רוצה להתחיל — ציון 1-10.\n"
            "URGENCY אינו: מטרה אימונית, סכום כסף, מספר טלפון.\n"
            "\n"
            "מיפוי ציונים:\n"
            "  מיד / עכשיו / כמה שיותר מהר  → 10\n"
            "  היום / מחר / השבוע            → 9\n"
            "  בימים הקרובים                 → 8\n"
            "  בקרוב                         → 7\n"
            "  בחודש הקרוב                   → 6\n"
            "  עוד כמה שבועות                → 5\n"
            "  בהמשך / לא לחוץ              → 3\n"
            "  מתישהו                        → 2\n"
            "\n"
            "דוגמאות:\n"
            "  'כמה שיותר מהר' → found, 10\n"
            "  'מחר'           → found, 9\n"
            "  'עוד שבועיים'   → found, 5\n"
            "  'בהמשך'         → found, 3\n"
            "  'לא יודע'       → missing:vague\n"
            "  'להתחטב'        → confused:focus\n"
            "  '450'           → confused:focus\n"
            "  ''              → missing:no_info\n"
        ),
 
        # ── PHONE ─────────────────────────────
        "phone": (
            "\n"
            "━━━ שדה: phone (מספר טלפון ישראלי) ━━━\n"
            "PHONE הוא מספר טלפון נייד ישראלי בלבד — 10 ספרות, מתחיל ב-05.\n"
            "PHONE אינו: מטרה אימונית, סכום כסף, זמן התחלה.\n"
            "\n"
            "חוקי חילוץ:\n"
            "  • הסר רווחים, מקפים ותווים מיוחדים (החזר ספרות בלבד).\n"
            "  • דרוש בדיוק 10 ספרות שמתחילות ב-05.\n"
            "  • אל תשלים ספרות חסרות — אין ניחושים.\n"
            "  • כל ערך שלא עומד בתנאים → missing:no_info.\n"
            "\n"
            "value = מחרוזת הספרות בלבד (ללא מקפים/רווחים).\n"
            "\n"
            "דוגמאות:\n"
            "  '050-123-4567'  → found, '0501234567'\n"
            "  '054 987 6543'  → found, '0549876543'\n"
            "  '0541234567'    → found, '0541234567'\n"
            "  '03-1234567'    → missing:no_info\n"
            "  '054123456'     → missing:no_info\n"
            "  'להתחטב'       → missing:no_info\n"
            "  '450'          → missing:no_info\n"
            "  ''             → missing:no_info\n"
            )
    }
    # ─────────────────────────────────────────
    # API  –  build_prompt
    # ─────────────────────────────────────────
    def build_prompt(self, field: str, content: str) -> list[dict]:
        if field not in self._FIELD_PROMPTS:
            raise ValueError(f"Unknown field: {field}")
 
        system_content = (
            self._BASE
            + self._FORMATS
            + self._DECISION
            + self._FIELD_PROMPTS[field]
        )
 
        return [
            {"role": "system", "content": system_content},
            {"role": "user",   "content": content},
        ]
    
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




    def goal_analyze_prompt(self, content):
        return [
            {
                "role": "system",
                "content": (
                    "החזר JSON בלבד.\n"

                    "\n"
                    "פורמט:\n"
                    '{"status":"found","value":<number>}\n'
                    '{"status":"missing","reason":"no_info|vague|avoid"}\n'
                    '{"status":"confused","reason":"meaning|answer_type|focus"}\n'

                    "\n"
                    "goal = מטרה אימונית בלבד (חיטוב, ירידה במשקל, מסה, שריר, כושר וכו').\n"

                    "\n"
                    "סדר:\n"
                    "1. לא הבין -> confused:meaning\n"
                    "2. לא יודע איך לענות -> confused:answer_type\n"
                    "3. ענה על כסף/זמן -> confused:focus\n"
                    "4. יש מטרה -> found\n"
                    "5. ריק -> missing:no_info\n"
                    "6. התחמקות -> missing:avoid\n"
                    "7. כללי מדי -> missing:vague\n"

                    "\n"
                    "דירוג:\n"
                    "1-2 אין מטרה\n"
                    "3-4 מעורפל\n"
                    "5-6 כללי\n"
                    "7-8 ברור\n"
                    "9-10 ספציפי\n"

                    "\n"
                    "חוקים:\n"
                    "- אם יש מילה כמו חיטוב/שריר/מסה -> found\n"
                    "- '450' או זמן -> confused:focus\n"
                    "- 'לא רוצה' -> missing:avoid\n"
                    "- 'לא יודע' -> missing:vague\n"
                )
            },
            {
                "role": "user",
                "content": content
            }
        ]
    

    def budget_analyze_prompt(self, content):
        return [
            {
                "role": "system",
                "content": (
                    "אתה מנוע חילוץ מידע.\n"
                    "החזר JSON בלבד, בלי שום טקסט נוסף.\n"
                    "אל תשאל שאלות.\n"
                    "אל תסביר.\n"

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
                    "3. אם ברור שהתשובה שייכת לשדה אחר (מטרה/זמן) -> status='confused', reason='focus'\n"
                    "4. אם יש סכום כסף ברור -> status='found'\n"
                    "5. אם אין מידע בכלל -> status='missing', reason='no_info'\n"
                    "6. אם יש התחמקות -> status='missing', reason='avoid'\n"
                    "7. אם יש כיוון אבל לא מספר -> status='missing', reason='vague'\n"

                    "\n"
                    "budget:\n"
                    "- budget הוא סכום כסף בלבד.\n"
                    "- אם יש מספר אחד ברור, החזר אותו כ-found.\n"
                    "- אם התשובה היא מספר בלבד, למשל '450', החזר value=450.\n"
                    "- אם יש טווח, קח את הגבוה יותר.\n"
                    "- אם יש תקרה, למשל 'עד 300' -> החזר 300.\n"
                    "- אם המספר כתוב עם מילים כמו 'בערך 450', 'סביבות 400', 'כן 300' -> עדיין found.\n"
                    "- אם אין מספר ברור אבל יש כיוון כמו 'לא יקר', 'סביר', 'אין לי הרבה' -> missing:vague.\n"
                    "- אם התשובה עוסקת במטרה או בזמן התחלה -> confused:focus.\n"
                    "- אל תחזיר confused:focus על מספר בודד.\n"

                    "\n"
                    "דוגמאות:\n"
                    "- '450' -> found, 450\n"
                    "- 'בערך 400' -> found, 400\n"
                    "- 'עד 300' -> found, 300\n"
                    "- 'להתחטב' -> confused, focus\n"
                    "- 'מחר' -> confused, focus\n"
                    "- 'לא יודע' -> missing, vague\n"
                    "- '' -> missing, no_info\n"
                    "- 'לא רוצה לענות' -> missing, avoid\n"
                )
            },
            {
                "role": "user",
                "content": content
            }
        ]


    def phone_analyze(self, content):
            return [
                {
                    "role": "system",
                    "content": (
                        f"המטרה שלך היא לחלץ מספר טלפון מהודעת המשתמש.\n"
                        f"זו הודעת המשתמש:\n"
                        f"{content}\n\n"
                        "חוקים:\n"
                        "- אם יש מספר טלפון ישראלי מלא → החזר status: found\n"
                        "- מספר תקין: מתחיל ב-05 ומכיל 10 ספרות\n"
                        "- הסר רווחים, מקפים או תווים מיוחדים (החזר רק ספרות בלבד)\n"
                        "- אל תנחש ואל תשלים מספרים\n"
                        "- אם אין מספר מלא וברור → החזר status: missing ו-reason: no_info\n\n"
                        "פורמט תשובה:\n\n"
                        "אם נמצא:\n"
                        "{\n"
                        '  "status": "found",\n'
                        '  "value": "PHONE_NUMBER"\n'
                        "}\n\n"
                        "אם לא נמצא:\n"
                        "{\n"
                        '  "status": "missing",\n'
                        '  "reason": "no_info"\n'
                        "}"
                    )
                }
            ]
    


    def urgency_analyze_prompt(self, content):
        return [
            {
                "role": "system",
                "content": (
                    "אתה מנוע חילוץ מידע.\n"
                    "החזר JSON בלבד, בלי שום טקסט נוסף.\n"
                    "אל תשאל שאלות.\n"
                    "אל תסביר.\n"

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
                    "3. אם ברור שהתשובה שייכת לשדה אחר (מטרה/כסף) -> status='confused', reason='focus'\n"
                    "4. אם יש כוונה ברורה לגבי זמן התחלה -> status='found'\n"
                    "5. אם אין מידע בכלל -> status='missing', reason='no_info'\n"
                    "6. אם יש התחמקות -> status='missing', reason='avoid'\n"
                    "7. אם התשובה כללית מדי לגבי זמן -> status='missing', reason='vague'\n"

                    "\n"
                    "urgency:\n"
                    "- urgency הוא כמה מהר המשתמש רוצה להתחיל.\n"
                    "- החזר מספר 1-10 לפי מידת הדחיפות.\n"

                    "\n"
                    "מיפוי:\n"
                    "מיד / עכשיו / כמה שיותר מהר -> 10\n"
                    "היום / מחר / השבוע -> 9-10\n"
                    "בימים הקרובים -> 8-9\n"
                    "בקרוב -> 7\n"
                    "בחודש הקרוב -> 6-7\n"
                    "עוד כמה שבועות -> 6\n"
                    "בהמשך / לא לחוץ -> 3-4\n"
                    "מתישהו -> 2\n"

                    "\n"
                    "חוקים:\n"
                    "- אם יש זמן התחלה ברור -> status='found'\n"
                    "- אם התשובה עוסקת במטרה או כסף -> status='confused', reason='focus'\n"
                    "- אם אין זמן ברור -> status='missing', reason='vague'\n"

                    "\n"
                    "דוגמאות:\n"
                    "- 'כמה שיותר מהר' -> found, 10\n"
                    "- 'מחר' -> found, 9\n"
                    "- 'עוד שבועיים' -> found, 6\n"
                    "- 'להתחטב' -> confused, focus\n"
                    "- '450' -> confused, focus\n"
                    "- 'לא יודע' -> missing, vague\n"
                    "- '' -> missing, no_info\n"
                    "- 'לא רוצה לענות' -> missing, avoid\n"
                )
            },
            {
                "role": "user",
                "content": content
            }
        ]


    def build_prompt_second(self , field , content):
        if field == "goal":
            prompt = self.goal_analyze_prompt(content=content)

        elif field == "budget":
            prompt = self.budget_analyze_prompt(content=content)

        elif field == "phone":
            prompt = self.phone_analyze(content=content)

        elif field == "urgency":
            prompt = self.urgency_analyze_prompt(content=content)

        return prompt
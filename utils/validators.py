def validate_int(value, name):  
    if value is None:
        raise ValueError(f"לא הוזן {name}")
    if not isinstance(value, int):
        raise TypeError(f"{name} צריך להיות מספר שלם")
    if value < 0:
        raise ValueError(f"{name} לא יכול להיות שלילי")


def validate_str(value, name, allow_empty=False):
    if value is None:
        raise ValueError(f"לא הוזן {name}")
    if not isinstance(value, str):
        raise TypeError(f"{name} צריך להיות טקסט")
    if not allow_empty and not value.strip():
        raise ValueError(f"{name} לא יכול להיות ריק")


def validate_phone_number(phone_number, allow_empty=False):
    if phone_number is None:
        raise ValueError("לא הוזן מספר טלפון")
    
    if not isinstance(phone_number, str):
        raise TypeError("מספר טלפון לא תקין")

    phone_number = phone_number.strip()

    if not allow_empty and not phone_number:
        raise ValueError("מספר טלפון לא יכול להיות ריק")

    if not phone_number.isdigit():
        raise ValueError("מספר טלפון חייב להכיל רק ספרות")

    if not phone_number.startswith("05"):
        raise ValueError("מספר טלפון חייב להתחיל ב־05")

    if len(phone_number) != 10:
        raise ValueError("מספר טלפון לא תקין")
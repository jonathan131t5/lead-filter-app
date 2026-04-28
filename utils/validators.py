import re


class UserError(Exception):
    pass



def validate_int(value, name):  
    if value is None:
        raise UserError(f"לא הוזן {name}")
    if not isinstance(value, int):
        raise UserError(f"{name} צריך להיות מספר שלם")
    if value < 0:
        raise UserError(f"{name} לא יכול להיות שלילי")


def validate_str(value, name, allow_empty=False):
    if value is None:
        raise UserError(f"לא הוזן {name}")
    if not isinstance(value, str):
        raise UserError(f"{name} צריך להיות טקסט")
    if not allow_empty and not value.strip():
        raise UserError(f"{name} לא יכול להיות ריק")


#
    


def extract_phone(content: str):
    match = re.search(r"(?<!\d)05(?:[\s-]?\d){8}(?!\d)", content)

    if match:
        digits = re.sub(r"\D", "", match.group())
        return {
            "status": "found",
            "value": digits
        }

    if re.search(r"\d", content):
        return {
            "status": "missing",
            "reason": "invalid_format"
        }

    return {
        "status": "missing",
        "reason": "no_info"
    }
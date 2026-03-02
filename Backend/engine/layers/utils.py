from typing import Optional

import phonenumbers


def normalize_phone_number(phone_number: str, region: str = "US") -> Optional[str]:
    sanitized = "".join(ch for ch in phone_number.strip() if ch.isdigit() or ch == "+")

    try:
        parsed = phonenumbers.parse(sanitized, region)
        if not phonenumbers.is_valid_number(parsed):
            if sanitized.startswith("+") and sanitized[1:].isdigit() and 8 <= len(sanitized[1:]) <= 15:
                return sanitized
            return None
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        if sanitized.startswith("+") and sanitized[1:].isdigit() and 8 <= len(sanitized[1:]) <= 15:
            return sanitized
        return None

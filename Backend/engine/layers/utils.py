from typing import Optional

import phonenumbers


def normalize_phone_number(phone_number: str, region: str = "US") -> Optional[str]:
    try:
        parsed = phonenumbers.parse(phone_number, region)
        if not phonenumbers.is_valid_number(parsed):
            return None
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except Exception:
        return None

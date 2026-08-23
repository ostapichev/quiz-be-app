import phonenumbers


def normalize_phone_number(raw: str) -> str:
    try:
        parsed = phonenumbers.parse(raw, None)
    except phonenumbers.NumberParseException:
        raise ValueError(
            "Invalid phone number format. "
            "Use international format, e.g. +380501234567"
        )

    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Phone number is not a valid, existing number")

    return phonenumbers.format_number(
        parsed,
        phonenumbers.PhoneNumberFormat.E164,
    )


def valid_test_phone_number(seq: int) -> str:
    raw = f"+1201555{seq:04d}"
    parsed = phonenumbers.parse(raw, None)

    return phonenumbers.format_number(
        parsed,
        phonenumbers.PhoneNumberFormat.E164,
    )

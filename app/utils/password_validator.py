def password_validator(raw: str | None) -> str:
    if not raw or len(raw) < 8:
        raise ValueError("Password must be at least 8 characters long")
    return raw

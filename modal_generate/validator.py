def keep_warm_validator(value: str):
    if not isinstance(value, str):
        return "Value is not a string"

    if not value.isdigit() and value.lower() not in {"yes", "y", "no", "n"}:
        return "Value is not a number, (Y)es or (N)o."

    else:
        return True

import re


def classify(value: str):
    sanitized_string = re.sub(r'[^a-zA-Z0-9\s]', '', value)
    title = sanitized_string.title()
    cleaned_string = title.strip(' _')
    if cleaned_string and not cleaned_string[0].isalpha():
        cleaned_string = 'Class' + cleaned_string
    return cleaned_string

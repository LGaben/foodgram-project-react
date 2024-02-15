from django.core.validators import RegexValidator


def validate_username(username: str):
    regex_validator = RegexValidator(
        regex=r'^[\w.@+-]+\Z',
        message='Только буквы, цифры и @/./+/-/_')
    regex_validator(username)

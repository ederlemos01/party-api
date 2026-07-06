from django.core.validators import RegexValidator

username_validator = RegexValidator(r'^[a-zA-Z0-9_]{3,15}$', 'Username invalido')
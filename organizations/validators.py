from django.core.exceptions import ValidationError
import re

def validate_slug(value):
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', value):
        raise ValidationError(
            'O slug deve conter apenas minúsculas, números e hífens, '
            'sem hífens no início/fim ou repetidos.',
            code='invalid_slug',
        )
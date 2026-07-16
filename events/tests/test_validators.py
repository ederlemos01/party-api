import pytest
from django.core.exceptions import ValidationError

from events.validators import validate_slug


class TestValidateSlug:
    @pytest.mark.parametrize('slug', [
        'ab',
        'a1',
        '42',
        'meu-slug',
        'a-b-c',
        'festa-2026',
        'a',  # tamanho mínimo é responsabilidade do MinLengthValidator, não do formato
    ])
    def test_formatos_validos_passam(self, slug):
        validate_slug(slug)

    @pytest.mark.parametrize('slug', [
        'Foo',    # maiúscula
        '-abc',   # hífen no início
        'abc-',   # hífen no fim
        'a--b',   # hífen repetido
        'a_b',    # underscore
        'café',   # acento
        'a b',    # espaço
        '',       # vazio
    ])
    def test_formatos_invalidos_falham(self, slug):
        with pytest.raises(ValidationError):
            validate_slug(slug)

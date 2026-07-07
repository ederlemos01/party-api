import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from users.models import User


@pytest.mark.django_db
class TestUserManager:

    def test_create_user_normaliza_email_com_strip_e_lower(self):
        user = User.objects.create_user(
            email='  Teste@EMAIL.Com  ',
            username='usuario1',
            password='S3nha-F0rte!2026',
        )
        assert user.email == 'teste@email.com'

    def test_create_user_sem_email_levanta_value_error(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email='', username='usuario1', password='x')

    def test_create_user_sem_username_levanta_value_error(self):
        with pytest.raises(ValueError):
            User.objects.create_user(email='a@b.com', username='', password='x')

    def test_create_user_define_senha_com_hash(self):
        user = User.objects.create_user(
            email='hash@exemplo.com',
            username='usuario2',
            password='S3nha-F0rte!2026',
        )
        assert user.password != 'S3nha-F0rte!2026'
        assert user.check_password('S3nha-F0rte!2026')

    def test_create_superuser_define_flags_por_padrao(self):
        admin = User.objects.create_superuser(
            email='admin@exemplo.com',
            username='admin1',
            password='S3nha-F0rte!2026',
        )
        assert admin.is_staff is True
        assert admin.is_superuser is True

    def test_create_superuser_com_is_staff_false_levanta_value_error(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email='admin@exemplo.com',
                username='admin1',
                password='S3nha-F0rte!2026',
                is_staff=False,
            )

    def test_create_superuser_com_is_superuser_false_levanta_value_error(self):
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email='admin@exemplo.com',
                username='admin1',
                password='S3nha-F0rte!2026',
                is_superuser=False,
            )


@pytest.mark.django_db
class TestUserConstraints:

    def test_email_unico_case_insensitive_no_banco(self):
     
        first = User(email='Teste@Email.com', username='usuario1')
        first.set_password('S3nha-F0rte!2026')
        first.save()
        User.objects.filter(id=first.id).update(email='Caso@X.com')

        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email='caso@x.com',
                username='usuario2',
                password='S3nha-F0rte!2026',
            )

    def test_username_unico_case_insensitive_no_banco(self):
        User.objects.create_user(
            email='um@exemplo.com',
            username='Usuario',
            password='S3nha-F0rte!2026',
        )
        with pytest.raises(IntegrityError):
            User.objects.create_user(
                email='dois@exemplo.com',
                username='usuario',
                password='S3nha-F0rte!2026',
            )


@pytest.mark.django_db
class TestUsernameValidation:

    def test_username_valido_passa_no_full_clean(self):
        user = User.objects.create_user(
            email='ok@exemplo.com',
            username='user_ok1',
            password='S3nha-F0rte!2026',
        )
        user.full_clean()  # nao deve levantar erro

    @pytest.mark.parametrize('username_invalido', [
        'ab',            # menos de 3 caracteres
        'user name',     # espaco
        'user-name',     # hifen (caractere especial)
        'user@name',     # arroba
        'usuário',       # acento
    ])
    def test_username_invalido_levanta_validation_error(self, username_invalido):
        user = User(
            email='invalido@exemplo.com',
            username=username_invalido,
        )
        user.set_password('S3nha-F0rte!2026')
        with pytest.raises(ValidationError) as exc_info:
            user.full_clean()
        assert 'username' in exc_info.value.error_dict

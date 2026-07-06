import pytest
from django.urls import reverse
from rest_framework import status

from users.models import User

REGISTER_URL = reverse('register')


@pytest.mark.django_db
class TestRegisterViewSucesso:

    def test_registro_valido_retorna_201(self, api_client, valid_register_payload):
        response = api_client.post(REGISTER_URL, valid_register_payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='novo@exemplo.com').exists()

    def test_password_nao_aparece_na_resposta(self, api_client, valid_register_payload):
        response = api_client.post(REGISTER_URL, valid_register_payload)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'password' not in response.data

    def test_senha_persistida_com_hash(self, api_client, valid_register_payload):
        api_client.post(REGISTER_URL, valid_register_payload)

        user = User.objects.get(email='novo@exemplo.com')
        assert user.password != valid_register_payload['password']
        assert user.check_password(valid_register_payload['password'])


@pytest.mark.django_db
class TestRegisterViewSenhaFraca:

    def test_senha_fraca_retorna_400(self, api_client, valid_register_payload):
        valid_register_payload['password'] = '123'
        response = api_client.post(REGISTER_URL, valid_register_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
        assert not User.objects.filter(email='novo@exemplo.com').exists()

    def test_senha_igual_ao_username_retorna_400(self, api_client, valid_register_payload):
        # UserAttributeSimilarityValidator deve barrar senha parecida com username
        valid_register_payload['username'] = 'novousuario'
        valid_register_payload['password'] = 'novousuario'
        response = api_client.post(REGISTER_URL, valid_register_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data


@pytest.mark.django_db
class TestRegisterViewDuplicados:

    def test_email_ja_existente_retorna_400(self, api_client, existing_user):
        response = api_client.post(REGISTER_URL, {
            'email': existing_user.email,
            'username': 'outro_user',
            'password': 'S3nha-F0rte!2026',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_username_ja_existente_retorna_400(self, api_client, existing_user):
        response = api_client.post(REGISTER_URL, {
            'email': 'outro@exemplo.com',
            'username': existing_user.username,
            'password': 'S3nha-F0rte!2026',
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data
        assert User.objects.count() == 1


@pytest.mark.django_db
class TestRegisterViewCaseInsensitive:

    def test_email_duplicado_com_caixa_diferente_retorna_400(self, api_client, existing_user):
        response = api_client.post(REGISTER_URL, {
              'email': 'EXISTENTE@Exemplo.COM',
              'username': 'outro_user',
              'password': 'S3nha-F0rte!2026',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_username_duplicado_com_caixa_diferente_retorna_400(self, api_client, existing_user):
        response = api_client.post(REGISTER_URL, {
            'email': 'outro@exemplo.com',
            'username': 'EXISTENTE',
            'password': 'S3nha-F0rte!2026',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data

    def test_username_invalido_retorna_400(self, api_client, valid_register_payload):
        valid_register_payload['username'] = 'user name'
        response = api_client.post(REGISTER_URL, valid_register_payload)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'username' in response.data

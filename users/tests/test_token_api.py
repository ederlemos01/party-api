import pytest
from django.urls import reverse
from rest_framework import status

from users.models import User

TOKEN_URL = reverse('token_obtain_pair')
REFRESH_URL = reverse('token_refresh')

SENHA = 'S3nha-F0rte!2026'


@pytest.mark.django_db
class TestTokenObtainSucesso:

    def test_credenciais_validas_retornam_par_de_tokens(self, api_client, existing_user):
        response = api_client.post(TOKEN_URL, {
            'email': existing_user.email,
            'password': SENHA,
        })

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data

    def test_login_com_email_em_caixa_diferente_funciona(self, api_client, existing_user):
        response = api_client.post(TOKEN_URL, {
            'email': 'EXISTENTE@Exemplo.COM',
            'password': SENHA,
        })

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_login_funciona_com_email_gravado_fora_do_manager(self, api_client):
      
        user = User(email='Fulano@Exemplo.com', username='fulano_1')
        user.set_password(SENHA)
        user.save()

        response = api_client.post(TOKEN_URL, {
            'email': 'Fulano@Exemplo.com',
            'password': SENHA,
        })

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestTokenObtainFalha:

    def test_senha_errada_retorna_401(self, api_client, existing_user):
        response = api_client.post(TOKEN_URL, {
            'email': existing_user.email,
            'password': 'senha-errada',
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_senha_eh_case_sensitive(self, api_client, existing_user):
        # Email eh case-insensitive, senha nao: caixa diferente deve falhar.
        response = api_client.post(TOKEN_URL, {
            'email': existing_user.email,
            'password': SENHA.lower(),
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_email_inexistente_retorna_401(self, api_client):
        response = api_client.post(TOKEN_URL, {
            'email': 'nao-existe@exemplo.com',
            'password': SENHA,
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_erro_nao_revela_se_o_email_existe(self, api_client, existing_user):
        # Anti-enumeracao: senha errada e conta inexistente devem produzir
        # exatamente a mesma resposta.
        senha_errada = api_client.post(TOKEN_URL, {
            'email': existing_user.email,
            'password': 'senha-errada',
        })
        conta_inexistente = api_client.post(TOKEN_URL, {
            'email': 'nao-existe@exemplo.com',
            'password': 'senha-errada',
        })

        assert senha_errada.status_code == status.HTTP_401_UNAUTHORIZED
        assert conta_inexistente.status_code == status.HTTP_401_UNAUTHORIZED
        assert senha_errada.data == conta_inexistente.data

    def test_usuario_inativo_retorna_401(self, api_client, existing_user):
        existing_user.is_active = False
        existing_user.save()

        response = api_client.post(TOKEN_URL, {
            'email': existing_user.email,
            'password': SENHA,
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRefresh:

    def test_refresh_valido_emite_novo_access(self, api_client, existing_user):
        tokens = api_client.post(TOKEN_URL, {
            'email': existing_user.email,
            'password': SENHA,
        }).data

        response = api_client.post(REFRESH_URL, {'refresh': tokens['refresh']})

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data

    def test_refresh_invalido_retorna_401(self, api_client):
        response = api_client.post(REFRESH_URL, {'refresh': 'token-invalido'})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

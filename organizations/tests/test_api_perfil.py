import pytest
from django.urls import reverse
from rest_framework import status

pytestmark = pytest.mark.django_db


def perfil_url(slug):
    return reverse('organization-profile', kwargs={'org_slug': slug})


class TestPerfilPublico:
    def test_anonimo_retorna_200(self, api_client, organization):
        response = api_client.get(perfil_url(organization.slug))

        assert response.status_code == status.HTTP_200_OK

    def test_retorna_somente_campos_publicos(self, api_client, organization):
        response = api_client.get(perfil_url(organization.slug))

        assert set(response.data) == {
            'id', 'name', 'description', 'photo', 'banner', 'slug'
        }
        assert response.data['slug'] == 'noite-baixa'
        assert response.data['name'] == 'Coletivo Noite Baixa'

    def test_org_inexistente_retorna_404(self, api_client):
        response = api_client.get(perfil_url('nao-existe'))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_org_soft_deletada_retorna_404(self, api_client, organization):
        organization.delete()

        response = api_client.get(perfil_url(organization.slug))

        assert response.status_code == status.HTTP_404_NOT_FOUND

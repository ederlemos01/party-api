import pytest
from django.urls import reverse
from rest_framework import status

from events.models import EventStatus

pytestmark = pytest.mark.django_db


def perfil_url(org_slug, event_slug):
    return reverse('event-perfil', kwargs={'org_slug': org_slug, 'event_slug': event_slug})


class TestPerfilPublicado:
    def test_anonimo_retorna_200(self, api_client, organization, evento_publicado):
        response = api_client.get(
            perfil_url(organization.slug, evento_publicado.slug)
        )

        assert response.status_code == status.HTTP_200_OK

    def test_retorna_somente_campos_publicos(
        self, api_client, organization, evento_publicado
    ):
        response = api_client.get(
            perfil_url(organization.slug, evento_publicado.slug)
        )

        assert set(response.data) == {
            'id', 'title', 'description', 'banner', 'start_at', 'end_at',
            'location', 'slug', 'organization',
        }
        assert response.data['slug'] == 'noite-baixa-vol-1'
        assert response.data['title'] == 'Noite Baixa Vol. 1'


class TestPerfilNaoPublicado:
    @pytest.mark.parametrize('status_evento', [
        EventStatus.DRAFT,
        EventStatus.FINISHED,
        EventStatus.CANCELED,
    ])
    def test_evento_nao_publicado_retorna_404(
        self, api_client, organization, criar_evento, status_evento
    ):
        """O perfil público só existe enquanto o evento está published."""
        evento = criar_evento(organization, status=status_evento)

        response = api_client.get(perfil_url(organization.slug, evento.slug))

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPerfilNaoEncontrado:
    def test_evento_inexistente_retorna_404(self, api_client, organization):
        response = api_client.get(perfil_url(organization.slug, 'nao-existe'))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_evento_soft_deletado_retorna_404(
        self, api_client, organization, evento_publicado
    ):
        evento_publicado.delete()

        response = api_client.get(
            perfil_url(organization.slug, evento_publicado.slug)
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_org_soft_deletada_retorna_404(
        self, api_client, organization, evento_publicado
    ):
        """Org deletada leva o perfil dos eventos junto, mesmo que o evento
        em si continue ativo."""
        organization.delete()

        response = api_client.get(
            perfil_url(organization.slug, evento_publicado.slug)
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_evento_de_outra_org_no_path_retorna_404(
        self, api_client, outra_organization, evento_publicado
    ):
        """O slug do evento só resolve dentro da org que está no path."""
        response = api_client.get(
            perfil_url(outra_organization.slug, evento_publicado.slug)
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

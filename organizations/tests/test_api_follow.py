import pytest
from django.db import IntegrityError
from django.urls import reverse
from rest_framework import status

from organizations.models import OrganizationFollow

pytestmark = pytest.mark.django_db


def follow_url(slug):
    return reverse('organization-follow', kwargs={'org_slug': slug})


class TestFollowAutenticacao:
    def test_post_anonimo_retorna_401(self, api_client, organization):
        response = api_client.post(follow_url(organization.slug))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_delete_anonimo_retorna_401(self, api_client, organization):
        response = api_client.delete(follow_url(organization.slug))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestSeguir:
    def test_seguir_retorna_201_e_cria_follow(self, auth_client, seguidor, organization):
        response = auth_client.post(follow_url(organization.slug))

        assert response.status_code == status.HTTP_201_CREATED
        assert OrganizationFollow.objects.filter(
            user=seguidor, organization=organization
        ).exists()

    def test_seguir_de_novo_e_idempotente(self, auth_client, organization, follow):
        """O contrato é idempotente: seguir quem já se segue não é erro
        (double-click, retry de rede móvel) e não pode duplicar linha."""
        response = auth_client.post(follow_url(organization.slug))

        assert response.status_code == status.HTTP_201_CREATED
        assert OrganizationFollow.all_objects.count() == 1

    def test_seguir_org_inexistente_retorna_404(self, auth_client):
        response = auth_client.post(follow_url('nao-existe'))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_seguir_org_soft_deletada_retorna_404(self, auth_client, organization):
        """A view usa o manager de vivas: org soft-deletada não pode ganhar
        seguidores novos."""
        organization.delete()

        response = auth_client.post(follow_url(organization.slug))

        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeixarDeSeguir:
    def test_unfollow_retorna_204_e_soft_deleta(self, auth_client, organization, follow):
        response = auth_client.delete(follow_url(organization.slug))

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert OrganizationFollow.objects.count() == 0
        assert OrganizationFollow.all_objects.dead().count() == 1

    def test_unfollow_sem_seguir_retorna_404(self, auth_client, organization):
        response = auth_client.delete(follow_url(organization.slug))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unfollow_nao_afeta_outros_seguidores(
        self, auth_client, organization, follow, criar_usuario
    ):
        outro = criar_usuario()
        outro_follow = OrganizationFollow.objects.create(
            user=outro, organization=organization
        )

        auth_client.delete(follow_url(organization.slug))

        outro_follow.refresh_from_db()
        assert not outro_follow.is_deleted


class TestReseguir:
    def test_reseguir_restaura_a_mesma_linha(self, auth_client, organization, follow):
        """Unfollow + follow de novo não cria linha nova: o update_or_create
        revive a existente, preservando o created_at do primeiro follow."""
        created_at_original = follow.created_at
        auth_client.delete(follow_url(organization.slug))

        response = auth_client.post(follow_url(organization.slug))

        assert response.status_code == status.HTTP_201_CREATED
        assert OrganizationFollow.all_objects.count() == 1
        follow.refresh_from_db()
        assert not follow.is_deleted
        assert follow.created_at == created_at_original


class TestInvarianteDeUnicidade:
    """A constraint agora é total (sem condition): o banco garante no máximo
    uma linha por (user, organization), viva OU morta — o invariante que o
    update_or_create da view assume."""

    def test_banco_rejeita_duplicata_com_linha_viva(
        self, seguidor, organization, follow
    ):
        with pytest.raises(IntegrityError):
            OrganizationFollow.objects.create(
                user=seguidor, organization=organization
            )

    def test_banco_rejeita_duplicata_mesmo_com_linha_morta(
        self, seguidor, organization, follow
    ):
        follow.delete()  # soft delete: a linha continua existindo no banco

        with pytest.raises(IntegrityError):
            OrganizationFollow.objects.create(
                user=seguidor, organization=organization
            )

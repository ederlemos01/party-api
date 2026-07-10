import pytest
from django.db import IntegrityError

from organizations.models import Organization, OrganizationFollow

pytestmark = pytest.mark.django_db


class TestSoftDeleteInstancia:
    def test_delete_marca_em_vez_de_apagar(self, organization):
        organization.delete()

        assert organization.deleted_at is not None
        assert organization.is_deleted
        assert Organization.all_objects.count() == 1

    def test_delete_atualiza_updated_at(self, organization):
        antes = organization.updated_at

        organization.delete()
        organization.refresh_from_db()

        assert organization.updated_at > antes

    def test_restore_ressuscita(self, organization):
        organization.delete()

        organization.restore()

        assert not organization.is_deleted
        assert Organization.objects.count() == 1

    def test_hard_delete_apaga_de_verdade(self, organization):
        organization.hard_delete()

        assert Organization.all_objects.count() == 0


class TestManagers:
    def test_objects_esconde_deletados(self, organization):
        organization.delete()

        assert Organization.objects.count() == 0
        assert Organization.all_objects.count() == 1
        assert Organization.all_objects.dead().count() == 1

    def test_delete_em_massa_via_queryset_marca(self, organization):
        Organization.objects.all().delete()

        assert Organization.objects.count() == 0
        assert Organization.all_objects.dead().count() == 1

    def test_restore_em_massa_via_queryset(self, organization):
        Organization.objects.all().delete()

        Organization.all_objects.dead().restore()

        assert Organization.objects.count() == 1


class TestRelacoes:
    def test_fk_para_frente_alcanca_pai_deletado(self, follow, organization):
        """O base manager não filtra: seguir a FK de um filho vivo até um pai
        soft-deletado não pode estourar DoesNotExist."""
        organization.delete()

        follow_recarregado = OrganizationFollow.objects.get(pk=follow.pk)

        assert follow_recarregado.organization == organization

    def test_relacao_reversa_esconde_filhos_deletados(self, follow, organization):
        follow.delete()

        assert organization.follows.count() == 0


class TestUnicidadeCondicional:
    def test_slug_repetido_entre_vivas_falha(self, organization, criar_usuario):
        """Owner distinto: garante que o IntegrityError vem da constraint de
        slug, e não da unicidade da FK + constraint condicional."""
        with pytest.raises(IntegrityError):
            Organization.objects.create(
                name='Outra', slug='noite-baixa', owner=criar_usuario()
            )

    def test_soft_delete_libera_o_slug(self, organization, criar_usuario):
        organization.delete()

        nova = Organization.objects.create(
            name='Nova Noite Baixa', slug='noite-baixa', owner=criar_usuario()
        )

        assert nova.slug == organization.slug

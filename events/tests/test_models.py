from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from events.models import Event

pytestmark = pytest.mark.django_db


class TestSlugUnicoPorOrg:
    def test_mesmo_slug_na_mesma_org_ativa_falha(self, criar_evento, organization):
        criar_evento(organization, slug='festa')

        with pytest.raises(IntegrityError):
            criar_evento(organization, slug='festa')

    def test_mesmo_slug_em_orgs_diferentes_passa(
        self, criar_evento, organization, outra_organization
    ):
        """A unicidade é por (slug, organization): o slug só precisa ser
        único dentro da própria org."""
        criar_evento(organization, slug='festa')

        evento = criar_evento(outra_organization, slug='festa')

        assert evento.slug == 'festa'

    def test_soft_delete_libera_o_slug_na_mesma_org(self, criar_evento, organization):
        """A constraint é parcial (deleted_at__isnull=True): evento deletado
        sai do índice e o slug volta a ficar disponível."""
        antigo = criar_evento(organization, slug='festa')
        antigo.delete()

        novo = criar_evento(organization, slug='festa')

        assert novo.slug == 'festa'


class TestFimDepoisDoInicio:
    @pytest.mark.parametrize('deslocamento', [
        timedelta(0),         # end_at igual ao start_at
        timedelta(hours=-1),  # end_at antes do start_at
    ])
    def test_end_at_nao_posterior_ao_start_at_falha(
        self, criar_evento, organization, deslocamento
    ):
        """event_end_after_start exige end_at estritamente maior (gt):
        terminar no mesmo instante em que começa também é inválido."""
        inicio = timezone.now() + timedelta(days=7)

        with pytest.raises(IntegrityError):
            criar_evento(
                organization, start_at=inicio, end_at=inicio + deslocamento
            )


class TestProtecaoDaOrganizacao:
    def test_hard_delete_da_org_com_evento_falha(self, criar_evento, organization):
        """on_delete=PROTECT: org com eventos só sai via soft delete; apagar
        a linha de verdade derrubaria o histórico de eventos junto."""
        criar_evento(organization)

        with pytest.raises(ProtectedError):
            organization.hard_delete()


class TestSoftDelete:
    def test_objects_esconde_deletados_e_all_objects_enxerga(
        self, criar_evento, organization
    ):
        evento = criar_evento(organization)
        evento.delete()

        assert evento.is_deleted
        assert Event.objects.count() == 0
        assert Event.all_objects.count() == 1
        assert Event.all_objects.dead().count() == 1

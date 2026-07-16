from datetime import timedelta
from types import SimpleNamespace

import pytest

from events.serializers import CreateEventSerializer

pytestmark = pytest.mark.django_db


def serializer_para(user, data):
    """O validate() lê request.user do contexto para descobrir a org do
    usuário; um objeto simples com .user basta, sem request DRF de verdade."""
    return CreateEventSerializer(
        data=data, context={'request': SimpleNamespace(user=user)}
    )


class TestDatas:
    @pytest.mark.parametrize('deslocamento', [
        timedelta(0),         # end_at igual ao start_at
        timedelta(hours=-1),  # end_at antes do start_at
    ])
    def test_end_at_nao_posterior_ao_start_at_invalido(
        self, owner, organization, payload_evento, deslocamento
    ):
        """Espelha a check constraint event_end_after_start do banco, com o
        erro apontando para end_at."""
        payload_evento['end_at'] = payload_evento['start_at'] + deslocamento

        serializer = serializer_para(owner, payload_evento)

        assert not serializer.is_valid()
        assert 'end_at' in serializer.errors


class TestOrganizacaoDoUsuario:
    def test_usuario_sem_org_invalido(self, owner, payload_evento):
        """Sem a fixture organization, o dono não tem nenhuma org ativa."""
        serializer = serializer_para(owner, payload_evento)

        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors

    def test_org_soft_deletada_nao_conta(self, owner, organization, payload_evento):
        """owned_organizations usa o manager de vivas: org soft-deletada não
        habilita o dono a criar eventos."""
        organization.delete()

        serializer = serializer_para(owner, payload_evento)

        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors


class TestSlugDisponibilidade:
    def test_slug_de_evento_ativo_da_org_invalido(
        self, owner, organization, criar_evento, payload_evento
    ):
        criar_evento(organization, slug='festa-lancamento')

        serializer = serializer_para(owner, payload_evento)

        assert not serializer.is_valid()
        assert 'slug' in serializer.errors

    def test_slug_de_evento_soft_deletado_e_reutilizavel(
        self, owner, organization, criar_evento, payload_evento
    ):
        """Espelha a constraint parcial do banco: slug de evento deletado
        volta a ficar disponível na org."""
        evento = criar_evento(organization, slug='festa-lancamento')
        evento.delete()

        serializer = serializer_para(owner, payload_evento)

        assert serializer.is_valid(), serializer.errors

    def test_slug_em_uso_por_outra_org_nao_bloqueia(
        self, owner, organization, outra_organization, criar_evento, payload_evento
    ):
        """A checagem é escopada à org do usuário, como a constraint."""
        criar_evento(outra_organization, slug='festa-lancamento')

        serializer = serializer_para(owner, payload_evento)

        assert serializer.is_valid(), serializer.errors


class TestSlugFormato:
    def test_slug_curto_demais_invalido(self, owner, organization, payload_evento):
        payload_evento['slug'] = 'a'

        serializer = serializer_para(owner, payload_evento)

        assert not serializer.is_valid()
        assert 'slug' in serializer.errors

    def test_formato_do_modelo_vale_no_serializer(
        self, owner, organization, payload_evento
    ):
        """Campo redeclarado não herda validadores do modelo: garante que
        validate_slug foi ligado explicitamente no serializer (underscore
        passa no SlugField do DRF, mas não no nosso formato)."""
        payload_evento['slug'] = 'meu_slug'

        serializer = serializer_para(owner, payload_evento)

        assert not serializer.is_valid()
        assert 'slug' in serializer.errors

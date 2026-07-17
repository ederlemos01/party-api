import pytest

from organizations.serializers import OrganizationEditProfileSerializer

pytestmark = pytest.mark.django_db


class TestEditSerializerSlugUnico:
    def test_slug_em_uso_por_org_ativa_invalido(self, organization):
        serializer = OrganizationEditProfileSerializer(data={'slug': 'noite-baixa'})

        assert not serializer.is_valid()
        assert 'slug' in serializer.errors

    def test_slug_de_org_soft_deletada_e_reutilizavel(self, organization):
        """O UniqueValidator usa o manager de vivas, espelhando a constraint
        parcial do banco: slug de org deletada volta a ficar disponível."""
        organization.delete()

        serializer = OrganizationEditProfileSerializer(data={'slug': 'noite-baixa'})

        assert serializer.is_valid(), serializer.errors

    def test_update_pode_manter_o_proprio_slug(self, organization):
        """O UniqueValidator exclui a própria instância no update — senão
        salvar o perfil sem trocar o slug viraria erro de duplicidade."""
        serializer = OrganizationEditProfileSerializer(
            instance=organization, data={'slug': 'noite-baixa'}, partial=True
        )

        assert serializer.is_valid(), serializer.errors


class TestEditSerializerSlugFormato:
    def test_slug_curto_demais_invalido(self):
        serializer = OrganizationEditProfileSerializer(data={'slug': 'a'})

        assert not serializer.is_valid()
        assert 'slug' in serializer.errors

    def test_formato_do_modelo_vale_no_serializer(self):
        """Campo redeclarado não herda validadores do modelo: garante que
        validate_slug foi ligado explicitamente no serializer (underscore
        passa no SlugField do DRF, mas não no nosso formato)."""
        serializer = OrganizationEditProfileSerializer(data={'slug': 'meu_slug'})

        assert not serializer.is_valid()
        assert 'slug' in serializer.errors

from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone

from organizations.models import (
    Organization,
    OrganizationInvite,
    OrganizationMember,
    Roles,
)

pytestmark = pytest.mark.django_db


class TestDonoUnico:
    def test_dono_nao_pode_ter_duas_orgs_ativas(self, owner, organization):
        """Slug distinto: garante que o IntegrityError vem da constraint de
        owner, e não da de slug."""
        with pytest.raises(IntegrityError):
            Organization.objects.create(name='Segunda', slug='segunda', owner=owner)

    def test_soft_delete_libera_o_dono_para_nova_org(self, owner, organization):
        organization.delete()

        nova = Organization.objects.create(name='Nova', slug='nova', owner=owner)

        assert nova.owner == owner


class TestMembroUnico:
    def test_membro_duplicado_ativo_falha(self, seguidor, organization):
        OrganizationMember.objects.create(
            user=seguidor, organization=organization, role=Roles.CHECKIN
        )

        with pytest.raises(IntegrityError):
            OrganizationMember.objects.create(
                user=seguidor, organization=organization, role=Roles.GERENTE
            )

    def test_soft_delete_libera_nova_membership(self, seguidor, organization):
        membro = OrganizationMember.objects.create(
            user=seguidor, organization=organization, role=Roles.CHECKIN
        )
        membro.delete()

        novo = OrganizationMember.objects.create(
            user=seguidor, organization=organization, role=Roles.GERENTE
        )

        assert novo.role == Roles.GERENTE


class TestInvitePendenteUnico:
    def criar_invite(self, owner, seguidor, organization, **kwargs):
        kwargs.setdefault('role', Roles.CHECKIN)
        return OrganizationInvite.objects.create(
            invited_by=owner, user=seguidor, organization=organization, **kwargs
        )

    def test_segundo_invite_pendente_falha(self, owner, seguidor, organization):
        self.criar_invite(owner, seguidor, organization)

        with pytest.raises(IntegrityError):
            self.criar_invite(owner, seguidor, organization)

    def test_invite_aceito_libera_novo_pendente(self, owner, seguidor, organization):
        """A constraint só vale para status pendente: histórico de convites
        aceitos não bloqueia um convite novo."""
        self.criar_invite(
            owner, seguidor, organization,
            status=OrganizationInvite.StatusChoices.ACCEPTED,
        )

        novo = self.criar_invite(owner, seguidor, organization)

        assert novo.status == OrganizationInvite.StatusChoices.PENDING


class TestInviteExpiracao:
    def test_expires_at_default_e_7_dias(self, owner, seguidor, organization):
        invite = OrganizationInvite.objects.create(
            invited_by=owner,
            user=seguidor,
            organization=organization,
            role=Roles.CHECKIN,
        )

        esperado = timezone.now() + timedelta(days=7)
        assert abs(invite.expires_at - esperado) < timedelta(minutes=1)

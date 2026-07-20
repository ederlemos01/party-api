import pytest
from datetime import timedelta

from django.core import mail
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from organizations.models import OrganizationInvite, OrganizationMember, Roles

pytestmark = pytest.mark.django_db


def invite_url(slug):
    return reverse('invite-organization-members', kwargs={'org_slug': slug})


def accept_url(invite_pk):
    return reverse('accept-organization-invite', kwargs={'invite_pk': invite_pk})


# --- fixtures locais do fluxo de convite ---

@pytest.fixture
def owner_member(owner, organization):
    """A fixture 'organization' só cria a Organization; o IsOwner exige um
    OrganizationMember(role=OWNER) de verdade (no fluxo real quem cria é o
    CreateOrganizationView)."""
    return OrganizationMember.objects.create(
        user=owner, organization=organization, role=Roles.OWNER,
    )


@pytest.fixture
def owner_client(api_client, owner, owner_member):
    api_client.force_authenticate(user=owner)
    return api_client


@pytest.fixture
def convidado(criar_usuario):
    return criar_usuario(email='convidado@exemplo.com', username='convidado')


@pytest.fixture
def convidado_client(api_client, convidado):
    api_client.force_authenticate(user=convidado)
    return api_client


@pytest.fixture
def convite(owner, organization, convidado):
    return OrganizationInvite.objects.create(
        organization=organization, user=convidado,
        invited_by=owner, role=Roles.CHECKIN,
    )


# =====================================================================
# POST convite  (InviteOrganizationMemberView)
# =====================================================================

class TestConvidarAutorizacao:
    def test_anonimo_retorna_401(self, api_client, organization, convidado):
        response = api_client.post(
            invite_url(organization.slug),
            {'email': convidado.email, 'role': Roles.CHECKIN.value},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_nao_owner_retorna_403(self, auth_client, organization, convidado):
        """auth_client está autenticado como 'seguidor', que não é membro."""
        response = auth_client.post(
            invite_url(organization.slug),
            {'email': convidado.email, 'role': Roles.CHECKIN.value},
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestConvidar:
    def test_owner_convida_retorna_201_e_cria_invite(
        self, owner_client, owner, organization, convidado
    ):
        response = owner_client.post(
            invite_url(organization.slug),
            {'email': convidado.email, 'role': Roles.CHECKIN.value},
        )

        assert response.status_code == status.HTTP_201_CREATED
        invite = OrganizationInvite.objects.get(
            organization=organization, user=convidado
        )
        assert invite.status == OrganizationInvite.StatusChoices.PENDING
        assert invite.invited_by == owner
        assert invite.role == Roles.CHECKIN

    def test_email_sem_conta_retorna_400(self, owner_client, organization):
        response = owner_client.post(
            invite_url(organization.slug),
            {'email': 'ninguem@exemplo.com', 'role': Roles.CHECKIN.value},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_ja_membro_retorna_400(self, owner_client, organization, convidado):
        OrganizationMember.objects.create(
            user=convidado, organization=organization, role=Roles.VIEWER,
        )

        response = owner_client.post(
            invite_url(organization.slug),
            {'email': convidado.email, 'role': Roles.CHECKIN.value},
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_reconvidar_revoga_antigo_e_cria_novo(
        self, owner_client, organization, convidado, convite
    ):
        """Já existe convite pendente: reconvidar revoga o antigo e cria um novo,
        sem violar a unique_invite_pending."""
        response = owner_client.post(
            invite_url(organization.slug),
            {'email': convidado.email, 'role': Roles.MANAGER.value},
        )

        assert response.status_code == status.HTTP_201_CREATED
        convite.refresh_from_db()
        assert convite.status == OrganizationInvite.StatusChoices.REVOKED
        assert OrganizationInvite.objects.filter(
            organization=organization, user=convidado
        ).count() == 1

    def test_convidar_dispara_email(
        self, owner_client, organization, convidado,
        django_capture_on_commit_callbacks,settings
    ):
        settings.CELERY_TASK_ALWAYS_EAGER = True
        settings.CELERY_TASK_EAGER_PROPAGATES = True
        """O e-mail é registrado via transaction.on_commit, então só dispara
        quando o callback é executado (execute=True)."""
        with django_capture_on_commit_callbacks(execute=True):
            response = owner_client.post(
                invite_url(organization.slug),
                {'email': convidado.email, 'role': Roles.CHECKIN.value},
            )

        assert response.status_code == status.HTTP_201_CREATED
        assert len(mail.outbox) == 1
        assert convidado.email in mail.outbox[0].to


# =====================================================================
# POST aceitar convite  (AcceptOrganizationInviteView)
# =====================================================================

class TestAceitarConvite:
    def test_outro_usuario_retorna_403(self, api_client, convite, criar_usuario):
        intruso = criar_usuario()
        api_client.force_authenticate(user=intruso)

        response = api_client.post(accept_url(convite.id))

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_pendente_retorna_201_e_cria_membro(
        self, convidado_client, convite, convidado, organization
    ):
        response = convidado_client.post(accept_url(convite.id))

        assert response.status_code == status.HTTP_201_CREATED
        assert OrganizationMember.objects.filter(
            user=convidado, organization=organization
        ).exists()
        convite.refresh_from_db()
        assert convite.status == OrganizationInvite.StatusChoices.ACCEPTED

    def test_expirado_retorna_410(
        self, convidado_client, owner, organization, convidado
    ):
        expirado = OrganizationInvite.objects.create(
            organization=organization, user=convidado, invited_by=owner,
            role=Roles.CHECKIN, expires_at=timezone.now() - timedelta(days=1),
        )

        response = convidado_client.post(accept_url(expirado.id))

        assert response.status_code == status.HTTP_410_GONE
        assert not OrganizationMember.objects.filter(
            user=convidado, organization=organization
        ).exists()

    def test_ja_aceito_retorna_410(self, convidado_client, convite):
        convite.status = OrganizationInvite.StatusChoices.ACCEPTED
        convite.save(update_fields=['status'])

        response = convidado_client.post(accept_url(convite.id))

        assert response.status_code == status.HTTP_410_GONE

    def test_pendente_mas_ja_membro_retorna_400(
        self, convidado_client, convite, convidado, organization
    ):
        """Convite pendente, porém o usuário já é membro por outro caminho:
        o get_or_create do accept() devolve created=False -> AlreadyMember."""
        OrganizationMember.objects.create(
            user=convidado, organization=organization, role=Roles.VIEWER,
        )

        response = convidado_client.post(accept_url(convite.id))

        assert response.status_code == status.HTTP_400_BAD_REQUEST

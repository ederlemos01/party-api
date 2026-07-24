import itertools
from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from events.models import Event, EventStatus
from organizations.models import Organization, OrganizationMember, OrganizationRoles
from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def criar_usuario(db):
    """Factory de usuários: a constraint unique_active_organization_owner
    permite uma única org ativa por dono, então cada Organization extra
    criada num teste precisa de um dono diferente."""
    contador = itertools.count(1)

    def _criar(**kwargs):
        n = next(contador)
        kwargs.setdefault('email', f'usuario{n}@exemplo.com')
        kwargs.setdefault('username', f'usuario{n}')
        kwargs.setdefault('password', 'S3nha-F0rte!2026')
        return User.objects.create_user(**kwargs)

    return _criar


@pytest.fixture
def owner(criar_usuario):
    return criar_usuario(email='dono@exemplo.com', username='dono')


@pytest.fixture
def organization(owner):
    return Organization.objects.create(
        name='Coletivo Noite Baixa',
        slug='noite-baixa',
        owner=owner,
    )


@pytest.fixture
def outra_organization(criar_usuario):
    """Org de um segundo dono: unique_active_organization_owner não deixa
    o mesmo usuário ter duas orgs ativas."""
    return Organization.objects.create(
        name='Outro Coletivo',
        slug='outro-coletivo',
        owner=criar_usuario(),
    )


@pytest.fixture
def criar_evento(db):
    """Factory de eventos: preenche os obrigatórios com valores válidos
    (start < end) para cada teste sobrescrever só o campo em jogo."""

    def _criar(organization, **kwargs):
        inicio = timezone.now() + timedelta(days=7)
        kwargs.setdefault('title', 'Noite Baixa Vol. 1')
        kwargs.setdefault('start_at', inicio)
        kwargs.setdefault('end_at', inicio + timedelta(hours=4))
        kwargs.setdefault('location', 'Galpão 13, São Paulo')
        kwargs.setdefault('slug', 'noite-baixa-vol-1')
        return Event.objects.create(organization=organization, **kwargs)

    return _criar


@pytest.fixture
def evento_publicado(criar_evento, organization):
    return criar_evento(organization, status=EventStatus.PUBLISHED)


@pytest.fixture
def owner_client(api_client, owner):
    """Cliente autenticado como o dono da org. force_authenticate pula a
    emissão de JWT de propósito: o fluxo de token já é coberto em users/tests."""
    api_client.force_authenticate(user=owner)
    return api_client


@pytest.fixture
def gerente(criar_usuario, organization):
    """Usuário com papel MANAGER na organization, mas que NÃO é o dono.
    Cobre o caminho is_manager da CreateEventSerializer."""
    user = criar_usuario(email='gerente@exemplo.com', username='gerente')
    OrganizationMember.objects.create(
        user=user, organization=organization, role=OrganizationRoles.MANAGER,
    )
    return user


@pytest.fixture
def gerente_client(api_client, gerente):
    api_client.force_authenticate(user=gerente)
    return api_client


@pytest.fixture
def payload_evento(organization):
    """Payload válido para o POST de criação; cada teste altera só o campo
    em jogo. A organization é obrigatória no corpo (o `owner` é dono dela)."""
    inicio = timezone.now() + timedelta(days=7)
    return {
        'title': 'Festa de Lançamento',
        'description': 'Primeira edição.',
        'start_at': inicio,
        'end_at': inicio + timedelta(hours=4),
        'location': 'Galpão 13, São Paulo',
        'slug': 'festa-lancamento',
        'organization': organization.id,
    }

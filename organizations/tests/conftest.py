import itertools

import pytest
from rest_framework.test import APIClient

from organizations.models import Organization, OrganizationFollow
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
def seguidor(criar_usuario):
    return criar_usuario(email='seguidor@exemplo.com', username='seguidor')


@pytest.fixture
def organization(owner):
    return Organization.objects.create(
        name='Coletivo Noite Baixa',
        slug='noite-baixa',
        owner=owner,
    )


@pytest.fixture
def auth_client(api_client, seguidor):
    """Cliente autenticado como o seguidor. force_authenticate pula a emissão
    de JWT de propósito: o fluxo de token já é coberto em users/tests."""
    api_client.force_authenticate(user=seguidor)
    return api_client


@pytest.fixture
def follow(seguidor, organization):
    return OrganizationFollow.objects.create(
        user=seguidor, organization=organization
    )

import itertools

import pytest

from organizations.models import Organization, OrganizationFollow
from users.models import User


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
def user(criar_usuario):
    return criar_usuario(email='dono@exemplo.com', username='dono')


@pytest.fixture
def organization(user):
    return Organization.objects.create(
        name='Coletivo Noite Baixa',
        slug='noite-baixa',
        owner=user,
    )


@pytest.fixture
def follow(user, organization):
    return OrganizationFollow.objects.create(user=user, organization=organization)

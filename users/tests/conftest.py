import pytest
from rest_framework.test import APIClient

from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def valid_register_payload():
    return {
        'email': 'novo@exemplo.com',
        'username': 'novo_user',
        'password': 'S3nha-F0rte!2026',
    }


@pytest.fixture
def existing_user(db):
    return User.objects.create_user(
        email='existente@exemplo.com',
        username='existente',
        password='S3nha-F0rte!2026',
    )

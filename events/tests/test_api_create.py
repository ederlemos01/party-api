from datetime import timedelta

import pytest
from django.urls import reverse
from rest_framework import status

from events.models import Event, EventStatus

pytestmark = pytest.mark.django_db


def create_url():
    return reverse('create-event')


class TestCriacaoAutenticacao:
    def test_post_anonimo_retorna_401(self, api_client, payload_evento, db):
        response = api_client.post(create_url(), payload_evento, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestCriacaoSucesso:
    def test_dono_de_org_cria_evento_201(
        self, owner_client, organization, payload_evento
    ):
        response = owner_client.post(create_url(), payload_evento, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        evento = Event.objects.get(slug='festa-lancamento')
        assert evento.organization == organization
        assert evento.status == EventStatus.DRAFT


class TestCriacaoSemOrg:
    def test_autenticado_sem_org_retorna_400(self, owner_client, payload_evento):
        """Sem a fixture organization, o usuário autenticado não é dono de
        nenhuma org ativa."""
        response = owner_client.post(create_url(), payload_evento, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'non_field_errors' in response.data


class TestCriacaoPayloadInvalido:
    def test_titulo_ausente_retorna_400(
        self, owner_client, organization, payload_evento
    ):
        del payload_evento['title']

        response = owner_client.post(create_url(), payload_evento, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'title' in response.data

    def test_slug_com_formato_invalido_retorna_400(
        self, owner_client, organization, payload_evento
    ):
        payload_evento['slug'] = 'Slug--Invalido'

        response = owner_client.post(create_url(), payload_evento, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'slug' in response.data

    def test_end_at_antes_do_start_at_retorna_400(
        self, owner_client, organization, payload_evento
    ):
        payload_evento['end_at'] = payload_evento['start_at'] - timedelta(hours=1)

        response = owner_client.post(create_url(), payload_evento, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'end_at' in response.data

    def test_slug_ja_usado_na_org_retorna_400(
        self, owner_client, organization, criar_evento, payload_evento
    ):
        criar_evento(organization, slug='festa-lancamento')

        response = owner_client.post(create_url(), payload_evento, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'slug' in response.data
        assert Event.objects.count() == 1

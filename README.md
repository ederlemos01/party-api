# Party API

API REST de uma plataforma de eventos: organizações têm perfil público, seguidores,
membros com papéis (owner, manager, viewer, check-in) e eventos. Convites de membros
são enviados por e-mail de forma assíncrona.

**Stack:** Django 6 · Django REST Framework · PostgreSQL 17 · Celery + Redis ·
SimpleJWT · drf-spectacular (OpenAPI)

## Subindo o projeto (Docker — caminho recomendado)

Pré-requisitos: Docker + Docker Compose.

```bash
# 1. Crie o .env a partir do exemplo
cp .env.example .env

# 2. Gere uma SECRET_KEY e cole no .env
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 3. Suba tudo (Postgres, Redis, API com migrate automático, worker Celery)
docker compose up --build
```

A API sobe em `http://localhost:8000`. Em dev os e-mails **não são enviados de
verdade** — aparecem nos logs (`docker compose logs -f celery`).

> O código é montado por bind-mount: o `runserver` recarrega sozinho ao editar,
> mas o **worker Celery não** — depois de mexer em `tasks.py`, rode
> `docker compose restart celery`.

## URLs importantes

| O quê | URL |
|---|---|
| Base da API | `http://localhost:8000/api/v1/` |
| Swagger UI | `http://localhost:8000/api/v1/schema/swagger-ui/` |
| Redoc | `http://localhost:8000/api/v1/schema/redoc/` |
| Schema OpenAPI (vivo) | `http://localhost:8000/api/v1/schema/` |
| Admin | `http://localhost:8000/admin/` |

O `schema.yml` na raiz é um snapshot commitado do schema. A fonte da verdade é o
endpoint vivo; ao mudar o contrato, regenere o snapshot:

```bash
python manage.py spectacular --file schema.yml --validate
```

## Autenticação (JWT)

Fluxo: registrar → obter par de tokens → mandar o access token no header.

```bash
# Registro
curl -X POST http://localhost:8000/api/v1/users/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "a@b.com", "username": "fulano", "password": "SenhaForte123"}'

# Tokens (login) — o campo é "email" por ser o USERNAME_FIELD
curl -X POST http://localhost:8000/api/v1/users/token/ \
  -H "Content-Type: application/json" \
  -d '{"email": "a@b.com", "password": "SenhaForte123"}'

# Uso
curl http://localhost:8000/api/v1/users/perfil/me/ \
  -H "Authorization: Bearer <access>"
```

- **Access token: 60 minutos. Refresh token: 24 horas.** Renove via
  `POST /api/v1/users/token/refresh/` com `{"refresh": "..."}` quando receber 401.
- Todos os endpoints exigem autenticação, exceto registro, tokens, perfil público
  de organização e perfil público de evento.

## Convenções da API

- **Barra final obrigatória**: `POST /api/v1/events` (sem `/`) retorna 404 —
  o redirect automático do Django só vale para GET.
- **IDs são UUID.** Organizações são endereçadas por `slug` na URL; membros e
  convites, por UUID.
- **Criação de organização é em duas etapas**: o `POST` cria com slug
  auto-gerado e sem nome (`{id, slug}`); nome, descrição, fotos e slug definitivo
  entram via `PATCH /api/v1/manage/organizations/<slug>/`. Um usuário só pode ter
  uma organização.
- **Datas**: ISO 8601 em UTC. Formatação e fuso são responsabilidade do cliente.
- **Paginação** (todas as listas): envelope `{count, next, previous, results}`,
  20 itens por página, navegação via `?page=N`.
- **Upload de imagens** (fotos, banners): `multipart/form-data`.
- **Erros**: validação retorna 400 com dict por campo
  (`{"slug": ["mensagem"]}`); demais erros retornam `{"detail": "mensagem"}`.
  Convite expirado ou já resolvido responde **410 Gone**. Convite para quem já é
  membro, 400.
- **Seguir organização é idempotente**: `POST .../followers/` responde 201 mesmo
  se já seguia; `DELETE` responde 404 se não seguia.

## Rodando os testes

```bash
pytest              # suíte completa
pytest users        # um app
pytest --reuse-db   # re-execuções mais rápidas
```

> **Não use** `python manage.py test`: a suíte é pytest-style e o runner do
> Django coleta 0 testes e reporta OK (falso verde).

## Desenvolvimento sem Docker

Requer Python 3.12+, PostgreSQL e Redis locais (o `.env.example` já aponta para
`localhost`).

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver          # API
celery -A core worker -l info       # worker (segundo terminal)
```

## Estrutura

```
core/           # settings, URLs raiz, bootstrap do Celery
users/          # modelo de usuário custom (login por e-mail), registro, perfil
organizations/  # orgs, seguidores, membros, convites — regras em services.py
events/         # eventos das organizações
common/         # BaseModel (UUID + soft delete) e permissões por papel
```

Regras de negócio multi-etapa vivem em `services.py` (não nas views); erros de
domínio são exceções em `exceptions.py`. Tasks Celery ficam em `<app>/tasks.py`,
recebem IDs (nunca instâncias) e são disparadas via `transaction.on_commit`.

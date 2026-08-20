Esse projeto está sendo desenvolvido para ser uma API (back end) de uma plataforma completa de ponta a ponta para gestão de eventos, venda de ingressos online e interações sociais entre os usuarios. O sistema atua como uma ponte dupla: permite que organizadores criem eventos, gerenciem lotes de ingressos, ao mesmo tempo em que oferece aos participantes uma interface simples para explorar eventos, realizar compras seguras e acessar seus ingressos digitais."

## Estrutura

```
core/           # settings, URLs raiz, bootstrap do Celery
users/          # modelo de usuário custom (login por e-mail), registro, perfil
organizations/  # orgs, seguidores, membros, convites — regras em services.py
events/         # eventos das organizações
common/         # BaseModel (UUID + soft delete) e permissões por papel
tickets/        # TicketType controlando os lotes e estoque, e Ticket como instancia que o usuario ganha
orders/         # gerencia toda parte de pagamentos integracao com gateway do MP (atual foco de desenvolvimento)
```

## Como rodar

Stack: Django 6 + DRF, PostgreSQL 17, Redis e Celery. Há dois caminhos — tudo em
Docker (mais rápido) ou a API local com os serviços em Docker.

### execucao



```bash
cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(64))"   # ou: openssl rand -base64 48
```

```bash
docker compose up --build
```



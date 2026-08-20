"Esse projeto está sendo desenvolvido para ser uma API (back end) de uma plataforma completa de ponta a ponta para gestão de eventos, venda de ingressos online e interações sociais entre os usuarios. O sistema atua como uma ponte dupla: permite que organizadores criem eventos, gerenciem lotes de ingressos, ao mesmo tempo em que oferece aos participantes uma interface simples para explorar eventos, realizar compras seguras e acessar seus ingressos digitais."

## Estrutura

```
core/           # settings, URLs raiz, bootstrap do Celery
users/          # modelo de usuário custom (login por e-mail), registro, perfil
organizations/  # orgs, seguidores, membros, convites — regras em services.py
events/         # eventos das organizações
common/         # BaseModel (UUID + soft delete) e permissões por papel
```


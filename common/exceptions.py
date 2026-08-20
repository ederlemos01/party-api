from rest_framework.exceptions import APIException

class InviteExpired(APIException):
    status_code = 410
    default_detail = "Este convite expirou."

class NotInvitedUser(APIException):
    status_code = 403
    default_detail = "Você não é o destinatário deste convite."
    default_code = "not_invited_user"

class InviteNotPending(APIException):
    status_code = 410
    default_detail = "o convite nao esta pendente"


class AlreadyOrganizationMember(APIException):
    status_code = 400
    default_detail = "voce ja e membro da organizacao"

class AlreadyEventMember(APIException):
    status_code = 400
    default_detail = "voce ja e membro do evento"

class UserHasNoAccount(APIException):
    status_code = 400
    default_detail = "esse usuario nao possui conta" 

class InviteAlreadyExists(APIException):
    status_code = 400
    default_detail = "o convite ja foi enviado" 

class MPGatewayError(APIException):
    status_code = 202
    default_detail = "Falha ao comunicar com o Mercado Pago (rede, timeout, resposta inesperada"
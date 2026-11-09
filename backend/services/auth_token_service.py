from models.auth_session import AuthSession

class AuthTokenService:

    def __init__(self, token):
        self.token = token or ''

    def execute(self):
        sessao = AuthSession.buscar_por_token(self.token)
        return sessao.usuario if sessao else None

from models.auth_session import AuthSession

class UserLogoutService:

    def __init__(self, token):
        self.token = token or ''

    def execute(self):
        return AuthSession.revogar(self.token)

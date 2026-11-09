from werkzeug.security import check_password_hash
from models.auth_session import AuthSession
from models.user import User

class UserLoginService:

    def __init__(self, data):
        self.data = data or {}

    def execute(self):
        email = str(self.data.get('email') or '').strip().lower()
        senha = '' if self.data.get('senha') is None else str(self.data.get('senha'))
        if not email or not senha:
            raise ValueError('Informe e-mail e senha.')
        usuario = User.buscar_por_email(email)
        if not usuario or not usuario.senha_hash or not check_password_hash(usuario.senha_hash, senha):
            raise ValueError('E-mail ou senha inválidos.')
        return {'token': AuthSession.abrir(usuario), 'usuario': usuario.to_dict()}

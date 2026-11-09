from werkzeug.security import generate_password_hash
from models.auth_session import AuthSession
from models.user import User
from services.helpers import validar_senha, validar_usuario

class UserRegisterService:

    def __init__(self, data):
        self.data = data or {}

    def execute(self):
        validar_usuario(self.data, obrigatorio=True)
        senha = validar_senha(self.data.get('senha'))
        if User.buscar_por_email(self.data['email']):
            raise ValueError('Este e-mail já está cadastrado.')
        usuario = User.salvar({
            'nome': self.data['nome'],
            'email': self.data['email'],
            'senha_hash': generate_password_hash(senha)
        })
        return {'token': AuthSession.abrir(usuario), 'usuario': usuario.to_dict()}

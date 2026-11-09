from models.user import User
from services.helpers import validar_usuario

class UserCreateService:

    def __init__(self, data):
        self.data = data or {}

    def execute(self):
        validar_usuario(self.data, obrigatorio=True)
        self.data.pop('senha', None)
        self.data.pop('senha_hash', None)
        if User.buscar_por_email(self.data['email']):
            raise ValueError('Este e-mail já está cadastrado.')
        return User.salvar(self.data).to_dict()

from models.user import User
from services.helpers import validar_usuario

class UserUpdateService:

    def __init__(self, item_id, data):
        self.item_id = item_id
        self.data = data or {}

    def execute(self):
        item = User.buscar_por_id(self.item_id)
        if not item:
            return None
        self.data.pop('senha', None)
        self.data.pop('senha_hash', None)
        validar_usuario(self.data, obrigatorio=False)
        if 'email' in self.data:
            outro = User.buscar_por_email(self.data['email'])
            if outro and outro.user_id != item.user_id:
                raise ValueError('Este e-mail já está cadastrado.')
        return item.atualizar(self.data).to_dict()

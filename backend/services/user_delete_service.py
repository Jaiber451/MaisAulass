from models.user import User

class UserDeleteService:

    def __init__(self, item_id):
        self.item_id = item_id

    def execute(self):
        item = User.buscar_por_id(self.item_id)
        return item.deletar() if item else False

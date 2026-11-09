from models.user import User

class UserListService:

    def execute(self):
        return [item.to_dict() for item in User.listar_todos()]

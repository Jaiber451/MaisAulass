from models.activity import Activity

class ActivityListService:

    def execute(self):
        return [item.to_dict() for item in Activity.listar_todos()]

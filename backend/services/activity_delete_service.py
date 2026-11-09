from models.activity import Activity

class ActivityDeleteService:

    def __init__(self, item_id):
        self.item_id = item_id

    def execute(self):
        item = Activity.buscar_por_id(self.item_id)
        return item.deletar() if item else False

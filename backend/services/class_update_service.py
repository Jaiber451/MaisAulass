from models.school_class import SchoolClass

class SchoolClassUpdateService:

    def __init__(self, item_id, data):
        self.item_id = item_id
        self.data = data or {}

    def execute(self):
        item = SchoolClass.buscar_por_id(self.item_id)
        return item.atualizar(self.data).to_dict() if item else None

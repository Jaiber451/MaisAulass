from models.school_class import SchoolClass

class SchoolClassDeleteService:

    def __init__(self, item_id):
        self.item_id = item_id

    def execute(self):
        item = SchoolClass.buscar_por_id(self.item_id)
        return item.deletar() if item else False

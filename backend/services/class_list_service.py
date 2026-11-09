from models.school_class import SchoolClass

class SchoolClassListService:

    def execute(self):
        return [item.to_dict() for item in SchoolClass.listar_todos()]

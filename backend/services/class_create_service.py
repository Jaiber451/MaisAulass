from models.school_class import SchoolClass
from services.helpers import ensure_fields

class SchoolClassCreateService:

    def __init__(self, data):
        self.data = data or {}

    def execute(self):
        ensure_fields(self.data, ['nome_turma', 'user_id'])
        return SchoolClass.salvar(self.data).to_dict()

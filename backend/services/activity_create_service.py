from models.activity import Activity
from services.helpers import ensure_fields

class ActivityCreateService:

    def __init__(self, data):
        self.data = data or {}

    def execute(self):
        ensure_fields(self.data, ['titulo', 'turma_id', 'data_entrega'])
        return Activity.salvar(self.data).to_dict()

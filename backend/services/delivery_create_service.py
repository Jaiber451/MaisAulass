from models.delivery import Delivery
from services.helpers import ensure_fields

class DeliveryCreateService:

    def __init__(self, data):
        self.data = data or {}

    def execute(self):
        ensure_fields(self.data, ['data_entrega', 'atividade_id', 'user_id'])
        return Delivery.salvar(self.data).to_dict()

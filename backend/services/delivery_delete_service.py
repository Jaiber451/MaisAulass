from models.delivery import Delivery

class DeliveryDeleteService:

    def __init__(self, item_id):
        self.item_id = item_id

    def execute(self):
        item = Delivery.buscar_por_id(self.item_id)
        return item.deletar() if item else False

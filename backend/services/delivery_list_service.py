from models.delivery import Delivery

class DeliveryListService:

    def execute(self):
        return [item.to_dict() for item in Delivery.listar_todos()]

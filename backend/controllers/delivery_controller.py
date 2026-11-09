from flask import Blueprint, jsonify, request
from services.delivery_list_service import DeliveryListService
from services.delivery_filter_service import DeliveryFilterService
from services.delivery_create_service import DeliveryCreateService
from services.delivery_update_service import DeliveryUpdateService
from services.delivery_delete_service import DeliveryDeleteService
from sqlalchemy.exc import IntegrityError
from extensions import db
delivery_bp = Blueprint('deliverys', __name__)

class DeliveryController:

    def list(self):
        status = request.args.get('status', '')
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        if status or data_inicio or data_fim:
            try:
                return jsonify(DeliveryFilterService(status, data_inicio, data_fim).execute())
            except ValueError as error:
                return (jsonify({'error': str(error)}), 400)
        return jsonify(DeliveryListService().execute())

    def create(self):
        try:
            return (jsonify(DeliveryCreateService(request.get_json() or {}).execute()), 201)
        except ValueError as e:
            return (jsonify({'error': str(e)}), 400)
        except IntegrityError:
            db.session.rollback()
            return (jsonify({'error': 'Dados inválidos ou relacionamento inexistente.'}), 400)

    def update(self, item_id):
        try:
            item = DeliveryUpdateService(item_id, request.get_json() or {}).execute()
            return (jsonify(item or {'error': 'Registro não encontrado'}), 200 if item else 404)
        except IntegrityError:
            db.session.rollback()
            return (jsonify({'error': 'Dados inválidos ou relacionamento inexistente.'}), 400)

    def delete(self, item_id):
        try:
            ok = DeliveryDeleteService(item_id).execute()
            return (jsonify({'deleted': ok}), 200 if ok else 404)
        except IntegrityError:
            db.session.rollback()
            return (jsonify({'error': 'Não é possível excluir este registro.'}), 400)
controller = DeliveryController()
delivery_bp.add_url_rule('', view_func=controller.list, methods=['GET'])
delivery_bp.add_url_rule('', view_func=controller.create, methods=['POST'])
delivery_bp.add_url_rule('/<int:item_id>', view_func=controller.update, methods=['PUT'])
delivery_bp.add_url_rule('/<int:item_id>', view_func=controller.delete, methods=['DELETE'])

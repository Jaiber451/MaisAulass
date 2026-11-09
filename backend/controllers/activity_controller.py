from flask import Blueprint, jsonify, request
from services.activity_list_service import ActivityListService
from services.activity_filter_service import ActivityFilterService
from services.activity_create_service import ActivityCreateService
from services.activity_update_service import ActivityUpdateService
from services.activity_delete_service import ActivityDeleteService
from sqlalchemy.exc import IntegrityError
from extensions import db
activity_bp = Blueprint('activitys', __name__)

class ActivityController:

    def list(self):
        data_inicio = request.args.get('data_inicio', '')
        data_fim = request.args.get('data_fim', '')
        if data_inicio or data_fim:
            try:
                return jsonify(ActivityFilterService(data_inicio, data_fim).execute())
            except ValueError as error:
                return (jsonify({'error': str(error)}), 400)
        return jsonify(ActivityListService().execute())

    def create(self):
        try:
            return (jsonify(ActivityCreateService(request.get_json() or {}).execute()), 201)
        except ValueError as e:
            return (jsonify({'error': str(e)}), 400)
        except IntegrityError:
            db.session.rollback()
            return (jsonify({'error': 'Dados inválidos ou relacionamento inexistente.'}), 400)

    def update(self, item_id):
        try:
            item = ActivityUpdateService(item_id, request.get_json() or {}).execute()
            return (jsonify(item or {'error': 'Registro não encontrado'}), 200 if item else 404)
        except IntegrityError:
            db.session.rollback()
            return (jsonify({'error': 'Dados inválidos ou relacionamento inexistente.'}), 400)

    def delete(self, item_id):
        try:
            ok = ActivityDeleteService(item_id).execute()
            return (jsonify({'deleted': ok}), 200 if ok else 404)
        except IntegrityError:
            db.session.rollback()
            return (jsonify({'error': 'Não é possível excluir este registro.'}), 400)
controller = ActivityController()
activity_bp.add_url_rule('', view_func=controller.list, methods=['GET'])
activity_bp.add_url_rule('', view_func=controller.create, methods=['POST'])
activity_bp.add_url_rule('/<int:item_id>', view_func=controller.update, methods=['PUT'])
activity_bp.add_url_rule('/<int:item_id>', view_func=controller.delete, methods=['DELETE'])

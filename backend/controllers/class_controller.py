from flask import Blueprint, jsonify, request
from services.class_list_service import SchoolClassListService
from services.class_filter_service import SchoolClassFilterService
from services.class_create_service import SchoolClassCreateService
from services.class_update_service import SchoolClassUpdateService
from services.class_delete_service import SchoolClassDeleteService
from sqlalchemy.exc import IntegrityError
from extensions import db
class_bp = Blueprint('classs', __name__)

class SchoolClassController:

    def list(self):
        user_id = request.args.get('user_id')
        service = SchoolClassFilterService(user_id) if user_id else SchoolClassListService()
        try:
            return jsonify(service.execute())
        except ValueError as error:
            return (jsonify({'error': str(error)}), 400)

    def create(self):
        try:
            return (jsonify(SchoolClassCreateService(request.get_json() or {}).execute()), 201)
        except ValueError as e:
            return (jsonify({'error': str(e)}), 400)
        except IntegrityError:
            db.session.rollback()
            return (jsonify({'error': 'Dados inválidos ou relacionamento inexistente.'}), 400)

    def update(self, item_id):
        try:
            item = SchoolClassUpdateService(item_id, request.get_json() or {}).execute()
            return (jsonify(item or {'error': 'Registro não encontrado'}), 200 if item else 404)
        except IntegrityError:
            db.session.rollback()
            return (jsonify({'error': 'Dados inválidos ou relacionamento inexistente.'}), 400)

    def delete(self, item_id):
        try:
            ok = SchoolClassDeleteService(item_id).execute()
            return (jsonify({'deleted': ok}), 200 if ok else 404)
        except IntegrityError:
            db.session.rollback()
            return (jsonify({'error': 'Não é possível excluir este registro.'}), 400)
controller = SchoolClassController()
class_bp.add_url_rule('', view_func=controller.list, methods=['GET'])
class_bp.add_url_rule('', view_func=controller.create, methods=['POST'])
class_bp.add_url_rule('/<int:item_id>', view_func=controller.update, methods=['PUT'])
class_bp.add_url_rule('/<int:item_id>', view_func=controller.delete, methods=['DELETE'])

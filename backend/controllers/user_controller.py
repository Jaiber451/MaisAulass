from flask import Blueprint, jsonify, request
from services.user_list_service import UserListService
from services.user_search_service import UserSearchService
from services.user_create_service import UserCreateService
from services.user_update_service import UserUpdateService
from services.user_delete_service import UserDeleteService
from sqlalchemy.exc import IntegrityError
from extensions import db
user_bp = Blueprint('users', __name__)

class UserController:

    def list(self):
        nome = request.args.get('nome', '').strip()
        service = UserSearchService(nome) if nome else UserListService()
        return jsonify(service.execute())

    def create(self):
        try:
            return (jsonify(UserCreateService(request.get_json() or {}).execute()), 201)
        except ValueError as e:
            return (jsonify({'error': str(e)}), 400)
        except IntegrityError:
            db.session.rollback()
            return (jsonify({'error': 'Dados inválidos ou relacionamento inexistente.'}), 400)

    def update(self, item_id):
        try:
            item = UserUpdateService(item_id, request.get_json() or {}).execute()
            return (jsonify(item or {'error': 'Registro não encontrado'}), 200 if item else 404)
        except ValueError as e:
            return (jsonify({'error': str(e)}), 400)
        except IntegrityError:
            db.session.rollback()
            return (jsonify({'error': 'Dados inválidos ou relacionamento inexistente.'}), 400)

    def delete(self, item_id):
        try:
            ok = UserDeleteService(item_id).execute()
            return (jsonify({'deleted': ok}), 200 if ok else 404)
        except IntegrityError:
            db.session.rollback()
            return (jsonify({'error': 'Não é possível excluir este registro.'}), 400)
controller = UserController()
user_bp.add_url_rule('', view_func=controller.list, methods=['GET'])
user_bp.add_url_rule('', view_func=controller.create, methods=['POST'])
user_bp.add_url_rule('/<int:item_id>', view_func=controller.update, methods=['PUT'])
user_bp.add_url_rule('/<int:item_id>', view_func=controller.delete, methods=['DELETE'])

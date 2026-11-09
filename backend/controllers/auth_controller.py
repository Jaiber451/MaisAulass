from flask import Blueprint, g, jsonify, request
from sqlalchemy.exc import IntegrityError
from extensions import db
from services.auth_token_service import AuthTokenService
from services.user_login_service import UserLoginService
from services.user_logout_service import UserLogoutService
from services.user_register_service import UserRegisterService
auth_bp = Blueprint('auth', __name__)

def token_do_pedido():
    header = request.headers.get('Authorization', '')
    if header.startswith('Bearer '):
        return header[7:].strip()
    return ''

class AuthController:

    def register(self):
        try:
            return (jsonify(UserRegisterService(request.get_json(silent=True) or {}).execute()), 201)
        except ValueError as e:
            return (jsonify({'error': str(e)}), 400)
        except IntegrityError:
            db.session.rollback()
            return (jsonify({'error': 'Este e-mail já está cadastrado.'}), 400)

    def login(self):
        try:
            return jsonify(UserLoginService(request.get_json(silent=True) or {}).execute())
        except ValueError as e:
            return (jsonify({'error': str(e)}), 400)

    def me(self):
        return jsonify(g.usuario.to_dict())

    def logout(self):
        UserLogoutService(token_do_pedido()).execute()
        return jsonify({'ok': True})

    def usuario_atual(self):
        return AuthTokenService(token_do_pedido()).execute()
controller = AuthController()
auth_bp.add_url_rule('/cadastro', view_func=controller.register, methods=['POST'])
auth_bp.add_url_rule('/login', view_func=controller.login, methods=['POST'])
auth_bp.add_url_rule('/logout', view_func=controller.logout, methods=['POST'])
auth_bp.add_url_rule('/me', view_func=controller.me, methods=['GET'])

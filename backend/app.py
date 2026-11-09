from pathlib import Path
from flask import Flask, g, jsonify, request, send_from_directory
from flask_cors import CORS
from sqlalchemy import event
from sqlalchemy.engine import Engine

@event.listens_for(Engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()
    except Exception:
        pass
from config import Config
from extensions import db
from models import User, SchoolClass, Activity, Delivery
from controllers.auth_controller import auth_bp, controller as auth_controller
from controllers.user_controller import user_bp
from controllers.class_controller import class_bp
from controllers.activity_controller import activity_bp
from controllers.delivery_controller import delivery_bp
from controllers.dashboard_controller import dashboard_bp
FRONTEND_DIR = Path(__file__).resolve().parent.parent / 'frontend'

def seed():
    if not User.listar_todos():
        ana = User.salvar({'nome': 'Julia Souza', 'email': 'julia@maisaulas.local'})
        pedro = User.salvar({'nome': 'Pedro Lima', 'email': 'pedro@maisaulas.local'})
        turma = SchoolClass.salvar({'nome_turma': 'Turma 2B', 'user_id': ana.user_id, 'descricao_atividade': 'Atividades da semana'})
        activity = Activity.salvar({'titulo': 'Exercícios de Matemática', 'descricao_atividade': 'Resolver a lista 1', 'turma_id': turma.turma_id, 'data_entrega': '2026-09-01'})
        Delivery.salvar({'data_entrega': '2026-08-25', 'status_entrega': 'Entregue', 'atividade_id': activity.atividade_id, 'user_id': pedro.user_id, 'nota': 9})

def atualizar_esquema():
    db.create_all()
    colunas = {coluna['name'] for coluna in db.inspect(db.engine).get_columns('usuario')}
    if 'senha_hash' not in colunas:
        db.session.execute(db.text('ALTER TABLE usuario ADD COLUMN senha_hash VARCHAR(512)'))
        db.session.commit()

def create_app():
    app = Flask(__name__, static_folder=str(FRONTEND_DIR / 'static'), static_url_path='/static')
    app.config.from_object(Config)
    db.init_app(app)
    CORS(app, resources={'/api/*': {'origins': '*'}})
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/usuarios')
    app.register_blueprint(class_bp, url_prefix='/api/turmas')
    app.register_blueprint(activity_bp, url_prefix='/api/atividades')
    app.register_blueprint(delivery_bp, url_prefix='/api/entregas')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    with app.app_context():
        atualizar_esquema()
        seed()

    @app.before_request
    def proteger_api():
        if not request.path.startswith('/api/') or request.method == 'OPTIONS':
            return None
        if (request.method, request.path) in {('POST', '/api/auth/login'), ('POST', '/api/auth/cadastro'), ('GET', '/api/health')}:
            return None
        usuario = auth_controller.usuario_atual()
        if not usuario:
            return (jsonify({'error': 'Faça login para continuar.'}), 401)
        g.usuario = usuario
        return None

    @app.get('/api/health')
    def health():
        return jsonify({'status': 'ok', 'service': '+Aula API'})

    @app.get('/')
    def index():
        return send_from_directory(FRONTEND_DIR / 'templates', 'index.html')

    @app.errorhandler(404)
    def not_found(_):
        return (jsonify({'error': 'Rota não encontrada'}), 404)
    return app
app = create_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


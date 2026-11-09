from sqlalchemy import func
from extensions import db
from models.user import User
from models.school_class import SchoolClass
from models.activity import Activity
from models.delivery import Delivery

class DashboardRepository:

    @staticmethod
    def resumo():
        return {'usuarios': db.session.query(func.count(User.user_id)).scalar() or 0, 'turmas': db.session.query(func.count(SchoolClass.turma_id)).scalar() or 0, 'atividades': db.session.query(func.count(Activity.atividade_id)).scalar() or 0, 'entregas': db.session.query(func.count(Delivery.entrega_id)).scalar() or 0, 'pendentes': db.session.query(func.count(Delivery.entrega_id)).filter(Delivery.status_entrega != 'Entregue').scalar() or 0}

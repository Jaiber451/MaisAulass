from sqlalchemy import func
from models.activity import Activity
from models.delivery import Delivery
from models.school_class import SchoolClass
from models.user import User

class FilterRepository:

    @staticmethod
    def usuarios_por_nome(nome):
        consulta = User.query
        if nome:
            consulta = consulta.filter(func.lower(User.nome).contains(nome.strip().lower()))
        return consulta.order_by(User.nome).all()

    @staticmethod
    def turmas_por_responsavel(user_id):
        consulta = SchoolClass.query
        if user_id:
            consulta = consulta.filter(SchoolClass.user_id == user_id)
        return consulta.order_by(SchoolClass.nome_turma).all()

    @staticmethod
    def atividades_por_periodo(data_inicio, data_fim):
        consulta = Activity.query
        if data_inicio:
            consulta = consulta.filter(Activity.data_entrega >= data_inicio)
        if data_fim:
            consulta = consulta.filter(Activity.data_entrega <= data_fim)
        return consulta.order_by(Activity.data_entrega, Activity.titulo).all()

    @staticmethod
    def entregas_por_filtros(status, data_inicio, data_fim):
        consulta = Delivery.query
        if status:
            consulta = consulta.filter(Delivery.status_entrega == status)
        if data_inicio:
            consulta = consulta.filter(Delivery.data_entrega >= data_inicio)
        if data_fim:
            consulta = consulta.filter(Delivery.data_entrega <= data_fim)
        return consulta.order_by(Delivery.data_entrega.desc(), Delivery.entrega_id.desc()).all()

    @staticmethod
    def relatorio_por_atividade(atividade_id):
        consulta = Delivery.query
        if atividade_id:
            consulta = consulta.filter(Delivery.atividade_id == atividade_id)
        entregas = consulta.order_by(Delivery.entrega_id.desc()).all()
        notas = [entrega.nota for entrega in entregas if entrega.nota is not None]
        return {'items': [entrega.to_dict() for entrega in entregas], 'resumo': {'total': len(entregas), 'concluidas': sum((entrega.status_entrega == 'Entregue' for entrega in entregas)), 'atrasadas': sum((entrega.status_entrega == 'Atrasada' for entrega in entregas)), 'media': round(sum(notas) / len(notas), 2) if notas else None}}

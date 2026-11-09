from extensions import db

class Delivery(db.Model):
    __tablename__ = 'entrega'
    entrega_id = db.Column(db.Integer, primary_key=True)
    data_entrega = db.Column(db.String(100), nullable=False)
    status_entrega = db.Column(db.String(100), nullable=False, default='Pendente')
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividade.atividade_id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.user_id', ondelete='CASCADE'), nullable=False)
    nota = db.Column(db.Integer, nullable=True)
    atividade = db.relationship('Activity', back_populates='entregas')
    usuario = db.relationship('User')

    @classmethod
    def listar_todos(cls):
        return cls.query.order_by(cls.entrega_id.desc()).all()

    @classmethod
    def buscar_por_id(cls, item_id):
        return db.session.get(cls, item_id)

    @classmethod
    def salvar(cls, data):
        item = cls(data_entrega=str(data['data_entrega']), status_entrega=data.get('status_entrega', 'Pendente'), atividade_id=data['atividade_id'], user_id=data['user_id'], nota=data.get('nota'))
        db.session.add(item)
        db.session.commit()
        return item

    def atualizar(self, data):
        for f in ('data_entrega', 'status_entrega', 'atividade_id', 'user_id', 'nota'):
            if f in data:
                setattr(self, f, data[f])
        db.session.commit()
        return self

    def deletar(self):
        db.session.delete(self)
        db.session.commit()
        return True

    def to_dict(self):
        return {'id': self.entrega_id, 'data_entrega': self.data_entrega, 'status_entrega': self.status_entrega, 'atividade_id': self.atividade_id, 'atividade_titulo': self.atividade.titulo if self.atividade else None, 'user_id': self.user_id, 'usuario_nome': self.usuario.nome if self.usuario else None, 'nota': self.nota}

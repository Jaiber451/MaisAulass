from extensions import db

class Activity(db.Model):
    __tablename__ = 'atividade'
    atividade_id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao_atividade = db.Column(db.String(100), nullable=True)
    turma_id = db.Column(db.Integer, db.ForeignKey('turma.turma_id', ondelete='CASCADE'), nullable=False)
    data_entrega = db.Column(db.String(100), nullable=False)
    turma = db.relationship('SchoolClass', back_populates='atividades')
    entregas = db.relationship('Delivery', back_populates='atividade', cascade='all, delete-orphan')

    @classmethod
    def listar_todos(cls):
        return cls.query.order_by(cls.atividade_id.desc()).all()

    @classmethod
    def buscar_por_id(cls, item_id):
        return db.session.get(cls, item_id)

    @classmethod
    def salvar(cls, data):
        item = cls(titulo=data['titulo'].strip(), descricao_atividade=data.get('descricao_atividade') or None, turma_id=data['turma_id'], data_entrega=str(data['data_entrega']))
        db.session.add(item)
        db.session.commit()
        return item

    def atualizar(self, data):
        for f in ('titulo', 'descricao_atividade', 'turma_id', 'data_entrega'):
            if f in data:
                setattr(self, f, data[f].strip() if f in ('titulo', 'descricao_atividade') and isinstance(data[f], str) else data[f])
        db.session.commit()
        return self

    def deletar(self):
        db.session.delete(self)
        db.session.commit()
        return True

    def to_dict(self):
        return {'id': self.atividade_id, 'titulo': self.titulo, 'descricao_atividade': self.descricao_atividade or '', 'turma_id': self.turma_id, 'turma_nome': self.turma.nome_turma if self.turma else None, 'data_entrega': self.data_entrega}

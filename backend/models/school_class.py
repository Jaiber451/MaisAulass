from extensions import db

class SchoolClass(db.Model):
    __tablename__ = 'turma'
    turma_id = db.Column(db.Integer, primary_key=True)
    nome_turma = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.user_id', ondelete='CASCADE'), nullable=False)
    descricao_atividade = db.Column(db.String(100), nullable=True)
    usuario = db.relationship('User')
    atividades = db.relationship('Activity', back_populates='turma', cascade='all, delete-orphan')

    @classmethod
    def listar_todos(cls):
        return cls.query.order_by(cls.nome_turma).all()

    @classmethod
    def buscar_por_id(cls, item_id):
        return db.session.get(cls, item_id)

    @classmethod
    def salvar(cls, data):
        item = cls(nome_turma=data['nome_turma'].strip(), user_id=data['user_id'], descricao_atividade=data.get('descricao_atividade') or None)
        db.session.add(item)
        db.session.commit()
        return item

    def atualizar(self, data):
        for f in ('nome_turma', 'user_id', 'descricao_atividade'):
            if f in data:
                setattr(self, f, data[f] if f != 'nome_turma' else data[f].strip())
        db.session.commit()
        return self

    def deletar(self):
        db.session.delete(self)
        db.session.commit()
        return True

    def to_dict(self):
        return {'id': self.turma_id, 'nome_turma': self.nome_turma, 'user_id': self.user_id, 'usuario_nome': self.usuario.nome if self.usuario else None, 'descricao_atividade': self.descricao_atividade or ''}

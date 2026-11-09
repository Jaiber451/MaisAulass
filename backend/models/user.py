from extensions import db

class User(db.Model):
    __tablename__ = 'usuario'
    user_id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    senha_hash = db.Column(db.String(512), nullable=True)

    @classmethod
    def listar_todos(cls):
        return cls.query.order_by(cls.nome).all()

    @classmethod
    def buscar_por_id(cls, item_id):
        return db.session.get(cls, item_id)

    @classmethod
    def buscar_por_email(cls, email):
        return cls.query.filter(cls.email == str(email).strip().lower()).first()

    @classmethod
    def salvar(cls, data):
        item = cls(
            nome=data['nome'].strip(),
            email=data['email'].strip().lower(),
            senha_hash=data.get('senha_hash')
        )
        db.session.add(item)
        db.session.commit()
        return item

    def atualizar(self, data):
        if 'nome' in data:
            self.nome = data['nome'].strip()
        if 'email' in data:
            self.email = data['email'].strip().lower()
        db.session.commit()
        return self

    def deletar(self):
        db.session.delete(self)
        db.session.commit()
        return True

    def to_dict(self):
        return {'id': self.user_id, 'nome': self.nome, 'email': self.email}

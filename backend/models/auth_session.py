import hashlib
import secrets
from extensions import db

class AuthSession(db.Model):
    __tablename__ = 'sessao'
    sessao_id = db.Column(db.Integer, primary_key=True)
    token_hash = db.Column(db.String(64), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('usuario.user_id', ondelete='CASCADE'), nullable=False)
    usuario = db.relationship('User')

    @staticmethod
    def _hash(token):
        return hashlib.sha256(token.encode()).hexdigest()

    @classmethod
    def abrir(cls, usuario):
        token = secrets.token_urlsafe(32)
        item = cls(token_hash=cls._hash(token), user_id=usuario.user_id)
        db.session.add(item)
        db.session.commit()
        return token

    @classmethod
    def buscar_por_token(cls, token):
        if not token:
            return None
        return cls.query.filter_by(token_hash=cls._hash(token)).first()

    @classmethod
    def revogar(cls, token):
        item = cls.buscar_por_token(token)
        if not item:
            return False
        db.session.delete(item)
        db.session.commit()
        return True

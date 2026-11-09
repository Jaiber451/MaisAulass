import re
from sqlalchemy.exc import IntegrityError

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

def ensure_fields(data, fields):
    missing = [f for f in fields if data.get(f) in (None, '')]
    if missing:
        raise ValueError('Campos obrigatórios: ' + ', '.join(missing))

def validar_usuario(data, obrigatorio=True):
    if obrigatorio:
        ensure_fields(data, ['nome', 'email'])
    if 'nome' in data:
        nome = str(data.get('nome') or '').strip()
        if len(nome) < 3 or len(nome) > 100:
            raise ValueError('Informe um nome entre 3 e 100 caracteres.')
        data['nome'] = nome
    if 'email' in data:
        email = str(data.get('email') or '').strip().lower()
        if not email or len(email) > 100 or not EMAIL_RE.fullmatch(email):
            raise ValueError('Informe um e-mail válido.')
        data['email'] = email

def validar_senha(senha):
    senha = '' if senha is None else str(senha)
    if len(senha) < 8 or len(senha) > 100:
        raise ValueError('A senha precisa ter de 8 a 100 caracteres.')
    return senha

def commit_error(exc):
    if isinstance(exc, IntegrityError):
        return 'Não foi possível concluir a operação por causa de um relacionamento ou dado duplicado.'
    return 'Não foi possível concluir a operação.'

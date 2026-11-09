from repositories.filter_repository import FilterRepository

class UserSearchService:

    def __init__(self, nome=''):
        self.nome = nome

    def execute(self):
        return [usuario.to_dict() for usuario in FilterRepository.usuarios_por_nome(self.nome)]

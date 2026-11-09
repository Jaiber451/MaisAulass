from repositories.filter_repository import FilterRepository

class SchoolClassFilterService:

    def __init__(self, user_id=None):
        self.user_id = user_id

    def execute(self):
        if self.user_id not in (None, ''):
            try:
                self.user_id = int(self.user_id)
            except (TypeError, ValueError):
                raise ValueError('Selecione um responsável válido.')
        return [turma.to_dict() for turma in FilterRepository.turmas_por_responsavel(self.user_id)]

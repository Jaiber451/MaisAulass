from repositories.filter_repository import FilterRepository

class ActivityReportService:

    def __init__(self, atividade_id=None):
        self.atividade_id = atividade_id

    def execute(self):
        if self.atividade_id not in (None, ''):
            try:
                self.atividade_id = int(self.atividade_id)
            except (TypeError, ValueError) as exc:
                raise ValueError('Selecione uma atividade válida.') from exc
        return FilterRepository.relatorio_por_atividade(self.atividade_id)

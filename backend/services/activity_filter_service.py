from datetime import date
from repositories.filter_repository import FilterRepository

class ActivityFilterService:

    def __init__(self, data_inicio=None, data_fim=None):
        self.data_inicio = data_inicio or ''
        self.data_fim = data_fim or ''

    def execute(self):
        self._validar_periodo()
        atividades = FilterRepository.atividades_por_periodo(self.data_inicio, self.data_fim)
        return [atividade.to_dict() for atividade in atividades]

    def _validar_periodo(self):
        try:
            inicio = date.fromisoformat(self.data_inicio) if self.data_inicio else None
            fim = date.fromisoformat(self.data_fim) if self.data_fim else None
        except ValueError as exc:
            raise ValueError('Informe datas válidas no formato AAAA-MM-DD.') from exc
        if inicio and fim and (inicio > fim):
            raise ValueError('A data inicial não pode ser posterior à data final.')

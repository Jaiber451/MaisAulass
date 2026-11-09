from datetime import date
from repositories.filter_repository import FilterRepository

class DeliveryFilterService:
    STATUS_VALIDOS = {'Pendente', 'Entregue', 'Atrasada'}

    def __init__(self, status=None, data_inicio=None, data_fim=None):
        self.status = status or ''
        self.data_inicio = data_inicio or ''
        self.data_fim = data_fim or ''

    def execute(self):
        if self.status and self.status not in self.STATUS_VALIDOS:
            raise ValueError('Selecione um status válido.')
        try:
            inicio = date.fromisoformat(self.data_inicio) if self.data_inicio else None
            fim = date.fromisoformat(self.data_fim) if self.data_fim else None
        except ValueError as exc:
            raise ValueError('Informe datas válidas no formato AAAA-MM-DD.') from exc
        if inicio and fim and (inicio > fim):
            raise ValueError('A data inicial não pode ser posterior à data final.')
        entregas = FilterRepository.entregas_por_filtros(self.status, self.data_inicio, self.data_fim)
        return [entrega.to_dict() for entrega in entregas]

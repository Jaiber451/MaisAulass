from repositories.dashboard_repository import DashboardRepository

class DashboardSummaryService:

    def execute(self):
        return DashboardRepository.resumo()

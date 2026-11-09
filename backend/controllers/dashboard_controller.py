from flask import Blueprint, jsonify, request
from services.dashboard_summary_service import DashboardSummaryService
from services.report_activity_service import ActivityReportService
dashboard_bp = Blueprint('dashboard', __name__)

class DashboardController:

    def summary(self):
        return jsonify(DashboardSummaryService().execute())

    def report(self):
        try:
            atividade_id = request.args.get('atividade_id')
            return jsonify(ActivityReportService(atividade_id).execute())
        except ValueError as error:
            return (jsonify({'error': str(error)}), 400)
controller = DashboardController()
dashboard_bp.add_url_rule('/dashboard', view_func=controller.summary, methods=['GET'])
dashboard_bp.add_url_rule('/relatorios', view_func=controller.report, methods=['GET'])

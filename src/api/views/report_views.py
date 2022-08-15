"""Report views."""
# Standard Python Libraries
import os

# Third-Party Libraries
from flask import jsonify, request, send_file
from flask.views import MethodView

# cisagov Libraries
from api.manager import CustomerManager, CycleManager, SubscriptionManager
from api.schemas.reports_schema import AggregateReportsSchema
from utils.logging import setLogger
from utils.notifications import Notification
from utils.reports import (
    get_report,
    get_report_pdf,
    get_reports_sent,
    get_sector_industry_report,
)
from utils.stats import get_all_customer_stats

logger = setLogger(__name__)

subscription_manager = SubscriptionManager()
cycle_manager = CycleManager()
customer_manager = CustomerManager()


class ReportHtmlView(MethodView):
    """Status report view."""

    def get(self, cycle_id, report_type):
        """Post."""
        nonhuman = False
        if request.args.get("nonhuman", "") == "true":
            nonhuman = True

        resp_code = 200
        try:
            resp = get_report(cycle_id, report_type, nonhuman)
        except Exception as e:
            logger.exception(f"{report_type} report error: {str(e)}")
            resp = {"error": f"{report_type} report html failed"}
            resp_code = 400

        return resp, resp_code


class ReportPdfView(MethodView):
    """ReportPdfView."""

    def get(self, cycle_id, report_type):
        """Get."""
        nonhuman = False
        if request.args.get("nonhuman", "") == "true":
            nonhuman = True
        cycle = cycle_manager.get(document_id=cycle_id)
        subscription = subscription_manager.get(
            document_id=cycle["subscription_id"], fields=["reporting_password"]
        )
        filepath = get_report_pdf(
            cycle,
            report_type,
            reporting_password=subscription.get("reporting_password"),
            nonhuman=nonhuman,
        )
        try:
            logger.info(f"Sending file {filepath}")
            return send_file(
                filepath,
                as_attachment=True,
                download_name=f"{report_type}.pdf",
            )
        except Exception as e:
            logger.exception(
                f"An exception occurred creating a report for the {cycle['start_date']}-{cycle['end_date']} cycle for {subscription['name']} subscription: {e}",
                extra={"source_type": "cycle", "source": subscription["_id"]},
            )
        finally:
            logger.info(f"Deleting file {filepath}")
            os.remove(filepath)


class ReportEmailView(MethodView):
    """ReportEmailView."""

    def get(self, cycle_id, report_type):
        """Get."""
        nonhuman = False
        if request.args.get("nonhuman", "") == "true":
            nonhuman = True
        cycle = cycle_manager.get(document_id=cycle_id)
        subscription = subscription_manager.get(document_id=cycle["subscription_id"])
        Notification(f"{report_type}_report", subscription, cycle).send(nonhuman)
        return jsonify({"success": True}), 200


class AggregateReportView(MethodView):
    """AggregateReportView."""

    def get(self):
        """Get."""
        context = {
            "customers_enrolled": customer_manager.count(),
        }
        context["customers_active"] = subscription_manager.distinct_count(
            "customer_id", {"status": {"$in": ["queued", "running"]}}
        )

        context["new_subscriptions"] = subscription_manager.count({"status": "created"})
        context["ongoing_subscriptions"] = subscription_manager.count(
            {"status": {"$in": ["queued", "running"]}}
        )
        context["stopped_subscriptions"] = subscription_manager.count(
            {"status": "stopped"}
        )

        context.update(get_reports_sent())

        context.update(get_sector_industry_report())

        context["all_customer_stats"] = get_all_customer_stats()

        return AggregateReportsSchema().dump(context)

"""Report views."""
# Standard Python Libraries
import logging
import os

# Third-Party Libraries
from flask import jsonify, request, send_file
from flask.views import MethodView

# cisagov Libraries
from api.manager import CustomerManager, CycleManager, SubscriptionManager
from api.schemas.reports_schema import AggregateReportsSchema
from utils.notifications import Notification
from utils.reports import (
    get_all_customer_stats,
    get_report,
    get_report_pdf,
    get_reports_sent,
    get_sector_industry_report,
)

subscription_manager = SubscriptionManager()
cycle_manager = CycleManager()
customer_manager = CustomerManager()


class ReportHtmlView(MethodView):
    """Status report view."""

    def get(self, report_type):
        """Post."""
        data = request.args.get("cycles").split(",")
        nonhuman = False
        if request.args.get("nonhuman", "") == "true":
            nonhuman = True
        return get_report(data, report_type, nonhuman), 200


class ReportPdfView(MethodView):
    """ReportPdfView."""

    def get(self, report_type):
        """Get."""
        cycle_ids = request.args.get("cycles").split(",")
        nonhuman = False
        if request.args.get("nonhuman", "") == "true":
            nonhuman = True
        cycle = cycle_manager.get(document_id=cycle_ids[0], fields=["subscription_id"])
        subscription = subscription_manager.get(
            document_id=cycle["subscription_id"], fields=["reporting_password"]
        )
        filepath = get_report_pdf(
            cycle_ids,
            report_type,
            reporting_password=subscription.get("reporting_password"),
            nonhuman=nonhuman,
        )
        try:
            logging.info(f"Sending file {filepath}")
            return send_file(
                filepath, as_attachment=True, attachment_filename=f"{report_type}.pdf"
            )
        except Exception as e:
            logging.exception(e)
        finally:
            logging.info(f"Deleting file {filepath}")
            os.remove(filepath)


class ReportEmailView(MethodView):
    """ReportEmailView."""

    def get(self, report_type):
        """Get."""
        data = request.args.get("cycles").split(",")
        nonhuman = False
        if request.args.get("nonhuman", "") == "true":
            nonhuman = True
        cycle = cycle_manager.get(document_id=data[0])
        subscription = subscription_manager.get(document_id=cycle["subscription_id"])
        Notification(f"{report_type}_report", subscription, cycle).send(nonhuman)
        return jsonify({"success": True}), 200


class AggregateReportView(MethodView):
    """AggregateReportView."""

    def get(self):
        """Get."""
        context = {
            "customers_enrolled": len(customer_manager.all(fields=["_id"])),
        }
        context.update(get_reports_sent())
        context.update(get_sector_industry_report())
        context.update(get_all_customer_stats())
        return AggregateReportsSchema().dump(context)

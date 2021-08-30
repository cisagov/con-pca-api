"""Report views."""
# Standard Python Libraries
import logging
import os

# Third-Party Libraries
from flask import jsonify, send_file
from flask.views import MethodView
from utils.notifications import Notification
from utils.reports import get_report, get_report_pdf

# cisagov Libraries
from api.manager import CustomerManager, CycleManager, SubscriptionManager

subscription_manager = SubscriptionManager()
cycle_manager = CycleManager()
customer_manager = CustomerManager()


class ReportHtmlView(MethodView):
    """Status report view."""

    def get(self, cycle_uuid, report_type):
        """Get."""
        return get_report(cycle_uuid, report_type), 200


class ReportPdfView(MethodView):
    """ReportPdfView."""

    def get(self, cycle_uuid, report_type):
        """Get."""
        filepath = get_report_pdf(cycle_uuid, report_type)
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

    def get(self, cycle_uuid, report_type):
        """Get."""
        cycle = cycle_manager.get(uuid=cycle_uuid)
        subscription = subscription_manager.get(uuid=cycle["subscription_uuid"])
        Notification(f"{report_type}_report", subscription, cycle).send()
        return jsonify({"success": True}), 200

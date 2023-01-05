"""Report views."""
# Standard Python Libraries
from datetime import datetime, timedelta
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
from utils.stats import get_all_customer_stats, get_rolling_emails, get_rolling_tasks

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
            pw=subscription.get("reporting_password"),
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
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "customers_active": {
                        "$addToSet": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$in": ["$status", ["queued", "running"]]},
                                        {"$ne": ["$archived", True]},
                                    ]
                                },
                                "$customer_id",
                                "$$REMOVE",
                            ]
                        }
                    },
                    "new_subscriptions": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$in": ["$status", ["created"]]},
                                        {"$ne": ["$archived", True]},
                                    ]
                                },
                                1,
                                0,
                            ]
                        }
                    },
                    "ongoing_subscriptions": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$in": ["$status", ["queued", "running"]]},
                                        {"$ne": ["$archived", True]},
                                    ]
                                },
                                1,
                                0,
                            ]
                        }
                    },
                    "stopped_subscriptions": {
                        "$sum": {
                            "$cond": [
                                {
                                    "$and": [
                                        {"$in": ["$status", ["stopped"]]},
                                        {"$ne": ["$archived", True]},
                                    ]
                                },
                                1,
                                0,
                            ]
                        }
                    },
                }
            },
            {
                "$project": {
                    "customers_active": {"$size": "$customers_active"},
                    "new_subscriptions": "$new_subscriptions",
                    "ongoing_subscriptions": "$ongoing_subscriptions",
                    "stopped_subscriptions": "$stopped_subscriptions",
                }
            },
        ]
        aggregate_stats = subscription_manager.aggregate(pipeline)
        aggregate_stats = aggregate_stats[0] if len(aggregate_stats) > 0 else {}
        aggregate_stats["customers_enrolled"] = customer_manager.count(
            {"archived": {"$ne": True}}
        )

        aggregate_stats.update(get_reports_sent())

        aggregate_stats.update(get_sector_industry_report())

        email_sending_stats = {}
        (
            email_sending_stats["emails_sent_24_hours"],
            email_sending_stats["emails_scheduled_24_hours"],
            email_sending_stats["emails_sent_on_time_24_hours_ratio"],
            email_sending_stats["emails_clicked_24_hours"],
        ) = get_rolling_emails(1)
        (
            email_sending_stats["emails_sent_7_days"],
            email_sending_stats["emails_scheduled_7_days"],
            email_sending_stats["emails_sent_on_time_7_days_ratio"],
            email_sending_stats["emails_clicked_7_days"],
        ) = get_rolling_emails(7)
        (
            email_sending_stats["emails_sent_30_days"],
            email_sending_stats["emails_scheduled_30_days"],
            email_sending_stats["emails_sent_on_time_30_days_ratio"],
            email_sending_stats["emails_clicked_30_days"],
        ) = get_rolling_emails(30)
        aggregate_stats["email_sending_stats"] = email_sending_stats

        task_stats = {}
        (
            task_stats["tasks_succeeded_24_hours"],
            task_stats["tasks_scheduled_24_hours"],
            task_stats["tasks_succeeded_24_hours_ratio"],
        ) = get_rolling_tasks(1)
        (
            task_stats["tasks_succeeded_7_days"],
            task_stats["tasks_scheduled_7_days"],
            task_stats["tasks_succeeded_7_days_ratio"],
        ) = get_rolling_tasks(7)
        (
            task_stats["tasks_succeeded_30_days"],
            task_stats["tasks_scheduled_30_days"],
            task_stats["tasks_succeeded_30_days_ratio"],
        ) = get_rolling_tasks(30)
        aggregate_stats["task_stats"] = task_stats

        aggregate_stats["all_customer_stats"] = get_all_customer_stats()

        return AggregateReportsSchema().dump(aggregate_stats)


class OverdueTasksReportView(MethodView):
    """OverdueTasksReportView."""

    def get(self):
        """Get."""
        parameters = dict(request.args)
        parameters = subscription_manager.get_query(parameters)

        parameters["overdue_subscriptions"] = False
        if request.args.get("overdue_subscriptions", "").lower() == "true":
            parameters["overdue_subscriptions"] = True

        pipeline = [
            {"$unwind": {"path": "$tasks"}},
            {
                "$match": {
                    "status": {"$eq": "running"},
                    "continuous_subscription": {"$eq": True},
                    "tasks.task_type": {"$in": ["start_next_cycle", "end_cycle"]},
                    "tasks.executed": {"$eq": False},
                    "tasks.scheduled_date": {
                        "$lte": datetime.now() - timedelta(minutes=5),
                    },
                }
                if parameters["overdue_subscriptions"]
                else {
                    "status": {"$eq": "running"},
                    "tasks.executed": {"$eq": False},
                    "tasks.scheduled_date": {
                        "$lte": datetime.now() - timedelta(minutes=5),
                    },
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "scheduled_date": "$tasks.scheduled_date",
                    "executed": "$tasks.executed",
                    "task_type": "$tasks.task_type",
                    "subscription_status": "$status",
                    "subscription_name": "$name",
                    "subscription_continuous": "$continuous_subscription",
                }
            },
        ]
        overdue_tasks = subscription_manager.aggregate(pipeline)

        return overdue_tasks

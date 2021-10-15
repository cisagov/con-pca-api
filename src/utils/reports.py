"""Report utils."""
# Standard Python Libraries
from datetime import datetime
import json
import os.path
import subprocess  # nosec

# Third-Party Libraries
from faker import Faker
from flask import render_template
from flask.templating import render_template_string

# cisagov Libraries
from api.manager import CustomerManager, CycleManager, SubscriptionManager
from utils import time
from utils.emails import get_email_context
from utils.recommendations import get_recommendations
from utils.stats import get_cycle_stats, get_ratio

customer_manager = CustomerManager()
cycle_manager = CycleManager()
subscription_manager = SubscriptionManager()


def get_cycles(cycle_ids):
    """Individually get each cycle so they contain targets."""
    cycles = []
    for cycle_id in cycle_ids:
        cycles.append(cycle_manager.get(document_id=cycle_id))
    return cycles


def merge_cycles(cycles):
    """Merge cycles."""
    if len(cycles) == 1:
        return cycles[0]
    cycles = sorted(cycles, key=lambda x: x["start_date"])

    cycle_set = {
        "start_date": cycles[0]["start_date"],
        "end_date": cycles[-1]["end_date"],
        "subscription_id": cycles[0]["subscription_id"],
        "template_ids": [],
        "target_count": 0,
        "targets": [],
    }
    for cycle in cycles:
        cycle_set["template_ids"].extend(cycle["template_ids"])
        cycle_set["targets"].extend(cycle["targets"])
        cycle_set["target_count"] += cycle["target_count"]

    return cycle_set


def get_report(cycle_ids, report_type, nonhuman=False):
    """Get report by type and cycle."""
    cycles = get_cycles(cycle_ids)
    cycle = merge_cycles(cycles)
    subscription = subscription_manager.get(
        document_id=cycle["subscription_id"],
        fields=[
            "_id",
            "name",
            "customer_id",
            "target_domain",
            "start_date",
            "primary_contact",
            "admin_email",
            "status",
        ],
    )
    customer = customer_manager.get(document_id=subscription["customer_id"])
    get_cycle_stats(cycle)

    context = {
        "stats": cycle["nonhuman_stats"] if nonhuman else cycle["stats"],
        "cycle": cycle,
        "subscription": subscription,
        "customer": customer,
        "time": time,
        "preview_template": preview_template,
        "datetime": datetime,
        "recommendations": get_recommendations(),
        "json": json,
    }
    return render_template(f"reports/{report_type}.html", **context)


def get_report_pdf(cycle_ids, report_type, nonhuman=False):
    """Get report pdf."""
    filename = f"{cycle_ids[0]}_report.pdf"
    args = [
        "node",
        "report.js",
        filename,
        ",".join(cycle_ids),
        report_type,
        str(nonhuman),
    ]
    subprocess.run(args)  # nosec

    if not os.path.exists(f"/var/www/{filename}"):
        raise Exception("Reporting Exception - Check Logs")

    return f"/var/www/{filename}"


def get_reports_sent():
    """Get reports sent."""
    response = {
        "monthly_reports_sent": 0,
        "cycle_reports_sent": 0,
        "yearly_reports_sent": 0,
    }
    subscriptions = subscription_manager.all(fields=["notification_history"])
    for subscription in subscriptions:
        for notification in subscription.get("notification_history", []):
            if f"{notification['message_type']}s_sent" in response:
                response[f"{notification['message_type']}s_sent"] += 1
    return response


def get_sector_industry_report():
    """Get reports on sector industries."""
    response = {
        "federal_stats": {"subscription_count": 0, "cycle_count": 0},
        "state_stats": {"subscription_count": 0, "cycle_count": 0},
        "local_stats": {"subscription_count": 0, "cycle_count": 0},
        "tribal_stats": {"subscription_count": 0, "cycle_count": 0},
        "private_stats": {"subscription_count": 0, "cycle_count": 0},
    }
    customers = customer_manager.all(fields=["_id", "customer_type"])
    for customer in customers:
        stat = f"{customer['customer_type'].lower()}_stats"
        subscriptions = subscription_manager.all(
            params={"customer_id": customer["_id"]},
            fields=["_id"],
        )
        cycles = cycle_manager.all(
            params={"subscription_id": {"$in": [s["_id"] for s in subscriptions]}},
            fields=["_id"],
        )
        response[stat]["subscription_count"] += len(subscriptions)
        response[stat]["cycle_count"] += len(cycles)
    return response


def get_all_customer_stats():
    """Get all customer stats."""
    sent = 0
    total_clicks = 0
    averages = []
    cycles = cycle_manager.all(fields=["_id", "dirty_stats", "stats"])
    for cycle in cycles:
        if cycle.get("dirty_stats", True):
            cycle = cycle_manager.get(cycle["_id"])
            get_cycle_stats(cycle)
        sent += cycle["stats"]["stats"]["all"]["sent"]["count"]
        clicks = cycle["stats"]["stats"]["all"]["clicked"]["count"]
        avg = cycle["stats"]["stats"]["all"]["clicked"]["average"]
        total_clicks += clicks
        averages.extend([avg for _ in range(0, clicks)])

    return {
        "click_rate_across_all_customers": get_ratio(total_clicks, sent),
        "average_time_to_click_all_customers": time.convert_seconds(
            0 if len(averages) == 0 else sum(averages) / len(averages)
        ),
    }


def preview_template(data, customer):
    """Preview template subjects, html and from addresses for reports."""
    fake = Faker()
    target = {
        "email": fake.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "position": fake.job(),
    }
    context = get_email_context(customer=customer, target=target)
    return render_template_string(data, **context)

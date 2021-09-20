"""Report utils."""
# Standard Python Libraries
from subprocess import check_output  # nosec

# Third-Party Libraries
from flask import render_template

# cisagov Libraries
from api.manager import CustomerManager, CycleManager, SubscriptionManager
from utils import time
from utils.stats import get_cycle_stats, get_ratio

customer_manager = CustomerManager()
cycle_manager = CycleManager()
subscription_manager = SubscriptionManager()


def merge_cycles(cycles):
    """Merge cycles."""
    if len(cycles) == 1:
        return cycles[0]
    cycles = sorted(cycles, key=lambda x: x["start_date"])

    cycle_set = {
        "start_date": cycles[0]["start_date"],
        "end_date": cycles[-1]["end_date"],
        "subscription_uuid": cycles[0]["subscription_uuid"],
        "template_uuids": [],
        "target_count": 0,
        "targets": [],
    }
    for cycle in cycles:
        cycle_set["template_uuids"].extend(cycle["template_uuids"])
        cycle_set["targets"].extend(cycle["targets"])
        cycle_set["target_count"] += cycle["target_count"]

    return cycle_set


def get_report(cycle_uuids, report_type, nonhuman=False):
    """Get report by type and cycle."""
    cycles = cycle_manager.all(params={"cycle_uuid": {"$in": cycle_uuids}})
    cycle = merge_cycles(cycles)
    subscription = subscription_manager.get(
        uuid=cycle["subscription_uuid"],
        fields=[
            "subscription_uuid",
            "name",
            "customer_uuid",
            "target_domain",
            "start_date",
            "primary_contact",
            "admin_email",
            "status",
        ],
    )
    customer = customer_manager.get(uuid=subscription["customer_uuid"])
    get_cycle_stats(cycle)

    context = {
        "stats": cycle["nonhuman_stats"] if nonhuman else cycle["stats"],
        "cycle": cycle,
        "subscription": subscription,
        "customer": customer,
        "time": time,
    }
    return render_template(f"reports/{report_type}.html", **context)


def get_report_pdf(cycle_uuids, report_type, nonhuman=False):
    """Get report pdf."""
    args = ["node", "report.js", ",".join(cycle_uuids), report_type, str(nonhuman)]
    filename = str(check_output(args).decode("utf-8")).strip()  # nosec
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
    customers = customer_manager.all(fields=["customer_uuid", "customer_type"])
    for customer in customers:
        stat = f"{customer['customer_type'].lower()}_stats"
        subscriptions = subscription_manager.all(
            params={"customer_uuid": customer["customer_uuid"]},
            fields=["subscription_uuid"],
        )
        cycles = cycle_manager.all(
            params={
                "subscription_uuid": {
                    "$in": [s["subscription_uuid"] for s in subscriptions]
                }
            },
            fields=["cycle_uuid"],
        )
        response[stat]["subscription_count"] += len(subscriptions)
        response[stat]["cycle_count"] += len(cycles)
    return response


def get_all_customer_stats():
    """Get all customer stats."""
    sent = 0
    total_clicks = 0
    averages = []
    cycles = cycle_manager.all(fields=["cycle_uuid", "dirty_stats", "stats"])
    for cycle in cycles:
        if cycle.get("dirty_stats", True):
            cycle = cycle_manager.get(cycle["cycle_uuid"])
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

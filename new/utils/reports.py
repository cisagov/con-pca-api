"""Report utils."""
# Standard Python Libraries
from subprocess import check_output  # nosec

# Third-Party Libraries
from flask import render_template
from utils import time
from utils.stats import get_cycle_stats

# cisagov Libraries
from api.manager import CustomerManager, CycleManager, SubscriptionManager

customer_manager = CustomerManager()
cycle_manager = CycleManager()
subscription_manager = SubscriptionManager()


def get_report(cycle_uuid, report_type, nonhuman=False):
    """Get report by type and cycle."""
    cycle = cycle_manager.get(uuid=cycle_uuid)
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


def get_report_pdf(cycle_uuid, report_type, nonhuman=False):
    """Get report pdf."""
    args = ["node", "report.js", cycle_uuid, report_type, str(nonhuman)]
    filename = str(check_output(args).decode("utf-8")).strip()  # nosec
    return f"/var/www/{filename}"

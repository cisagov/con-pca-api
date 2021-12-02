"""Report utils."""
# Standard Python Libraries
from datetime import datetime
import json
import os
import os.path
import subprocess  # nosec

# Third-Party Libraries
from PyPDF2 import PdfFileReader, PdfFileWriter
from faker import Faker
from flask import render_template
from flask.templating import render_template_string

# cisagov Libraries
from api.manager import (
    CustomerManager,
    CycleManager,
    SendingProfileManager,
    SubscriptionManager,
)
from utils import time
from utils.emails import get_email_context, get_from_address
from utils.stats import get_cycle_stats, get_ratio
from utils.templates import get_indicators

customer_manager = CustomerManager()
cycle_manager = CycleManager()
sending_profile_manager = SendingProfileManager()
subscription_manager = SubscriptionManager()


def get_report(cycle_id, report_type, nonhuman=False):
    """Get report by type and cycle."""
    cycle = cycle_manager.get(document_id=cycle_id)
    subscription = subscription_manager.get(
        document_id=cycle["subscription_id"],
        fields=[
            "_id",
            "name",
            "customer_id",
            "sending_profile_id",
            "target_domain",
            "start_date",
            "primary_contact",
            "admin_email",
            "status",
        ],
    )
    customer = customer_manager.get(document_id=subscription["customer_id"])
    get_cycle_stats(cycle)
    previous_cycles = get_previous_cycles(cycle)

    context = {
        "stats": cycle["nonhuman_stats"] if nonhuman else cycle["stats"],
        "cycle": cycle,
        "subscription": subscription,
        "customer": customer,
        "previous_cycles": previous_cycles,
        "time": time,
        "preview_template": preview_template,
        "preview_from_address": preview_from_address,
        "datetime": datetime,
        "indicators": get_indicators(),
        "json": json,
        "str": str,
    }
    return render_template(f"reports/{report_type}.html", **context)


def get_report_pdf(cycle_id, report_type, reporting_password=None, nonhuman=False):
    """Get report pdf."""
    filename = f"{cycle_id}_report.pdf"
    args = [
        "node",
        "report.js",
        filename,
        cycle_id,
        report_type,
        str(nonhuman),
    ]
    subprocess.run(args)  # nosec

    filepath = f"/var/www/{filename}"
    new_filepath = f"/var/www/new-{filename}"

    if not os.path.exists(filepath):
        raise Exception("Reporting Exception - Check Logs")

    writer = PdfFileWriter()
    reader = PdfFileReader(open(filepath, "rb"))
    for i in range(0, reader.getNumPages()):
        writer.addPage(reader.getPage(i))
    if reporting_password:
        writer.encrypt(reporting_password, use_128bit=True)

    output = open(new_filepath, "wb")
    writer.write(output)
    output.close()
    os.remove(filepath)

    return new_filepath


def get_reports_sent():
    """Get reports sent."""
    response = {
        "status_reports_sent": 0,
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


def get_previous_cycles(current_cycle):
    """Get previous cycles for report."""
    cycles = cycle_manager.all(
        params={"subscription_id": current_cycle["subscription_id"]}
    )
    cycles = list(filter(lambda x: x["_id"] != current_cycle["_id"], cycles))

    # Sort timeline so most recent is first
    cycles = sorted(cycles, key=lambda x: x["start_date"], reverse=True)

    # Update stats for each cycle
    for cycle in cycles:
        get_cycle_stats(cycle)

    return cycles


def preview_from_address(template, subscription, customer):
    """Preview from address in a report."""
    if template.get("sending_profile_id"):
        sending_profile = sending_profile_manager.get(
            document_id=template["sending_profile_id"]
        )
    else:
        sending_profile = sending_profile_manager.get(
            document_id=subscription["sending_profile_id"]
        )
    from_address = get_from_address(sending_profile, template["from_address"])
    return preview_template(from_address, customer)


def preview_template(data, customer):
    """Preview template subject, from_address and html for reports."""
    fake = Faker()
    target = {
        "email": fake.email(),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "position": fake.job(),
    }
    context = get_email_context(customer=customer, target=target)
    return render_template_string(data, **context)

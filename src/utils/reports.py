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
    RecommendationManager,
    SendingProfileManager,
    SubscriptionManager,
)
from utils import time
from utils.emails import get_email_context, get_from_address
from utils.stats import get_cycle_stats, get_ratio
from utils.templates import get_indicators

customer_manager = CustomerManager()
cycle_manager = CycleManager()
recommendation_manager = RecommendationManager()
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
    recommendations = recommendation_manager.all()

    context = {
        "stats": cycle["nonhuman_stats"] if nonhuman else cycle["stats"],
        "cycle": cycle,
        "subscription": subscription,
        "customer": customer,
        "previous_cycles": previous_cycles,
        "recommendations": recommendations,
        "compare_svg": compare_svg,
        "percent_svg": percent_svg,
        "percent": percent,
        "preview_template": preview_template,
        "preview_from_address": preview_from_address,
        "indicators": get_indicators(),
        "datetime": datetime,
        "json": json,
        "str": str,
        "time": time,
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
    cycles = list(
        filter(
            lambda x: x["_id"] != current_cycle["_id"]
            and x["start_date"] < current_cycle["start_date"],
            cycles,
        )
    )

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


def percent(ratio):
    """Get percentage from ratio."""
    return round(ratio * 100)


def compare_svg(
    current,
    previous,
    up_color="default",
    down_color="default",
    neutral_color="default",
):
    """Compare current and previous value and return an SVG based on the result."""
    colors = {
        "good": "#5e9732",
        "bad": "#c41230",
        "neutral": "#fdc010",
        "default": "#006c9c",
    }
    up_svg = f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 22" style="width: 0.25in">
            <g id="Layer_2" data-name="Layer 2">
                <g id="Layer_1-2" data-name="Layer 1">
                <polygon
                    style="
                        fill: {colors.get(up_color)};
                        stroke: {colors.get(up_color)};
                        stroke-linecap: round;
                        stroke-linejoin: round;
                        stroke-width: 2px;
                    "
                    points="31 14.78 23.5 7.89 16 1 8.5 7.89 1 14.78 6.66 14.78 6.66 21 10.32 21 22.04 21 25.42 21 25.42 14.78 31 14.78"
                />
                </g>
            </g>
        </svg>
    """

    down_svg = f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 22" style="width: 0.25in; height: 0.25in">
            <g id="Layer_2" data-name="Layer 2">
                <g id="Layer_1-2" data-name="Layer 1">
                <polygon
                    style="
                        fill: {colors.get(down_color)};
                        stroke: {colors.get(down_color)};
                        stroke-linecap: round;
                        stroke-linejoin: round;
                        stroke-width: 2px;
                        width: .25in;
                    "
                    points="1 7.22 8.5 14.11 16 21 23.5 14.11 31 7.22 25.34 7.22 25.34 1 21.68 1 9.96 1 6.58 1 6.58 7.22 1 7.22"
                />
                </g>
            </g>
        </svg>
    """

    neutral_svg = f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 22" style="width: 0.25in; height: 0.25in;">
            <g id="Layer_2" data-name="Layer 2">
                <g id="Layer_1-2" data-name="Layer 1">
                <polygon
                    style="
                        fill: {colors.get(neutral_color)};
                        stroke: {colors.get(neutral_color)};
                        stroke-linecap: round;
                        stroke-linejoin: round;
                        stroke-width: 2px;
                    "
                    points="31 14.78 23.5 7.89 16 1 8.5 7.89 1 14.78 6.66 14.78 6.66 21 10.32 21 22.04 21 25.42 21 25.42 14.78 31 14.78"
                    transform="rotate(90, 17, 11)"
                />
                </g>
            </g>
        </svg>
    """

    if not previous:
        return neutral_svg
    if current > previous:
        return up_svg
    if current < previous:
        return down_svg
    if current == previous:
        return neutral_svg


def percent_change(current_percent, previous_percent):
    """Get percent change."""
    return round((current_percent - previous_percent) / abs(previous_percent) * 100, 2)


def percent_svg(current_percent, previous_percent):
    """Get an increase/decrease svg with a percentage."""
    change = percent_change(current_percent, previous_percent)
    up_svg = f"""
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 22" style="width: 50px; height: 40px">
            <g id="Layer_2" data-name="Layer 2">
                <g id="Layer_1-2" data-name="Layer 1">
                <polygon
                    style="
                        fill: #C41230;
                        stroke: #C41230;
                        stroke-linecap: round;
                        stroke-linejoin: round;
                        stroke-width: 2px;
                    "
                    points="31 14.78 23.5 7.89 16 1 8.5 7.89 1 14.78 6.66 14.78 6.66 21 10.32 21 22.04 21 25.42 21 25.42 14.78 31 14.78"
                />
                </g>
            </g>
        </svg>
        <p style="color: #C41230; margin: 0 0 0">+{change}%</p>
    """

    down_svg = f"""
        <p style="color: #5E9732; margin: 0 0 0">{change}%</p>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 22" style="width: 50px; height: 40px">
            <g id="Layer_2" data-name="Layer 2">
                <g id="Layer_1-2" data-name="Layer 1">
                <polygon
                    style="
                        fill: #5E9732;
                        stroke: #5E9732;
                        stroke-linecap: round;
                        stroke-linejoin: round;
                        stroke-width: 2px;
                        width: .25in;
                    "
                    points="1 7.22 8.5 14.11 16 21 23.5 14.11 31 7.22 25.34 7.22 25.34 1 21.68 1 9.96 1 6.58 1 6.58 7.22 1 7.22"
                />
                </g>
            </g>
        </svg>
    """

    neutral_svg = f"""
        <p style="color: white; margin: 0 0 0">{change}</p>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 22" style="width: 50px; height: 40px">
            <g id="Layer_2" data-name="Layer 2">
                <g id="Layer_1-2" data-name="Layer 1">
                <polygon
                    style="
                        fill: #006c9c;
                        stroke: #006c9c;
                        stroke-linecap: round;
                        stroke-linejoin: round;
                        stroke-width: 2px;
                    "
                    points="31 14.78 23.5 7.89 16 1 8.5 7.89 1 14.78 6.66 14.78 6.66 21 10.32 21 22.04 21 25.42 21 25.42 14.78 31 14.78"
                    transform="rotate(90, 17, 11)"
                />
                </g>
            </g>
        </svg>
    """

    if current_percent > previous_percent:
        return up_svg
    if current_percent < previous_percent:
        return down_svg
    if current_percent == previous_percent:
        return neutral_svg

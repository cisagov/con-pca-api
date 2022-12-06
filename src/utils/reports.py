"""Report utils."""
# Standard Python Libraries
import csv
from datetime import datetime, timedelta
from io import StringIO
import json
import os
import os.path
import re
import subprocess  # nosec
from typing import Any, List, Tuple

# Third-Party Libraries
from PyPDF2 import PdfFileReader, PdfFileWriter
from bs4 import BeautifulSoup
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
    TemplateManager,
)
from utils import time
from utils.emails import get_email_context, get_from_address
from utils.logging import setLogger
from utils.pdf import append_attachment
from utils.stats import get_all_customer_stats, get_cycle_stats
from utils.templates import get_indicators

logger = setLogger(__name__)

customer_manager = CustomerManager()
cycle_manager = CycleManager()
recommendation_manager = RecommendationManager()
sending_profile_manager = SendingProfileManager()
subscription_manager = SubscriptionManager()
template_manager = TemplateManager()


def get_report(cycle_id: str, report_type: str, nonhuman: bool = False):
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
            "buffer_time_minutes",
        ],
    )
    customer = customer_manager.get(document_id=subscription["customer_id"])
    get_cycle_stats(cycle)
    previous_cycles = get_previous_cycles(cycle)
    recommendations = recommendation_manager.all()
    red_flags = [rec for rec in recommendations if rec["type"] == "red_flag"]
    sophisticated_techniques = [
        rec for rec in recommendations if rec["type"] == "sophisticated"
    ]
    n_recs_per_page = 9

    all_customer_stats = get_all_customer_stats()

    context = {
        "stats": cycle["nonhuman_stats"] if nonhuman else cycle["stats"],
        "cycle": cycle,
        "subscription": subscription,
        "customer": customer,
        "previous_cycles": previous_cycles,
        "first_cycle": len(previous_cycles) > 0,
        "recommendations": recommendations,
        "red_flags_paginated": [
            red_flags[i * n_recs_per_page : (i + 1) * n_recs_per_page]
            for i in range((len(red_flags) + n_recs_per_page - 1) // n_recs_per_page)
        ],
        "sophisticated_techniques_paginated": [
            sophisticated_techniques[i * n_recs_per_page : (i + 1) * n_recs_per_page]
            for i in range(
                (len(sophisticated_techniques) + n_recs_per_page - 1) // n_recs_per_page
            )
        ],
        "compare_svg": compare_svg,
        "percent_svg": percent_svg,
        "percent": percent,
        "preview_template": preview_template,
        "preview_from_address": preview_from_address,
        "preview_html": preview_html,
        "all_customer_stats": all_customer_stats,
        "all_cycles_click_percents_str": str(
            [percent(ratio) for ratio in all_customer_stats["all"]["clicked"]["ratios"]]
        )[1:-1],
        "indicators": get_indicators(),
        "datetime": datetime,
        "timedelta": timedelta,
        "json": json,
        "str": str,
        "time": time,
        "getMaxTemplateLevel": _get_max_by_template_level,
        "_get_subject_from_template_level": _get_subject_from_template_level,
    }
    return render_template(f"reports/{report_type}.html", **context)


def get_report_pdf(
    cycle: dict,
    report_type: str,
    pw: str = "",
    nonhuman: bool = False,
):
    """Get report pdf."""
    cycle_id = cycle["_id"]
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
        logger.error(f"Expected path {filepath} does not exist")
        raise Exception("Reporting Exception - Check Logs")

    writer = PdfFileWriter()
    reader = PdfFileReader(open(filepath, "rb"))
    for i in range(0, reader.getNumPages()):
        writer.addPage(reader.getPage(i))
    if pw:
        writer.encrypt(pw, use_128bit=True)

    if report_type == "cycle":
        # add csv pages
        _add_csv_attachments(writer=writer, cycle=cycle)
        # add table of contents links
        _add_toc_links(writer=writer, n=len(cycle["stats"].get("template_stats", 0)))
        # add section 1 links
        _add_section1_links(
            writer=writer, n=len(cycle["stats"].get("template_stats", 0))
        )

    output = open(new_filepath, "wb")
    writer.write(output)
    output.close()
    os.remove(filepath)

    return new_filepath


def _add_csv_attachments(writer: PdfFileWriter, cycle: dict):
    """Add CSV attachments to PDF."""
    # Note: csv_data list must be in alphabetical order
    csv_data = [
        _add_indicator_stats_csv,
        _add_overall_stats_csv,
        _add_template_stats_csv,
        _add_time_stats_csv,
        _user_group_stats_csv,
    ]

    for func in csv_data:
        filename, headers, data = func(cycle=cycle)
        csv_file = StringIO()
        csv_writer = csv.DictWriter(csv_file, fieldnames=headers)
        csv_writer.writeheader()

        if isinstance(data, list):
            csv_writer.writerows(data)
        else:
            csv_writer.writerow(data)

        append_attachment(writer, filename, csv_file.getvalue().encode())
        csv_file.close()


def _add_toc_links(writer: PdfFileWriter, n: int):
    pagelinks = [3, 4, 5, 6, 7, 8, 9, 9 + n, 10 + n, 11 + n, 12 + n, 13 + n]
    rect = [65, 495, 550, 515]
    gap = 39
    for i in range(len(pagelinks)):
        writer.add_link(pagenum=(2) - 1, pagedest=pagelinks[i] - 1, rect=rect)

        rect[1] = rect[1] - gap
        rect[3] = rect[3] - gap


def _add_section1_links(writer: PdfFileWriter, n: int):
    writer.add_link(pagenum=(3) - 1, pagedest=(4) - 1, rect=[95, 563, 285, 578])
    writer.add_link(pagenum=(3) - 1, pagedest=(5) - 1, rect=[95, 502, 384, 517])
    writer.add_link(pagenum=(3) - 1, pagedest=(6) - 1, rect=[95, 428, 515, 443])
    writer.add_link(pagenum=(3) - 1, pagedest=(7) - 1, rect=[95, 367, 352, 382])
    writer.add_link(pagenum=(3) - 1, pagedest=(9) - 1, rect=[95, 292, 306, 307])
    writer.add_link(pagenum=(3) - 1, pagedest=(12 + n) - 1, rect=[308, 233, 435, 247])


def _add_overall_stats_csv(cycle: dict) -> Tuple[str, List[str], Any]:
    """Add Top Level Stats CSV attachment to PDF."""
    stats = cycle["stats"]

    average_click_time = stats["stats"]["all"]["clicked"]["average"]
    average_click_time_string = (
        f"{average_click_time} minutes"
        if average_click_time < 60
        else f"{round(average_click_time / 60)} hours"
    )
    data = {
        "Start Date": datetime.strftime(cycle["start_date"], "%m/%d/%Y, %H:%M:%S"),
        "End Date": datetime.strftime(cycle["end_date"], "%m/%d/%Y, %H:%M:%S"),
        "Average Click Time": average_click_time_string,
        "Low Sent": stats["stats"]["low"]["sent"]["count"],
        "Low Opened": stats["stats"]["low"]["opened"]["count"],
        "Low Clicked": stats["stats"]["low"]["clicked"]["count"],
        "Moderate Sent": stats["stats"]["moderate"]["sent"]["count"],
        "Moderate Opened": stats["stats"]["moderate"]["opened"]["count"],
        "Moderate Clicked": stats["stats"]["moderate"]["clicked"]["count"],
        "High Sent": stats["stats"]["high"]["sent"]["count"],
        "High Opened": stats["stats"]["high"]["opened"]["count"],
        "High Clicked": stats["stats"]["high"]["clicked"]["count"],
        "All Sent": stats["stats"]["all"]["sent"]["count"],
        "All Opened": stats["stats"]["all"]["opened"]["count"],
        "All Clicked": stats["stats"]["all"]["clicked"]["count"],
    }
    headers = list(data.keys())

    return "overall_stats.csv", headers, data


def _user_group_stats_csv(cycle: dict) -> Tuple[str, List[str], List[Any]]:
    """Add User Group Stats CSV attachment to PDF."""
    stats = cycle["stats"]

    if not stats.get("target_stats"):
        return "user_group_stats.csv", [], []

    data = [
        {
            "Group": t["group"] if t["group"] else "not grouped",
            "All Sent": t["sent"]["count"],
            "All Opened": t["opened"]["count"],
            "All Clicked": t["clicked"]["count"],
        }
        for t in stats["target_stats"]
        if t["sent"]["count"] > 5
    ]
    if len(data) == 0:
        data = [
            {
                "Message": "To protect the anonymity of participants, data can only be displayed for groups with over 5 members. This cycle does not have any qualifying groups.",
            }
        ]
    headers = list(data[0].keys())
    return "user_group_stats.csv", headers, data


def _add_time_stats_csv(cycle: dict) -> Tuple[str, List[str], Any]:
    """Add Time Stats CSV attachment to PDF."""
    stats = cycle["stats"]
    data = {
        "Opened one_minute": stats["time_stats"]["opened"]["one_minutes"]["count"],
        "Opened three_minutes": stats["time_stats"]["opened"]["three_minutes"]["count"],
        "Opened five_minutes": stats["time_stats"]["opened"]["five_minutes"]["count"],
        "Opened fifteen_minutes": stats["time_stats"]["opened"]["fifteen_minutes"][
            "count"
        ],
        "Opened thirty_minutes": stats["time_stats"]["opened"]["thirty_minutes"][
            "count"
        ],
        "Opened sixty_minutes": stats["time_stats"]["opened"]["sixty_minutes"]["count"],
        "Opened two_hours": stats["time_stats"]["opened"]["two_hours"]["count"],
        "Opened three_hours": stats["time_stats"]["opened"]["three_hours"]["count"],
        "Opened four_hours": stats["time_stats"]["opened"]["four_hours"]["count"],
        "Opened one_day": stats["time_stats"]["opened"]["one_day"]["count"],
        "Clicked one_minute": stats["time_stats"]["clicked"]["one_minutes"]["count"],
        "Clicked three_minutes": stats["time_stats"]["clicked"]["three_minutes"][
            "count"
        ],
        "Clicked five_minutes": stats["time_stats"]["clicked"]["five_minutes"]["count"],
        "Clicked fifteen_minutes": stats["time_stats"]["clicked"]["fifteen_minutes"][
            "count"
        ],
        "Clicked thirty_minutes": stats["time_stats"]["clicked"]["thirty_minutes"][
            "count"
        ],
        "Clicked sixty_minutes": stats["time_stats"]["clicked"]["sixty_minutes"][
            "count"
        ],
        "Clicked two_hours": stats["time_stats"]["clicked"]["two_hours"]["count"],
        "Clicked three_hours": stats["time_stats"]["clicked"]["three_hours"]["count"],
        "Clicked four_hours": stats["time_stats"]["clicked"]["four_hours"]["count"],
        "Clicked one_day": stats["time_stats"]["clicked"]["one_day"]["count"],
    }
    headers = list(data.keys())

    return "time_stats.csv", headers, data


def _add_template_stats_csv(cycle: dict) -> Tuple[str, List[str], List[Any]]:
    """Add Template Stats CSV attachment to PDF."""
    stats = cycle["stats"]
    subscription = subscription_manager.get(
        document_id=cycle.get("subscription_id"),
    )

    data = [
        {
            "Sent": stat["sent"]["count"],
            "Opened": stat["opened"]["count"],
            "Clicked": stat["clicked"]["count"],
            "Average time to first click (HH:MM:SS)": time.convert_seconds(
                stats["stats"][stat["deception_level"]]["clicked"]["average"]
            ).HH_MM_SS,
            "Deception level": stat["deception_level"],
            "Subject": stat["template"]["subject"],
            "From address": stat["template"]["from_address"].split("@")[0]
            + "@"
            + get_from_domain(stat["template"], subscription)
            + ">",
        }
        for stat in stats["template_stats"]
    ]

    headers = list(data[0].keys())

    return "template_stats.csv", headers, data


def _add_indicator_stats_csv(cycle: dict) -> Tuple[str, List[str], List[Any]]:
    """Add Indicator Stats CSV attachment to PDF."""
    stats = cycle["stats"]

    def _get_deception_level(templates: list) -> dict:
        """Return deception level of template."""
        low = False
        moderate = False
        high = False
        for template in templates:
            if template["deception_score"] in {1, 2}:
                low = True
            if template["deception_score"] in {3, 4}:
                moderate = True
            if template["deception_score"] in {5, 6}:
                high = True
        return {"low": low, "moderate": moderate, "high": high}

    data = [
        {
            "Indicator Name": stat["recommendation"]["title"],
            "Indicator Type": stat["recommendation"]["type"],
            "Sent": stat["sent"].get("count", 0),
            "Opened": stat["opened"].get("count", 0),
            "Clicked": stat["clicked"].get("count", 0),
            "Click Rate": f"{stat['clicked']['ratio']*100}%",
            "Open Rate": f"{stat['opened']['ratio']*100}%",
            "Included in Low Template": "yes" if decep_level["low"] else "no",
            "Included in Moderate Template": "yes" if decep_level["moderate"] else "no",
            "Included in High Template": "yes" if decep_level["high"] else "no",
        }
        for stat in stats["recommendation_stats"]
        if (decep_level := _get_deception_level(stat["templates"]))
    ]

    headers = list(data[0].keys()) if data else []

    return "indicator_stats.csv", headers, data


def get_reports_sent():
    """Get reports sent."""
    response = {
        "status_reports_sent": 0,
        "cycle_reports_sent": 0,
        "yearly_reports_sent": 0,
    }

    pipeline = [
        {"$match": {"archived": {"$ne": True}}},
        {"$unwind": "$notification_history"},
        {"$group": {"_id": "$notification_history.message_type", "count": {"$sum": 1}}},
        {
            "$group": {
                "_id": None,
                "message_type": {"$push": {"k": "$_id", "v": "$count"}},
            }
        },
        {"$replaceRoot": {"newRoot": {"$arrayToObject": "$message_type"}}},
    ]

    data = subscription_manager.aggregate(pipeline)
    if data:
        data = data[0]
        if "status_report" in data:
            data["status_reports_sent"] = data.pop("status_report")
        if "cycle_report" in data:
            data["cycle_reports_sent"] = data.pop("cycle_report")
        if "yearly_report" in data:
            data["yearly_reports_sent"] = data.pop("yearly_report")
        response.update(data)

    return response


def get_sector_industry_report():
    """Get reports on sector industries."""
    response = {
        "federal_stats": {
            "subscription_count": 0,
            "cycle_count": 0,
            "emails_sent": 0,
            "emails_clicked": 0,
            "emails_clicked_ratio": 0,
        },
        "state_stats": {
            "subscription_count": 0,
            "cycle_count": 0,
            "emails_sent": 0,
            "emails_clicked": 0,
            "emails_clicked_ratio": 0,
        },
        "local_stats": {
            "subscription_count": 0,
            "cycle_count": 0,
            "emails_sent": 0,
            "emails_clicked": 0,
            "emails_clicked_ratio": 0,
        },
        "tribal_stats": {
            "subscription_count": 0,
            "cycle_count": 0,
            "emails_sent": 0,
            "emails_clicked": 0,
            "emails_clicked_ratio": 0,
        },
        "private_stats": {
            "subscription_count": 0,
            "cycle_count": 0,
            "emails_sent": 0,
            "emails_clicked": 0,
            "emails_clicked_ratio": 0,
        },
    }

    for stat in response.keys():
        customers = [
            c["_id"]
            for c in customer_manager.all(
                params={
                    "customer_type": stat.split("_")[0].capitalize(),
                    "archived": {"$ne": True},
                },
                fields=["_id"],
            )
        ]
        subscriptions = [
            s["_id"]
            for s in subscription_manager.all(
                params={"customer_id": {"$in": customers}, "archived": {"$ne": True}},
                fields=["_id"],
            )
        ]
        if subscriptions:
            response[stat]["subscription_count"] = subscription_manager.count(
                {"customer_id": {"$in": customers}}
            )
            response[stat]["cycle_count"] = cycle_manager.count(
                {"subscription_id": {"$in": subscriptions}}
            )
            sent_aggregate = cycle_manager.aggregate(
                [
                    {"$match": {"subscription_id": {"$in": subscriptions}}},
                    {
                        "$group": {
                            "_id": None,
                            "sent": {"$sum": "$stats.stats.all.sent.count"},
                        }
                    },
                ]
            )
            try:
                response[stat]["emails_sent"] = sent_aggregate[0]["sent"]
            except IndexError:
                response[stat]["emails_sent"] = 0
            clicked_aggregate = cycle_manager.aggregate(
                [
                    {"$match": {"subscription_id": {"$in": subscriptions}}},
                    {
                        "$group": {
                            "_id": None,
                            "clicked": {"$sum": "$stats.stats.all.clicked.count"},
                        }
                    },
                ]
            )
            try:
                response[stat]["emails_clicked"] = clicked_aggregate[0]["clicked"]
            except IndexError:
                response[stat]["emails_clicked"] = 0
            try:
                clicked_ratio = (
                    response[stat]["emails_clicked"] / response[stat]["emails_sent"]
                )
            except ZeroDivisionError:
                clicked_ratio = 0

            response[stat]["emails_clicked_ratio"] = round(clicked_ratio, 4)

    return response


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


def _get_max_by_template_level(low_metric, moderate_metric, high_metric):
    """Get Most Clicked Template Level for report."""
    levels = {
        "Low": low_metric,
        "Moderate": moderate_metric,
        "High": high_metric,
    }
    return max(levels, key=levels.get)


def _get_subject_from_template_level(template_stats, level):
    """Get Subject Line from Template Level."""
    template = next(
        (t for t in template_stats if t.get("deception_level") == level), None
    )
    if template:
        return template.get("template").get("subject")
    else:
        return ""


def preview_from_address(template, subscription, customer):
    """Preview from address in a report."""
    template = template_manager.get(
        document_id=template["_id"], fields=["from_address", "sending_profile_id"]
    )
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


def get_from_domain(template, subscription):
    """Get from domain for template_stats.csv."""
    template = template_manager.get(
        document_id=template["_id"], fields=["from_address", "sending_profile_id"]
    )
    if template.get("sending_profile_id"):
        sending_profile = sending_profile_manager.get(
            document_id=template["sending_profile_id"]
        )
    else:
        sending_profile = sending_profile_manager.get(
            document_id=subscription["sending_profile_id"]
        )
    if type(sending_profile) is dict:
        sp_from = sending_profile["from_address"]
    else:
        sp_from = sending_profile.from_address
    sp_domain = sp_from.split("<")[-1].split("@")[1].replace(">", "")
    return sp_domain


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


def preview_html(html, customer):
    """Prepare html for cycle report viewing."""
    # Remove click links from raw html
    soup = BeautifulSoup(html, features="html.parser")
    while True:
        a = soup.find("a")
        if not a:
            break
        else:
            a["style"] = "color: blue"
            del a["href"]
            a.name = "span"
    html = str(soup)

    # Use fake data in html
    fake = Faker()
    context_keys = re.findall(r"\{\{(.*?)\}\}", html)
    context = {
        "target['first_name']": fake.first_name(),
        "target['last_name']": fake.last_name(),
        "url": "areallyfakeURL.com",
    }
    domain = customer.get("domain", "@example.com")
    context["target['email']"] = (
        context["target['first_name']"]
        + "."
        + context["target['last_name']"]
        + "@"
        + domain
    )

    for i in context_keys:
        if i not in context.keys():
            try:
                if i[0:6] == "target":
                    context[i] = str(i)
                elif i[0:4] == "fake":
                    try:
                        context[i] = eval(i + "()")  # nosec
                    except NameError as e:
                        logger.exception(e)
                        context[i] = str(i)
                else:
                    try:
                        context[i] = eval(i)  # nosec
                    except NameError as e:
                        logger.exception(e)
                        context[i] = str(i)
            except Exception as e:
                logger.exception(e)
                context[i] = str(i)

    return re.sub(
        r"\{\{(.*?)\}\}",
        lambda match: str(context[match.group(1)])
        if match.group(1) in context
        else f"{match.group(1)}",
        html,
    )


def percent(ratio):
    """Get percentage from ratio."""
    return round(ratio * 100, 1)


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
                        stroke: #000000;
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
                        stroke: #000000;
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
                        stroke: #000000;
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
    try:
        return round(
            (current_percent - previous_percent) / abs(previous_percent) * 100, 2
        )
    except ZeroDivisionError:
        return 0


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
                        stroke: #000000;
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
                        stroke: #000000;
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

    neutral_svg = """
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 22" style="width: 50px; height: 60px">
            <g id="Layer_2" data-name="Layer 2">
                <g id="Layer_1-2" data-name="Layer 1">
                <polygon
                    style="
                        fill: #006c9c;
                        stroke: #000000;
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

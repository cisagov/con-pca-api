"""Cycles Util."""
# Standard Python Libraries
import logging

# Third-Party Libraries
from api.utils.generic import format_ztime

logger = logging.getLogger()


def get_reported_emails(subscription):
    """Get Reported Emails.

    Args:
        subscription (object): subscription object

    Returns:
        list: list of all cycles and thair reported emails
    """
    list_data = subscription["gophish_campaign_list"]
    reports_per_campaign = []
    for campaign in list_data:
        timeline = campaign["timeline"]
        filtered_list = [d for d in timeline if d["message"] == "Email Reported"]
        reported_emails = []
        for item in filtered_list:
            reported_emails.append(
                {
                    "campaign_id": campaign["campaign_id"],
                    "email": item["email"],
                    "date": item["time"],
                }
            )
        reports_per_campaign.append(
            {
                "campaign_id": campaign["campaign_id"],
                "reported_emails": reported_emails,
            }
        )

    master_list = []
    for c in subscription["cycles"]:
        emails_reported_per_cycle = []
        c_list = c["campaigns_in_cycle"]
        for reports in reports_per_campaign:
            if reports["campaign_id"] in c_list:
                emails_reported_per_cycle.extend(reports["reported_emails"])

        report_count = len(emails_reported_per_cycle)
        c["phish_results"]["reported"] = report_count

        cycle_reported_emails = {
            "start_date": c["start_date"],
            "end_date": c["end_date"],
            "email_list": emails_reported_per_cycle,
            "override_total_reported": c["override_total_reported"],
            "cycle_uuid": c["cycle_uuid"]
        }
        master_list.append(cycle_reported_emails)

    return master_list, subscription


def delete_reported_emails(subscription, data):
    """Delete Reported Emails.

    Args:
        gophish_campaign_list (list): list of gophish campaigns
        delete_list (list): list of objects to be deleted.

    Returns:
        list: updated gophish campaign list
    """
    cycle = get_cycle(subscription, data)
    gophish_campaign_list = subscription["gophish_campaign_list"]

    if cycle is None:
        return gophish_campaign_list
    campaigns_in_cycle = cycle["campaigns_in_cycle"]
    delete_list = data["delete_list"]
    delete_list_campaigns = [email["campaign_id"] for email in delete_list]

    for campaign in gophish_campaign_list:
        if (
            campaign["campaign_id"] in delete_list_campaigns
            and campaign["campaign_id"] in campaigns_in_cycle
        ):
            for item_to_delete in delete_list:
                if item_to_delete["campaign_id"] == campaign["campaign_id"]:
                    for timeline_item in campaign["timeline"]:
                        if (
                            timeline_item["email"] == item_to_delete["email"]
                            and timeline_item["message"] == "Email Reported"
                        ):
                            campaign["timeline"].remove(timeline_item)

    return gophish_campaign_list


def update_reported_emails(subscription, data):
    """Update Reported Emails.

    Args:
        gophish_campaign_list (list): list of gophish campaigns
        update_list (list): list of objects to be Updated or to add.

    Returns:
        list: updated gophish campaign list
    """
    cycle = get_cycle(subscription, data)
    gophish_campaign_list = subscription["gophish_campaign_list"]

    if cycle is None:
        return gophish_campaign_list

    campaigns_in_cycle = cycle["campaigns_in_cycle"]

    update_list = data["update_list"]
    update_list_campaigns = add_email_reports = []

    for email in update_list:
        if email["campaign_id"] is not None:
            update_list_campaigns.append(email)
        else:
            add_email_reports.append(email)

    for campaign in gophish_campaign_list:
        campaign_targets = [target["email"] for target in campaign["target_email_list"]]
        if (
            campaign["campaign_id"] in update_list_campaigns
            and campaign["campaign_id"] in campaigns_in_cycle
        ):
            for item_to_update in update_list:
                if item_to_update["campaign_id"] == campaign["campaign_id"]:
                    for timeline_item in campaign["timeline"]:
                        if (
                            timeline_item["email"] == item_to_update["email"]
                            and timeline_item["message"] == "Email Reported"
                        ):
                            timeline_item.update(
                                {"time": format_ztime(item_to_update["date"])}
                            )

        for new_reported_email in add_email_reports:
            exixting_timeline_reports = [
                timeline_item["email"]
                for timeline_item in campaign["timeline"]
                if timeline_item["message"] == "Email Reported"
            ]
            if (
                new_reported_email["email"] in campaign_targets
                and new_reported_email["email"] not in exixting_timeline_reports
            ):
                campaign["timeline"].append(
                    {
                        "email": new_reported_email["email"],
                        "message": "Email Reported",
                        "time": format_ztime(new_reported_email["date"]),
                        "details": "",
                        "duplicate": False,
                    }
                )

    return gophish_campaign_list


def override_total_reported(subscription, cycle_data_override):
    """Override Total Reported.

    Args:
        subscription (dict): subscription object
        cycle_data_override (dict): cycle post data

    Returns:
        subscription: subscription object
    """
    cycle = get_cycle(subscription, cycle_data_override)

    if cycle is None or "override_total_reported" not in cycle_data_override:
        return subscription

    if cycle_data_override["override_total_reported"] is None:
        cycle["override_total_reported"] = -1
    else:
        cycle["override_total_reported"] = cycle_data_override[
            "override_total_reported"
        ]

    return subscription


def get_cycle(subscription, cycle_data_override):
    """Get Cycle."""
    cycle_start = cycle_data_override["start_date"].split("T")[0]
    cycle_end = cycle_data_override["end_date"].split("T")[0]
    cycle = next(
        (
            cycle
            for cycle in subscription["cycles"]
            if cycle["start_date"].strftime("%Y-%m-%d") == cycle_start
            and cycle["end_date"].strftime("%Y-%m-%d") == cycle_end
        ),
        None,
    )

    return cycle

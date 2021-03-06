"""Cycles Util."""
# Standard Python Libraries
from datetime import datetime

# cisagov Libraries
from api.services import CampaignService, SubscriptionService
from api.utils.generic import format_ztime

campaign_service = CampaignService()
subscription_service = SubscriptionService()


def get_reported_emails(subscription):
    """
    Get Reported Emails.

    Args:
        subscription (object): subscription object

    Returns:
        list: list of all cycles and their reported emails
    """
    campaign_reports = []
    for campaign in subscription["campaigns"]:
        campaign_reports.append(get_campaign_reports(campaign))

    cycle_reports = []
    for cycle in subscription.get("cycles", []):
        cycle_reports.append(get_cycle_reports(cycle, campaign_reports))

    return cycle_reports


def get_campaign_reports(campaign):
    """Get Campaign Reports."""
    reported_emails = []
    for item in campaign["timeline"]:
        if item["message"] == "Email Reported":
            reported_emails.append(
                {
                    "campaign_id": campaign["campaign_id"],
                    "email": item["email"],
                    "date": item["time"],
                }
            )
    return {"campaign_id": campaign["campaign_id"], "reported_emails": reported_emails}


def get_cycle_reports(cycle, campaign_reports):
    """Get Cycle Reports."""
    cycle_reports = []
    for reports in campaign_reports:
        if reports["campaign_id"] in cycle["campaigns_in_cycle"]:
            cycle_reports.extend(reports["reported_emails"])

    report_count = len(cycle_reports)
    cycle["phish_results"]["reported"] = report_count
    return {
        "start_date": cycle["start_date"],
        "end_date": cycle["end_date"],
        "email_list": cycle_reports,
        "override_total_reported": cycle.get("override_total_reported", -1),
        "cycle_uuid": cycle["cycle_uuid"],
    }


def delete_reported_emails(subscription, data):
    """
    Delete Reported Emails.

    Args:
        campaigns (list): list of gophish campaigns
        delete_list (list): list of objects to be deleted.

    Returns:
        list: updated gophish campaign list
    """
    cycle = get_cycle(subscription, data)

    if cycle is None:
        return subscription["campaigns"]
    campaigns_in_cycle = cycle["campaigns_in_cycle"]
    delete_list_campaigns = [email["campaign_id"] for email in data["delete_list"]]

    for campaign in subscription["campaigns"]:
        if (
            campaign["campaign_id"] in delete_list_campaigns
            and campaign["campaign_id"] in campaigns_in_cycle
        ):
            for item_to_delete in data["delete_list"]:
                if item_to_delete["campaign_id"] == campaign["campaign_id"]:
                    for timeline_item in campaign["timeline"]:
                        if (
                            timeline_item["email"] == item_to_delete["email"]
                            and timeline_item["message"] == "Email Reported"
                        ):
                            campaign["timeline"].remove(timeline_item)
                            campaign_service.update(
                                campaign["campaign_uuid"],
                                {"timeline": campaign["timeline"]},
                            )


def update_reported_emails(subscription, data):
    """
    Update Reported Emails.

    Args:
        campaigns (list): list of gophish campaigns
        update_list (list): list of objects to be Updated or to add.

    Returns:
        list: updated gophish campaign list
    """
    cycle = get_cycle(subscription, data)

    if cycle is None:
        return

    update_list_campaigns = []
    add_email_reports = []

    for email in data["update_list"]:
        if email.get("campaign_id"):
            update_list_campaigns.append(email["campaign_id"])
        else:
            add_email_reports.append(email)

    for campaign in subscription["campaigns"]:
        campaign_targets = [target["email"] for target in campaign["target_email_list"]]
        if (
            campaign["campaign_id"] in update_list_campaigns
            and campaign["campaign_id"] in cycle["campaigns_in_cycle"]
        ):
            for item_to_update in data["update_list"]:
                if item_to_update.get("campaign_id") == campaign["campaign_id"]:
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

        campaign_service.update(
            campaign["campaign_uuid"], {"timeline": campaign["timeline"]}
        )


def override_total_reported(subscription, cycle_data_override):
    """
    Override Total Reported.

    Args:
        subscription (dict): subscription object
        cycle_data_override (dict): cycle post data

    Returns:
        subscription: subscription object
    """
    cycle = get_cycle(subscription, cycle_data_override)

    if cycle is None or "override_total_reported" not in cycle_data_override:
        return

    if cycle_data_override["override_total_reported"] is None:
        cycle["override_total_reported"] = -1
    else:
        cycle["override_total_reported"] = cycle_data_override[
            "override_total_reported"
        ]

    subscription_service.update_nested(
        uuid=subscription["subscription_uuid"],
        field="cycles.$.override_total_reported",
        data=cycle["override_total_reported"],
        params={"cycles.cycle_uuid": cycle["cycle_uuid"]},
    )


def get_cycle(subscription, cycle_data_override):
    """Get Cycle."""
    return next(
        filter(
            lambda x: x["cycle_uuid"] == cycle_data_override["cycle_uuid"],
            subscription["cycles"],
        )
    )


def get_last_run_cycle(cycles):
    """Get Last Run Cycle."""
    now = datetime.now()
    return min(
        cycles,
        key=lambda x: abs(
            x["end_date"].replace(tzinfo=None) - now.replace(tzinfo=None)
        ),
    )

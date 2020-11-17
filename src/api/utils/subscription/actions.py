import logging
import uuid
import random

from api.manager import CampaignManager
from api.utils.subscription.campaigns import (
    generate_campaigns,
    stop_campaigns,
)
from api.utils.subscription.subscriptions import (
    calculate_subscription_start_end_date,
    init_subscription_tasks,
    create_subscription_name,
    get_subscription_cycles,
    send_stop_notification,
    get_staggered_dates_in_range,
)
from api.utils.subscription.targets import batch_targets
from api.utils.subscription.template_selector import personalize_template_batch
from api.utils.template.templates import deception_level
from api.services import (
    CustomerService,
    SubscriptionService,
    LandingPageService,
    CampaignService,
)

# GoPhish Campaign Manager
campaign_manager = CampaignManager()
customer_service = CustomerService()
subscription_service = SubscriptionService()
landing_page_service = LandingPageService()
campaign_service = CampaignService()


def create_subscription(subscription):
    customer = customer_service.get(subscription["customer_uuid"])

    subscription["name"] = create_subscription_name(customer)
    subscription["tasks"] = [
        {
            "task_uuid": str(uuid.uuid4()),
            "message_type": "start_subscription",
            "scheduled_date": subscription["start_date"],
            "executed": False,
        }
    ]
    _, end_date = calculate_subscription_start_end_date(subscription.get("start_date"))

    subscription["status"] = "Queued"
    response = subscription_service.save(subscription)
    response["name"] = subscription["name"]
    return response


def restart_subscription(subscription_uuid):
    subscription = subscription_service.get(subscription_uuid)
    data = {
        "status": "Queued",
        "tasks": [
            {
                "task_uuid": str(uuid.uuid4()),
                "message_type": "start_subscription",
                "scheduled_date": subscription["start_date"],
                "executed": False,
            }
        ],
    }

    _, end_date = calculate_subscription_start_end_date(subscription.get("start_date"))

    return subscription_service.update(subscription_uuid, data)


def start_subscription(subscription_uuid, new_cycle=False):
    """
    Returns a subscription from database.

    Parameters:
        data (dict): posted data of subscription to start.
        subscription_uuid (str): uuid of subscription to restart.

    Returns:
        dict: returns response of updated/created subscription from database.
    """
    subscription = subscription_service.get(subscription_uuid)

    if new_cycle:
        stop_campaigns(subscription["campaigns"])

    # calculate start and end date to subscription
    start_date, end_date = calculate_subscription_start_end_date(
        subscription.get("start_date")
    )

    # Get details for the customer that is attached to the subscription
    customer = customer_service.get(subscription["customer_uuid"])

    # Divide stagger each start date and randomize:
    if subscription["stagger_emails"]:
        date_list = get_staggered_dates_in_range(start_date, 3)
        date_list = random.sample(date_list, len(date_list))
    else:
        date_list = [start_date, start_date, start_date]

    # Create the needed subscription levels to fill.
    sub_levels = {
        "high": {
            "start_date": date_list[0],
            "end_date": end_date,
            "template_targets": {},
            "template_uuids": [],
            "personalized_templates": [],
            "targets": [],
            "deception_level": deception_level.get("high"),
        },
        "moderate": {
            "start_date": date_list[1],
            "end_date": end_date,
            "template_targets": {},
            "template_uuids": [],
            "personalized_templates": [],
            "targets": [],
            "deception_level": deception_level.get("moderate"),
        },
        "low": {
            "start_date": date_list[2],
            "end_date": end_date,
            "template_targets": {},
            "template_uuids": [],
            "personalized_templates": [],
            "targets": [],
            "deception_level": deception_level.get("low"),
        },
    }

    # get personalized and selected template_uuids
    sub_levels = personalize_template_batch(customer, subscription, sub_levels)

    # get targets assigned to each group
    batch_targets(subscription, sub_levels)

    # Get all Landing pages or default
    # This is currently selecting the default page on creation.
    landing_page = "Phished"
    parameters = {}
    parameters["is_default_template"] = True
    landing_pages = landing_page_service.get_list(parameters)
    for page in landing_pages:
        if page["is_default_template"]:
            landing_page = page["name"]

    cycle_uuid = str(uuid.uuid4())
    new_gophish_campaigns = generate_campaigns(
        subscription, landing_page, sub_levels, cycle_uuid
    )

    selected_templates = []
    for v in sub_levels.values():
        selected_templates.extend(list(v["template_targets"].keys()))
    subscription["templates_selected_uuid_list"] = selected_templates

    subscription["end_date"] = end_date.strftime("%Y-%m-%dT%H:%M:%S")
    subscription["status"] = "In Progress"
    if not subscription.get("cycles"):
        subscription["cycles"] = []

    total_targets_in_cycle = len(subscription["target_email_list"])
    subscription["cycles"].append(
        get_subscription_cycles(
            new_gophish_campaigns,
            start_date,
            end_date,
            cycle_uuid,
            total_targets_in_cycle,
        )[0]
    )

    if not subscription.get("tasks"):
        subscription["tasks"] = []

    if len(subscription["tasks"]) <= 1:
        subscription["tasks"].extend(
            init_subscription_tasks(
                start_date, subscription.get("continuous_subscription")
            )
        )

    response = subscription_service.update(subscription_uuid, subscription)

    for campaign in new_gophish_campaigns:
        campaign["subscription_uuid"] = str(response["subscription_uuid"])
        campaign["cycle_uuid"] = str(cycle_uuid)
        campaign_service.save(campaign)

    return response


def stop_subscription(subscription):
    """
    Stops a given subscription.
    Returns updated subscription.
    """
    # Stop Campaigns
    stop_campaigns(subscription["campaigns"])

    try:
        send_stop_notification(subscription)
    except Exception as e:
        logging.exception(e)

    resp = subscription_service.update(
        subscription["subscription_uuid"],
        {
            "campaigns": subscription["campaigns"],
            "tasks": [],
            "templates_selected_uuid_list": [],
            "active": False,
            "manually_stopped": True,
            "status": "stopped",
        },
    )

    return resp

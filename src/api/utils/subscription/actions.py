"""Subscription Actions."""
# Standard Python Libraries
import logging
import uuid

# cisagov Libraries
from api.manager import CampaignManager
from api.services import (
    CampaignService,
    CustomerService,
    LandingPageService,
    SubscriptionService,
    TemplateService,
)
from api.utils.subscription.campaigns import generate_campaigns, stop_campaigns
from api.utils.subscription.subscriptions import (
    calculate_subscription_start_end_date,
    create_subscription_name,
    get_subscription_cycles,
    init_subscription_tasks,
    send_stop_notification,
)
from api.utils.subscription.targets import batch_targets
from api.utils.template.personalize import personalize_templates
from api.utils.template.templates import deception_level

# GoPhish Campaign Manager
campaign_manager = CampaignManager()
customer_service = CustomerService()
subscription_service = SubscriptionService()
landing_page_service = LandingPageService()
campaign_service = CampaignService()
template_service = TemplateService()


def create_subscription(subscription):
    """Create a subscription."""
    customer = customer_service.get(subscription["customer_uuid"])
    subscription["name"] = create_subscription_name(customer)
    subscription["status"] = "created"
    response = subscription_service.save(subscription)
    response["name"] = subscription["name"]
    return response


def launch_subscription(subscription_uuid):
    """Launch a created/stopped subscription."""
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

    return subscription_service.update(subscription_uuid, data)


def start_subscription(subscription_uuid, new_cycle=False):
    """Start a subscription."""
    subscription = subscription_service.get(subscription_uuid)
    templates = template_service.get_list({"retired": False})
    if new_cycle:
        stop_campaigns(subscription["campaigns"])

    # calculate start and end date to subscription
    start_date, end_date = calculate_subscription_start_end_date(
        subscription.get("start_date"), subscription.get("cycle_length_minutes", 129600)
    )

    # Get details for the customer that is attached to the subscription
    customer = customer_service.get(subscription["customer_uuid"])

    # Create the needed subscription levels to fill.
    sub_levels = {
        "high": {
            "start_date": start_date,
            "end_date": end_date,
            "template_targets": {},
            "template_uuids": subscription["templates_selected"]["high"],
            "personalized_templates": [],
            "targets": [],
            "deception_level": deception_level["high"],
        },
        "moderate": {
            "start_date": start_date,
            "end_date": end_date,
            "template_targets": {},
            "template_uuids": subscription["templates_selected"]["moderate"],
            "personalized_templates": [],
            "targets": [],
            "deception_level": deception_level["moderate"],
        },
        "low": {
            "start_date": start_date,
            "end_date": end_date,
            "template_targets": {},
            "template_uuids": subscription["templates_selected"]["low"],
            "personalized_templates": [],
            "targets": [],
            "deception_level": deception_level["low"],
        },
    }

    # get personalized and selected template_uuids
    sub_levels = personalize_templates(customer, subscription, templates, sub_levels)

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

    new_gophish_campaigns = generate_campaigns(subscription, landing_page, sub_levels)

    selected_templates = []
    for v in sub_levels.values():
        selected_templates.extend(list(v["template_targets"].keys()))
    subscription["templates_selected_uuid_list"] = selected_templates

    subscription["end_date"] = end_date.strftime("%Y-%m-%dT%H:%M:%S")
    subscription["status"] = "In Progress"
    if not subscription.get("cycles"):
        subscription["cycles"] = []

    total_targets_in_cycle = len(subscription["target_email_list"])
    cycle_uuid = str(uuid.uuid4())
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
                start_date,
                subscription.get("continuous_subscription"),
                subscription.get("cycle_length_minutes", 129600),
                subscription.get("report_frequency_minutes", 43200),
            )
        )

    response = subscription_service.update(subscription_uuid, subscription)

    for campaign in new_gophish_campaigns:
        campaign["subscription_uuid"] = str(response["subscription_uuid"])
        campaign["cycle_uuid"] = str(cycle_uuid)
        campaign_service.save(campaign)

    return response


def stop_subscription(subscription):
    """Stop a subscription."""
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

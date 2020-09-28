"""Subscription Util Actions."""

# Standard Python Libraries
import logging
import uuid
import numpy

# Third-Party Libraries
from api.manager import CampaignManager
from api.models.landing_page_models import LandingPageModel, validate_landing_page
from api.utils import db_utils as db
from api.utils.customer.customers import get_customer
from api.utils.subscription.campaigns import (
    generate_campaigns,
    stop_campaigns,
)
from api.utils.subscription.subscriptions import (
    calculate_subscription_start_end_date,
    init_subscription_tasks,
    create_subscription_name,
    get_subscription,
    get_subscription_cycles,
    get_subscription_status,
    send_stop_notification,
    update_subscription,
    save_subscription,
    get_staggered_dates_in_range,
)
from api.utils.subscription.targets import batch_targets
from api.utils.subscription.template_selector import personalize_template_batch
from api.utils.template.templates import deception_level

logger = logging.getLogger(__name__)

# GoPhish Campaign Manager
campaign_manager = CampaignManager()


def start_subscription(data=None, subscription_uuid=None, new_cycle=False):
    """
    Returns a subscription from database.

    Parameters:
        data (dict): posted data of subscription to start.
        subscription_uuid (str): uuid of subscription to restart.

    Returns:
        dict: returns response of updated/created subscription from database.
    """
    if subscription_uuid:
        subscription = get_subscription(subscription_uuid)
    else:
        subscription = data

    if new_cycle and subscription_uuid:
        stop_campaigns(subscription["gophish_campaign_list"])

    # calculate start and end date to subscription
    start_date, end_date = calculate_subscription_start_end_date(
        subscription.get("start_date")
    )

    # Get details for the customer that is attached to the subscription
    customer = get_customer(subscription["customer_uuid"])

    # Divide stagger each start date and randomize:
    if subscription["stagger_emails"]:
        date_list = get_staggered_dates_in_range(start_date, end_date, 3)
        numpy.random.shuffle(date_list)
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

    # if a new subscription is being created, a name needs generated.
    if not subscription_uuid:
        subscription["name"] = create_subscription_name(customer)

    # get personalized and selected template_uuids
    sub_levels = personalize_template_batch(customer, subscription, sub_levels)

    # get targets assigned to each group
    sub_levels = batch_targets(subscription, sub_levels)

    # Get all Landing pages or default
    # This is currently selecting the default page on creation.
    landing_page = "Phished"
    parameters = {}
    parameters["is_default_template"] = True
    landing_pages = db.get_list(
        parameters, "landing_page", LandingPageModel, validate_landing_page
    )
    for page in landing_pages:
        if page["is_default_template"]:
            landing_page = page["name"]

    cycle_uuid = str(uuid.uuid4())
    new_gophish_campaigns = generate_campaigns(
        subscription, landing_page, sub_levels, cycle_uuid
    )
    if "gophish_campaign_list" not in subscription:
        subscription["gophish_campaign_list"] = []
    subscription["gophish_campaign_list"].extend(new_gophish_campaigns)

    selected_templates = []
    for v in sub_levels.values():
        selected_templates.extend(list(v["template_targets"].keys()))
    subscription["templates_selected_uuid_list"] = selected_templates

    subscription["end_date"] = end_date.strftime("%Y-%m-%dT%H:%M:%S")
    subscription["status"] = get_subscription_status(start_date)
    if "cycles" not in subscription:
        subscription["cycles"] = []
    subscription["cycles"].append(
        get_subscription_cycles(
            new_gophish_campaigns, start_date, end_date, cycle_uuid,
        )[0]
    )

    if not subscription.get("tasks"):
        logging.info("setting tasks")
        subscription["tasks"] = init_subscription_tasks(start_date)

    if subscription_uuid:
        response = update_subscription(subscription_uuid, subscription)
    else:
        response = save_subscription(subscription)
        response["name"] = subscription["name"]

    return response


def stop_subscription(subscription):
    """
    Stops a given subscription.
    Returns updated subscription.
    """
    # Stop Campaigns
    stop_campaigns(subscription["gophish_campaign_list"])

    # Remove subscription tasks from the scheduler
    subscription["tasks"] = []

    # Update subscription
    subscription["templates_selected_uuid_list"] = []
    subscription["active"] = False
    subscription["manually_stopped"] = True

    subscription["status"] = "stopped"

    try:
        send_stop_notification(subscription)
    except Exception as e:
        logging.exception(e)

    resp = update_subscription(subscription["subscription_uuid"], subscription)

    return resp

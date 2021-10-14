"""Load Test Data."""
# Standard Python Libraries
import datetime as dt
import json
import os

# cisagov Libraries
from api.config import logger
from api.manager import (
    CustomerManager,
    CycleManager,
    SendingProfileManager,
    SubscriptionManager,
    TargetManager,
    TemplateManager,
)

current_dir = os.path.dirname(__file__)

customer_manager = CustomerManager()
cycle_manager = CycleManager()
sending_profile_manager = SendingProfileManager()
subscription_manager = SubscriptionManager()
target_manager = TargetManager()
template_manager = TemplateManager()


def open_json_file(file_name: str):
    """Open json file from path."""
    return open(os.path.join(current_dir, f"data/{file_name}"))


def load_sending_profile():
    """Load sample sending profile."""
    sending_profile = sending_profile_manager.get(
        filter_data={"name": "Test Sending Profile"}
    )
    if sending_profile:
        logger.info("Test data for sending profile already exists.")
        return sending_profile["_id"]

    with open_json_file("sending_profile.json") as json_file:
        logger.info("loading sending profile test data...")
        sending_profile = sending_profile_manager.save(json.load(json_file))

    return sending_profile["_id"]


def load_customer():
    """Load sample customer data."""
    customer = customer_manager.get({"name": "Test Customer"})
    if customer:
        logger.info("Test data for customer already exists.")
        return customer["_id"]

    with open_json_file("customer.json") as json_file:
        logger.info("loading customer test data...")
        customer = customer_manager.save(json.load(json_file))

    return customer["_id"]


def load_subscription():
    """Load sample subscription data."""
    subscription = subscription_manager.get({"name": "test_subscription"})
    if subscription:
        logger.info("Test data for subscription already exists.")
        return subscription["_id"], subscription["templates_selected"]

    template_ids = [template["_id"] for template in template_manager.all(limit=3)]
    with open_json_file("subscription.json") as json_file:
        logger.info("loading subscription test data...")

        load_data = json.load(json_file)
        load_data["start_date"] = dt.datetime.now()
        load_data["customer_id"] = load_customer()
        load_data["sending_profile_id"] = load_sending_profile()
        load_data["templates_selected"] = template_ids
        subscription = subscription_manager.save(load_data)

    return subscription["_id"], subscription["templates_selected"]


def load_cycle():
    """Load sample cycle data."""
    cycle = cycle_manager.get({"dirty_stats": True})
    if cycle:
        logger.info("Test data for cycle already exists.")
        return

    subscription_id, template_ids = load_subscription()
    with open_json_file("cycle.json") as json_file:
        logger.info("loading cycle test data...")

        load_data = json.load(json_file)
        load_data["subscription_id"] = subscription_id
        load_data["start_date"] = dt.datetime.now()
        load_data["end_date"] = dt.datetime.now() + dt.timedelta(days=90)
        load_data["send_by_date"] = dt.datetime.now() + dt.timedelta(days=90)
        load_data["template_ids"] = template_ids

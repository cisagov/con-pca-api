"""Load Test Data."""
# Standard Python Libraries
from datetime import datetime, timedelta
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
from utils.subscriptions import create_targets_from_list

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
        return subscription["_id"], subscription

    template_ids = [template["_id"] for template in template_manager.all(limit=3)]
    with open_json_file("subscription.json") as json_file:
        logger.info("loading subscription test data...")

        load_data = json.load(json_file)
        load_data["start_date"] = datetime.now()
        load_data["customer_id"] = load_customer()
        load_data["sending_profile_id"] = load_sending_profile()
        load_data["templates_selected"] = template_ids
        subscription = subscription_manager.save(load_data)

    return subscription["_id"], load_data


def load_cycle(subscription_id: str, template_ids: list):
    """Load sample cycle data."""
    cycle = cycle_manager.get(filter_data={"dirty_stats": True})
    if cycle:
        logger.info("Test data for cycle already exists.")
        return cycle["_id"], cycle

    with open_json_file("cycle.json") as json_file:
        logger.info("loading cycle test data...")

        load_data = json.load(json_file)
        load_data["subscription_id"] = subscription_id
        load_data["start_date"] = datetime.utcnow()
        load_data["end_date"] = datetime.utcnow() + timedelta(days=90)
        load_data["send_by_date"] = datetime.utcnow() + timedelta(days=90)
        load_data["template_ids"] = template_ids
        cycle = cycle_manager.save(load_data)

    return cycle["_id"], load_data


def load_test_data():
    """Load sample targets and any missing test data."""
    targets = target_manager.all()
    if len(targets) >= 4:
        logger.info("Test data for targets already exist.")
        return

    subscription_id, subscription_data = load_subscription()
    cycle_id, cycle_data = load_cycle(
        subscription_id, subscription_data["templates_selected"]
    )
    targets = create_targets_from_list(
        cycle_id=cycle_id,
        subscription_id=subscription_id,
        target_list=subscription_data["target_email_list"],
        templates_selected=subscription_data["templates_selected"],
        cycle=cycle_data,
    )

    for target in targets:
        target["timeline"] = [
            {
                "time": datetime.utcnow(),
                "message": "opened",
                "details": {"country": "USA"},
            }
        ]
    target_manager.save_many(targets)

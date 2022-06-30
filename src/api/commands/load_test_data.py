"""Load Test Data."""
# Standard Python Libraries
from datetime import datetime, timedelta
import json
import logging
import os
import random

# Third-Party Libraries
from faker import Faker

# cisagov Libraries
from api.manager import (
    CustomerManager,
    CycleManager,
    SendingProfileManager,
    SubscriptionManager,
    TargetManager,
    TemplateManager,
)
from utils.subscriptions import get_target_send_date
from utils.templates import get_deception_level

current_dir = os.path.dirname(__file__)

customer_manager = CustomerManager()
cycle_manager = CycleManager()
sending_profile_manager = SendingProfileManager()
subscription_manager = SubscriptionManager()
target_manager = TargetManager()
template_manager = TemplateManager()
fake = Faker()


def load_test_data():
    """Load sample targets and any missing test data."""
    # Step 1 - Load Customer
    customer_id = load_customer()

    # Step 2 - Load Sending Profile
    sending_profile_id = load_sending_profile()

    # Step 3 - Get templates
    templates = get_templates()

    # Step 4 - Load Subscription
    subscription_id = load_subscription(customer_id, sending_profile_id, templates)

    # Step 5 - Load Cycle
    cycle = load_cycle(subscription_id, templates)

    # Step 6 - Load Targets
    load_targets(
        cycle=cycle,
        templates=templates,
    )


def read_json_file(file_name: str):
    """Open json file from path."""
    with open(os.path.join(current_dir, f"data/{file_name}")) as f:
        return json.load(f)


def load_sending_profile():
    """Load sample sending profile."""
    sending_profile = sending_profile_manager.get(
        filter_data={"name": "Test Sending Profile"}
    )
    if sending_profile:
        logging.info("Test data for sending profile already exists.")
        return sending_profile["_id"]

    load_data = read_json_file("sending_profile.json")
    sending_profile = sending_profile_manager.save(load_data)

    return sending_profile["_id"]


def load_customer():
    """Load sample customer data."""
    customer = customer_manager.get(filter_data={"name": "Test Customer"})
    if customer:
        logging.info("Test data for customer already exists.")
        return customer["_id"]

    load_data = read_json_file("customer.json")
    logging.info("loading customer test data...")
    customer = customer_manager.save(load_data)

    return customer["_id"]


def load_subscription(customer_id, sending_profile_id, templates):
    """Load sample subscription data."""
    subscription = subscription_manager.get(filter_data={"name": "test_subscription"})
    if subscription:
        logging.info("Test data for subscription already exists.")
        return subscription["_id"]

    template_ids = [t["_id"] for t in templates]
    load_data = read_json_file("subscription.json")
    logging.info("loading subscription test data...")
    load_data["start_date"] = datetime.utcnow()
    load_data["customer_id"] = customer_id
    load_data["sending_profile_id"] = sending_profile_id
    load_data["templates_selected"] = template_ids
    subscription = subscription_manager.save(load_data)

    return subscription["_id"]


def load_cycle(subscription_id: str, templates):
    """Load sample cycle data."""
    logging.info("loading cycle test data...")
    load_data = read_json_file("cycle.json")
    load_data["subscription_id"] = subscription_id
    load_data["start_date"] = datetime.utcnow()
    load_data["end_date"] = datetime.utcnow() + timedelta(days=90)
    load_data["send_by_date"] = datetime.utcnow() + timedelta(days=60)
    load_data["template_ids"] = [t["_id"] for t in templates]
    load_data["active"] = False
    load_data["dirty_stats"] = True
    load_data["target_count"] = random.randrange(3000, 12000)  # nosec
    cycle = cycle_manager.save(load_data)
    load_data["_id"] = cycle["_id"]
    return load_data


def get_templates():
    """Get templates from db to be used in cycle and subscription."""
    templates = template_manager.all()
    low = random.choice(  # nosec
        list(filter(lambda x: x["deception_score"] <= 2, templates))
    )
    moderate = random.choice(  # nosec
        list(
            filter(
                lambda x: x["deception_score"] > 2 and x["deception_score"] < 5,
                templates,
            )
        )
    )
    high = random.choice(  # nosec
        list(filter(lambda x: x["deception_score"] >= 5, templates))
    )
    return [low, moderate, high]


def load_targets(
    cycle: dict,
    templates: list,
):
    """Create targets from list."""
    targets = []
    for i in range(0, cycle["target_count"]):
        targets.append(get_target(cycle, i, templates))
    target_manager.save_many(targets)
    return targets


def get_target(cycle, index, templates):
    """Get a target."""
    template = min(templates, key=lambda k: k.get("count", 0))
    if not template.get("count"):
        template["count"] = 1
    else:
        template["count"] += 1
    send_date = get_target_send_date(
        index,
        cycle["target_count"],
        cycle["start_date"],
        cycle["end_date"],
    )
    return {
        "cycle_id": cycle["_id"],
        "subscription_id": cycle["subscription_id"],
        "email": f"test_{index}@test.com",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "position": fake.job(),
        "send_date": send_date,
        "template_id": template["_id"],
        "deception_level": get_deception_level(template["deception_score"]),
        "timeline": get_target_timeline(send_date),
        "sent": True,
        "sent_date": send_date,
    }


def get_target_timeline(send_date):
    """Get target timeline."""
    timeline = []
    if random.choice([True, False]):  # nosec
        for event in ["opened", "clicked"]:
            timeline.append(
                {
                    "time": send_date + timedelta(minutes=5),
                    "message": event,
                    "details": {
                        "user_agent": "test",
                        "ip": "127.0.0.1",
                        "asn_org": random.choice(  # nosec
                            ["TEST_1", "TEST_2", "TEST_3"]
                        ),
                        "city": "TEST",
                        "country": "TEST",
                    },
                }
            )
    return timeline

"""Subscription utils."""
# Standard Python Libraries
from datetime import datetime, timedelta
import random
from uuid import uuid4

# Third-Party Libraries
import dateutil.parser

# cisagov Libraries
from api import config
from api.manager import CycleManager, SubscriptionManager

subscription_manager = SubscriptionManager()
cycle_manager = CycleManager()


def start_subscription(subscription_uuid):
    """Launch a subscription."""
    subscription = subscription_manager.get(uuid=subscription_uuid)
    cycle = {}
    cycle.update(calculate_cycle_dates(subscription))
    cycle["subscription_uuid"] = subscription_uuid
    cycle["active"] = True
    cycle["targets"] = []
    total_targets = len(subscription["target_email_list"])
    deception_mods = get_deception_mods()
    for index, target in enumerate(subscription["target_email_list"]):
        target["target_id"] = str(uuid4())
        # Assign send date to target
        target["send_date"] = get_target_send_date(
            index, total_targets, cycle["start_date"], cycle["send_by_date"]
        )
        # Assign deception level to target
        target["deception_level"] = deception_mods[total_targets % (index + 1)]
        # Assign template to target
        # https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html#b311-random
        target["template_uuid"] = random.choice(  # nosec
            subscription["templates_selected"][target["deception_level"]]
        )
        cycle["targets"].append(target)

    # TODO: Create tasks
    subscription_manager.update(uuid=subscription_uuid, data={"status": "running"})
    return cycle_manager.save(cycle)


def stop_subscription(subscription_uuid):
    """Stop a subscription."""
    cycle = cycle_manager.get(filter_data={"active": True}, fields=["cycle_uuid"])
    cycle_manager.update(cycle["cycle_uuid"], {"active": False})
    subscription_manager.update(uuid=subscription_uuid, data={"status": "stopped"})
    return {"success": True}


def create_subscription_name(customer):
    """Create name for subscription from customer."""
    subscriptions = subscription_manager.all(
        {"customer_uuid": customer["customer_uuid"]},
        fields=["name", "identifier"],
    )
    if not subscriptions:
        return f"{customer['identifier']}_1"
    else:
        ids = [int(float(x["name"].split("_")[-1])) for x in subscriptions]
        return f"{customer['identifier']}_{max(ids) + 1}"


def calculate_cycle_dates(subscription):
    """Calculate subscription, start, send by and end dates."""
    now = datetime.utcnow()
    start_date = subscription.get("start_date", now)

    if not isinstance(start_date, datetime):
        start_date = dateutil.parser.parse(start_date)

    start_date = start_date.replace(tzinfo=None)

    if start_date < now:
        start_date = now

    start_date = start_date + timedelta(minutes=config.DELAY_MINUTES)
    send_by_date = start_date + timedelta(minutes=subscription["cycle_length_minutes"])
    end_date = send_by_date + timedelta(minutes=subscription["cooldown_minutes"])
    return {
        "start_date": start_date,
        "send_by_date": send_by_date,
        "end_date": end_date,
    }


def get_target_send_date(
    index: int, total_targets: int, start_date: datetime, send_by_date: datetime
):
    """Get datetime to send email to target."""
    total_minutes = (send_by_date - start_date).total_seconds() / 60
    minutes_per_email = total_minutes / total_targets
    offset = minutes_per_email * index
    return start_date + timedelta(minutes=offset)


def get_deception_mods():
    """Get modulus value to determine deception level to assign target."""
    mods = [0, 1, 2]
    random.shuffle(mods)
    return {mods[0]: "low", mods[1]: "moderate", mods[2]: "high"}

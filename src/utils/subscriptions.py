"""Subscription utils."""
# Standard Python Libraries
from datetime import datetime, timedelta
import random
from uuid import uuid4

# Third-Party Libraries
import dateutil.parser  # type: ignore

# cisagov Libraries
from api import config
from api.manager import (
    CycleManager,
    SubscriptionManager,
    TargetManager,
    TemplateManager,
)
from utils.templates import get_deception_level
from utils.time import get_yearly_minutes

subscription_manager = SubscriptionManager()
cycle_manager = CycleManager()
target_manager = TargetManager()
template_manager = TemplateManager()


def start_subscription(subscription_uuid):
    """Launch a subscription."""
    subscription = subscription_manager.get(uuid=subscription_uuid)
    cycle = {}
    cycle.update(calculate_cycle_dates(subscription))
    cycle["subscription_uuid"] = subscription_uuid
    cycle["active"] = True
    targets = []
    total_targets = len(subscription["target_email_list"])
    cycle["target_count"] = total_targets
    cycle["template_uuids"] = set()
    resp = cycle_manager.save(cycle)
    cycle_uuid = resp["cycle_uuid"]
    templates = template_manager.all(
        params={"template_uuid": {"$in": subscription["templates_selected"]}},
        fields=["template_uuid", "deception_score"],
    )

    template_counts = {t: 0 for t in subscription["templates_selected"]}

    # Shuffle list for more random template selection across cycles
    random.shuffle(subscription["target_email_list"])
    for index, target in enumerate(subscription["target_email_list"]):
        # Assign uuids to target
        target["cycle_uuid"] = cycle_uuid
        target["subscription_uuid"] = subscription_uuid
        # Assign send date to target
        target["send_date"] = get_target_send_date(
            index, total_targets, cycle["start_date"], cycle["send_by_date"]
        )

        # Assign template to target
        target["template_uuid"] = min(template_counts, key=lambda k: template_counts[k])
        template_counts[target["template_uuid"]] += 1

        # Assign deception level to target
        template = next(
            filter(lambda x: x["template_uuid"] == target["template_uuid"], templates)
        )
        target["deception_level"] = get_deception_level(template["deception_score"])

        targets.append(target)
        cycle["template_uuids"].add(target["template_uuid"])

    tasks = get_initial_tasks(subscription, cycle)
    subscription_manager.update(
        uuid=subscription_uuid,
        data={
            "status": "running",
            "tasks": tasks,
        },
    )
    cycle_manager.update(uuid=cycle_uuid, data=cycle)
    target_manager.save_many(targets)
    return resp


def stop_subscription(subscription_uuid):
    """Stop a subscription."""
    cycle = cycle_manager.get(
        filter_data={
            "active": True,
            "subscription_uuid": subscription_uuid,
        },
        fields=["cycle_uuid"],
    )
    cycle_manager.update(cycle["cycle_uuid"], {"active": False})
    subscription_manager.update(
        uuid=subscription_uuid, data={"status": "stopped", "tasks": []}
    )
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


def get_initial_tasks(subscription, cycle):
    """Get initial tasks for a subscription."""
    start_date = cycle["start_date"]
    report_minutes = subscription["report_frequency_minutes"]
    cycle_minutes = (
        subscription["cycle_length_minutes"] + subscription["cooldown_minutes"]
    )
    yearly_minutes = get_yearly_minutes()
    task_types = {
        "start_subscription_email": start_date
        + timedelta(minutes=config.DELAY_MINUTES),
        "monthly_report": start_date + timedelta(minutes=report_minutes),
        "cycle_report": start_date + timedelta(minutes=cycle_minutes),
        "yearly_report": start_date + timedelta(minutes=yearly_minutes),
        "end_cycle": start_date + timedelta(minutes=cycle_minutes),
    }
    tasks = []
    for task_type, scheduled_date in task_types.items():
        tasks.append(
            {
                "task_uuid": str(uuid4()),
                "task_type": task_type,
                "scheduled_date": scheduled_date,
                "executed": False,
            }
        )
    return tasks
"""Subscription utils."""
# Standard Python Libraries
from datetime import datetime, timedelta
import random
import string
from uuid import uuid4

# Third-Party Libraries
import dateutil.parser  # type: ignore

# cisagov Libraries
from api.manager import (
    CustomerManager,
    CycleManager,
    SubscriptionManager,
    TargetManager,
    TemplateManager,
)
from utils.templates import get_deception_level, get_random_templates

# from utils.time import get_yearly_minutes

customer_manager = CustomerManager()
cycle_manager = CycleManager()
subscription_manager = SubscriptionManager()
target_manager = TargetManager()
template_manager = TemplateManager()


def start_subscription(subscription_id, templates_selected=[]):
    """Launch a subscription."""
    subscription = subscription_manager.get(document_id=subscription_id)

    total_targets = len(subscription["target_email_list"])

    if total_targets == 0:
        return {
            "error": "Target recipients not specified. Please add target emails."
        }, 400

    cycle = {}
    cycle.update(calculate_cycle_dates(subscription))
    cycle["subscription_id"] = subscription_id
    cycle["phish_header"] = subscription["phish_header"]
    cycle["active"] = True
    targets = []
    cycle["target_count"] = total_targets
    cycle["template_ids"] = set()
    resp = cycle_manager.save(cycle)
    cycle_id = resp["_id"]

    if templates_selected:
        subscription["templates_selected"] = templates_selected

    templates = template_manager.all(
        params={"_id": {"$in": subscription["templates_selected"]}},
        fields=["_id", "deception_score"],
    )

    template_counts = {t: 0 for t in subscription["templates_selected"]}

    # Shuffle list for more random template selection across cycles
    random.shuffle(subscription["target_email_list"])
    for index, target in enumerate(subscription["target_email_list"]):
        # Assign ids to target
        target["cycle_id"] = cycle_id
        target["subscription_id"] = subscription_id
        # Assign send date to target
        target["send_date"] = get_target_send_date(
            index,
            total_targets,
            cycle["start_date"],
            cycle["send_by_date"],
        )

        # Assign template to target
        target["template_id"] = min(template_counts, key=lambda k: template_counts[k])
        template_counts[target["template_id"]] += 1

        # Assign deception level to target
        template = next(filter(lambda x: x["_id"] == target["template_id"], templates))
        target["deception_level"] = get_deception_level(template["deception_score"])
        target["deception_level_int"] = template["deception_score"]

        targets.append(target)
        cycle["template_ids"].add(target["template_id"])

    tasks = get_initial_tasks(subscription, cycle)

    update_data = {
        "status": "running",
        "tasks": tasks,
    }

    cycle["tasks"] = tasks

    if templates_selected:
        update_data["templates_selected"] = templates_selected
    else:
        update_data["templates_selected"] = get_random_templates(subscription)

    next_templates_selected = get_random_templates(subscription)
    if next_templates_selected:
        update_data["next_templates"] = next_templates_selected

    subscription_manager.update(document_id=subscription_id, data=update_data)
    cycle_manager.update(document_id=cycle_id, data=cycle)
    target_manager.save_many(targets)
    return resp, 200


def stop_subscription(subscription_id):
    """Stop a subscription."""
    cycle = cycle_manager.get(
        filter_data={
            "active": True,
            "subscription_id": subscription_id,
        },
        fields=["_id"],
    )
    if cycle:
        cycle_manager.update(cycle["_id"], {"active": False})
    subscription_manager.update(
        document_id=subscription_id, data={"status": "stopped", "tasks": []}
    )
    return {"success": True}


def create_subscription_name(customer):
    """Create name for subscription from customer."""
    subscriptions = subscription_manager.all(
        {"customer_id": customer["_id"]},
        fields=["name", "identifier", "stakeholder_shortname"],
    )
    if customer.get("stakeholder_shortname", "") != "":
        if not subscriptions:
            return f"{customer['stakeholder_shortname']}_1"
        else:
            ids = [int(float(x["name"].split("_")[-1])) for x in subscriptions]
            return f"{customer['stakeholder_shortname']}_{max(ids) + 1}"
    else:
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

    send_by_date = start_date + timedelta(minutes=subscription["cycle_length_minutes"])
    end_date = send_by_date + timedelta(minutes=subscription["cooldown_minutes"])
    return {
        "start_date": start_date,
        "send_by_date": send_by_date,
        "end_date": end_date,
    }


def get_target_send_date(
    index: int,
    total_targets: int,
    start_date: datetime,
    send_by_date: datetime,
):
    """Get datetime to send email to target."""
    total_minutes = (send_by_date - start_date).total_seconds() / 60
    minutes_per_email = total_minutes / total_targets
    offset = minutes_per_email * index
    return start_date + timedelta(minutes=offset)


def get_initial_tasks(subscription, cycle):
    """Get initial tasks for a subscription."""
    start_date = cycle["start_date"]
    end_date = cycle["end_date"]
    report_minutes = subscription["report_frequency_minutes"]
    cycle_minutes = (
        subscription["cycle_length_minutes"] + subscription["cooldown_minutes"]
    )
    cycle_days = cycle_minutes / 60 / 24
    # yearly_minutes = get_yearly_minutes()
    initial_tasks = []

    # start_subscription_email
    initial_tasks.append(get_new_task("start_subscription_email", start_date))

    # status_reports
    n_status_reports = 1 + (cycle_minutes // report_minutes)
    last_date = cycle["start_date"]
    for i in range(1, n_status_reports):
        initial_tasks.append(
            get_new_task("status_report", last_date + timedelta(minutes=report_minutes))
        )
        last_date += timedelta(minutes=report_minutes)

    # cycle_report
    initial_tasks.append(
        get_new_task("cycle_report", start_date + timedelta(minutes=cycle_minutes))
    )

    # safelisting_reminder
    if subscription.get("continuous_subscription"):
        initial_tasks.append(
            get_new_task(
                "safelisting_reminder", start_date + timedelta(minutes=cycle_minutes)
            )
        )

    # n_day_reminders
    if cycle_days >= 5:
        initial_tasks.append(
            get_new_task("five_day_reminder", end_date - timedelta(days=5))
        )
    if cycle_days >= 15:
        initial_tasks.append(
            get_new_task("fifteen_day_reminder", end_date - timedelta(days=15))
        )
    if cycle_days >= 30:
        initial_tasks.append(
            get_new_task("thirty_day_reminder", end_date - timedelta(days=30))
        )

    # end_cycle or start_next_cycle
    if subscription.get("continuous_subscription"):
        initial_tasks.append(
            get_new_task(
                "start_next_cycle",
                start_date
                + timedelta(
                    minutes=(cycle_minutes + subscription.get("buffer_time_minutes", 0))
                ),
            )
        )
    else:
        initial_tasks.append(
            get_new_task(
                "end_cycle", start_date + timedelta(minutes=(cycle_minutes + 15))
            )
        )

    return initial_tasks


def get_new_task(task_type, scheduled_date):
    """Generate a task."""
    return {
        "task_uuid": str(uuid4()),
        "task_type": task_type,
        "scheduled_date": scheduled_date,
        "executed": False,
    }


def get_random_phish_header():
    """Generate a random phish header."""
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(32)  # nosec
    )

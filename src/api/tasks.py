"""Tasks."""
# Standard Python Libraries
from datetime import datetime, timedelta
import logging
from uuid import uuid4

# cisagov Libraries
from api.app import app
from api.manager import CycleManager, SubscriptionManager
from utils.notifications import Notification
from utils.subscriptions import stop_subscription
from utils.time import get_yearly_minutes

subscription_manager = SubscriptionManager()
cycle_manager = CycleManager()


def tasks_job():
    """Run subscription tasks."""
    with app.app_context():
        while True:
            subscription = get_subscription()
            if not subscription:
                logging.info("No more subscription tasks to process.")
                break
            process_subscription(subscription)


def get_subscription():
    """Get and update cycle for processing."""
    return subscription_manager.find_one_and_update(
        params={
            "tasks": {
                "$elemMatch": {
                    "scheduled_date": {"$lt": datetime.utcnow()},
                    "executed": {"$in": [False, None]},
                }
            },
            "processing": {"$in": [False, None]},
        },
        data={"processing": True},
    )


def process_subscription(subscription):
    """Process subscription tasks."""
    cycle = cycle_manager.get(
        filter_data={
            "subscription_id": str(subscription["_id"]),
            "active": True,
        }
    )
    tasks = list(
        filter(
            lambda x: x["scheduled_date"].timestamp() < datetime.utcnow().timestamp()
            and not x.get("executed"),
            subscription.get("tasks", []),
        )
    )

    end_cycle_task = next(filter(lambda x: x["task_type"] == "end_cycle", tasks), None)
    for task in tasks:
        task["executed"] = True
        task["executed_date"] = datetime.utcnow()
        logging.info(f"Processing task {task}")
        try:
            process_task(task, subscription, cycle)
        except Exception as e:
            logging.exception(e)
            task["error"] = str(e)
        if not end_cycle_task:
            update_task(subscription["_id"], task)
            add_new_task(subscription, task)
        logging.info(f"Executed task {task}")

    subscription_manager.update(
        document_id=subscription["_id"], data={"processing": False}, update=False
    )


def update_task(subscription_id, task):
    """Update subsscription task."""
    subscription_manager.update_in_list(
        document_id=subscription_id,
        field="tasks.$",
        data=task,
        params={"tasks.task_uuid": task["task_uuid"]},
    )


def add_new_task(subscription, task):
    """Add new subscription task."""
    scheduled = task["scheduled_date"]
    report_minutes = subscription["report_frequency_minutes"]
    cycle_minutes = (
        subscription["cycle_length_minutes"] + subscription["cooldown_minutes"]
    )
    yearly_minutes = get_yearly_minutes()
    new_date = {
        "status_report": scheduled + timedelta(minutes=report_minutes),
        "cycle_report": scheduled + timedelta(minutes=cycle_minutes),
        "yearly_report": scheduled + timedelta(minutes=yearly_minutes),
        "end_cycle": scheduled + timedelta(minutes=cycle_minutes),
        "safelisting_reminder": scheduled,
    }.get(task["task_type"])
    if new_date:
        task = {
            "task_uuid": str(uuid4()),
            "task_type": task["task_type"],
            "scheduled_date": new_date,
            "executed": False,
        }
        logging.info(f"Adding new task {task}")

        return subscription_manager.add_to_list(
            document_id=subscription["_id"],
            field="tasks",
            data=task,
        )
    return None


def process_task(task, subscription, cycle):
    """Process subscription task."""
    task_types = {
        "start_subscription_email": start_subscription_email,
        "status_report": status_report,
        "cycle_report": cycle_report,
        "yearly_report": yearly_report,
        "end_cycle": end_cycle,
        "thirty_day_reminder": thirty_day_reminder,
        "fifteen_day_reminder": fifteen_day_reminder,
        "five_day_reminder": five_day_reminder,
        "safelisting_reminder": safelisting_reminder,
    }
    return task_types[task["task_type"]](subscription, cycle)


def start_subscription_email(subscription, cycle):
    """Send start subscription email."""
    Notification("subscription_started", subscription, cycle).send()


def status_report(subscription, cycle):
    """Send status report."""
    Notification("status_report", subscription, cycle).send()


def cycle_report(subscription, cycle):
    """Send cycle report."""
    Notification("cycle_report", subscription, cycle).send()


def yearly_report(subscription, cycle):
    """Send yearly report."""
    # Notification("yearly_report", subscription, cycle).send()
    return


def thirty_day_reminder(subscription, cycle):
    """Send thirty day reminder."""
    if subscription.get("continuous_subscription"):
        Notification("thirty_day_reminder", subscription, cycle).send()


def fifteen_day_reminder(subscription, cycle):
    """Send fifteen day reminder."""
    if subscription.get("continuous_subscription"):
        Notification("fifteen_day_reminder", subscription, cycle).send()


def five_day_reminder(subscription, cycle):
    """Send five day reminder."""
    if subscription.get("continuous_subscription"):
        Notification("five_day_reminder", subscription, cycle).send()


def end_cycle(subscription, cycle):
    """End cycle by stopping or continuing new cycle."""
    # Temporarily disable continuous subscription cycle for all subscriptions
    # When ready to re-enable, just uncomment the code below. This the only
    # instance in this codebase where this needs to be done.
    # if subscription.get("continuous_subscription"):
    #     stop_subscription(str(subscription["_id"]))
    #     start_subscription(str(subscription["_id"]))
    # else:
    stop_subscription(str(subscription["_id"]))
    Notification("subscription_stopped", subscription, cycle).send()


def safelisting_reminder(subscription, cycle):
    """Send safelisting reminder email."""
    Notification("safelisting_reminder", subscription, cycle).send()

"""Tasks."""
# Standard Python Libraries
from datetime import datetime, timedelta
import logging
from uuid import uuid4

# Third-Party Libraries
from utils.notifications import Notification
from utils.subscriptions import start_subscription, stop_subscription
from utils.time import get_yearly_minutes

# cisagov Libraries
from api.app import app
from api.manager import CycleManager, SubscriptionManager

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
            "subscription_uuid": subscription["subscription_uuid"],
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

    end_cycle_task = bool(list(filter(lambda x: x["task_type"] == "end_cycle", tasks)))
    is_stopping = end_cycle_task and not subscription.get("continuous_subscription")
    for task in tasks:
        try:
            logging.info(f"Processing task {task}")
            process_task(task, subscription, cycle)
            task["executed"] = True
            task["error"] = ""
            task["executed_date"] = datetime.utcnow()
            if not is_stopping:
                update_task(subscription["subscription_uuid"], task)
                add_new_task(subscription, task)
            logging.info(f"Successfully executed task {task}")
        except Exception as e:
            logging.error(f"Error executing task {task}")
            logging.exception(e)
            task["executed"] = False
            task["error"] = str(e)
            task["scheduled_date"] = datetime.utcnow() + timedelta(minutes=10)
            update_task(subscription["subscription_uuid"], task)

    subscription_manager.update(
        uuid=subscription["subscription_uuid"],
        data={"processing": False},
    )


def update_task(subscription_uuid, task):
    """Update subsscription task."""
    return subscription_manager.update_in_list(
        uuid=subscription_uuid,
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
        "monthly_report": scheduled + timedelta(minutes=report_minutes),
        "cycle_report": task["scheduled_date"] + timedelta(minutes=cycle_minutes),
        "yearly_report": task["scheduled_date"] + timedelta(minutes=yearly_minutes),
        "end_cycle": task["scheduled_date"] + timedelta(minutes=cycle_minutes),
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
            uuid=subscription["subscription_uuid"],
            field="tasks",
            data=task,
        )
    return None


def process_task(task, subscription, cycle):
    """Process subscription task."""
    task_types = {
        "start_subscription_email": start_subscription_email,
        "monthly_report": monthly_report,
        "cycle_report": cycle_report,
        "yearly_report": yearly_report,
        "end_cycle": end_cycle,
    }
    return task_types[task["task_type"]](subscription, cycle)


def start_subscription_email(subscription, cycle):
    """Send start subscription email."""
    Notification("subscription_started", subscription, cycle).send()


def monthly_report(subscription, cycle):
    """Send monthly report."""
    Notification("monthly_report", subscription, cycle).send()


def cycle_report(subscription, cycle):
    """Send cycle report."""
    Notification("cycle_report", subscription, cycle).send()


def yearly_report(subscription, cycle):
    """Send yearly report."""
    Notification("yearly_report", subscription, cycle).send()


def end_cycle(subscription, cycle):
    """End cycle by stopping or continuing new cycle."""
    if subscription.get("continuous_subscription"):
        stop_subscription(subscription["subscription_uuid"])
        start_subscription(subscription["subscription_uuid"])
    else:
        stop_subscription(subscription["subscription_uuid"])
        Notification("subscription_stopped", subscription, cycle).send()

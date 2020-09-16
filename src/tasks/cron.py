from api.utils import db_utils as db
from api.models.subscription_models import SubscriptionModel, validate_subscription
from datetime import datetime, timedelta
from uuid import uuid4
import logging
from tasks import tasks
from api.utils.subscription.static import YEARLY_MINUTES, MONTHLY_MINUTES, CYCLE_MINUTES


def execute_tasks():
    # Get all tasks
    logging.info("Getting tasks to execute")
    subscriptions = db.get_list(
        {}, "subscription", SubscriptionModel, validate_subscription
    )

    for s in subscriptions:
        tasks = s.get("tasks")
        if tasks:
            for t in tasks:
                scheduled_date = t.get("scheduled_date")
                if not scheduled_date:
                    scheduled_date = datetime.now() + timedelta(days=1)

                executed = t.get("executed")

                if (
                    scheduled_date.replace(tzinfo=None) < datetime.now()
                    and not executed
                ):
                    logging.info(f"Executing task {t}")

                    # Execute Task
                    try:
                        execute_task(s, t["message_type"])
                        t["executed"] = True
                        t["error"] = ""
                        t["executed_date"] = datetime.now()
                        update_task(s["subscription_uuid"], t)
                        add_new_task(
                            s["subscription_uuid"],
                            t["scheduled_date"],
                            t["message_type"],
                        )

                        logging.info(f"Successfully executed task {t}")

                    except BaseException as e:
                        logging.exception(e)
                        t["error"] = str(e)
                        update_task(s["subscription_uuid"], t)
        else:
            logging.info("No tasks to execute")


def update_task(subscription_uuid, task):

    return db.update_nested_single(
        uuid=subscription_uuid,
        field="tasks.$",
        put_data=task,
        collection="subscription",
        model=SubscriptionModel,
        validation_model=validate_subscription,
        params={"tasks.task_uuid": task["task_uuid"]},
    )


def add_new_task(subscription_uuid, scheduled_date, message_type):
    logging.info("checking for new task to add")

    new_date = {
        "monthly_report": scheduled_date + timedelta(minutes=MONTHLY_MINUTES),
        "cycle_report": scheduled_date + timedelta(minutes=CYCLE_MINUTES),
        "yearly_report": scheduled_date + timedelta(minutes=YEARLY_MINUTES),
        "start_new_cycle": scheduled_date + timedelta(minutes=CYCLE_MINUTES),
    }.get(message_type)

    if new_date:
        task = {
            "task_uuid": str(uuid4()),
            "message_type": message_type,
            "scheduled_date": new_date,
            "executed": False,
        }

        logging.info(f"Adding new task {task}")

        return db.push_nested_item(
            uuid=subscription_uuid,
            field="tasks",
            put_data=task,
            collection="subscription",
            model=SubscriptionModel,
            validation_model=validate_subscription,
        )

    return None


def execute_task(subscription, message_type):
    task = {
        "start_subscription_email": tasks.start_subscription_email,
        "monthly_report": tasks.email_subscription_monthly,
        "cycle_report": tasks.email_subscription_cycle,
        "yearly_report": tasks.email_subscription_yearly,
        "start_new_cycle": tasks.start_subscription_cycle,
    }
    task[message_type](subscription)

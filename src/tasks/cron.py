from api.utils import db_utils as db
from api.models.subscription_models import SubscriptionModel, validate_subscription
from api.serializers.subscriptions_serializers import SubscriptionPatchSerializer
from datetime import datetime, timedelta
from uuid import uuid4
import logging
from tasks import tasks
import os


def execute_tasks():
    # Get all tasks
    logging.info("Getting tasks to execute")
    subscriptions = db.get_list(
        {}, "subscription", SubscriptionModel, validate_subscription
    )

    for s in subscriptions:
        updated_tasks = []
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
                    # Create new task in future

                    # Execute Task
                    try:
                        execute_task(s, t["message_type"])
                        t["executed"] = True
                        t["error"] = ""
                        new_task = get_new_task(
                            s["subscription_uuid"],
                            t["scheduled_date"],
                            t["message_type"],
                        )
                        if new_task:
                            updated_tasks.append(new_task)

                        logging.info(f"Successfully executed task {t}")

                    except BaseException as e:
                        t["error"] = str(e)
                    finally:
                        t["executed_date"] = datetime.now()

                updated_tasks.append(t)

            # Update Database with tasks
            put_data = SubscriptionPatchSerializer({"tasks": updated_tasks}).data
            db.update_single(
                uuid=s["subscription_uuid"],
                put_data=put_data,
                collection="subscription",
                model=SubscriptionModel,
                validation_model=validate_subscription,
            )

        else:
            logging.info("No tasks to execute")


def execute_task(subscription, message_type):
    task = {
        "start_subscription_email": tasks.start_subscription_email,
        "monthly_report": tasks.email_subscription_monthly,
        "cycle_report": tasks.email_subscription_cycle,
        "yearly_report": tasks.email_subscription_yearly,
        "start_new_cycle": tasks.start_subscription_cycle,
    }
    task[message_type](subscription)


def get_new_task(subscription_uuid, scheduled_date, message_type):
    scheduled_date = {
        "monthly_report": scheduled_date + timedelta(days=30),
        "cycle_report": scheduled_date + timedelta(days=60),
        "yearly_report": scheduled_date + timedelta(days=365),
        "start_new_cycle": scheduled_date + timedelta(days=90),
    }.get("message_type")

    if scheduled_date:
        return {
            "task_uuid": uuid4(),
            "message_type": message_type,
            "scheduled_date": scheduled_date,
            "executed": False,
        }

    return None

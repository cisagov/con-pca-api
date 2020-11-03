import logging
import json
import dateutil.parser

from api.utils.subscription.static import YEARLY_MINUTES, MONTHLY_MINUTES, CYCLE_MINUTES
from api.utils.subscription.subscriptions import send_start_notification
from api.utils.subscription import actions
from api.services import SubscriptionService, CampaignService

from api.notifications import EmailSender

from datetime import datetime, timedelta
from uuid import uuid4

from django.core.wsgi import get_wsgi_application

logger = logging.getLogger()
logger.setLevel(logging.INFO)

application = get_wsgi_application()

subscription_service = SubscriptionService()
campaign_service = CampaignService()


def lambda_handler(event, context):
    for record in event["Records"]:
        payload = json.loads(record["body"])
        subscription_uuid = payload["subscription_uuid"]
        task = payload["task"]

        logger.info(f"Executing task {task}")
        subscription = subscription_service.get(subscription_uuid)

        task["scheduled_date"] = dateutil.parser.parse(task["scheduled_date"])

        try:
            execute_task(subscription, task["message_type"])
            task["executed"] = True
            task["error"] = ""
            task["executed_date"] = datetime.now()
            update_task(subscription_uuid, task)
            add_new_task(
                subscription_uuid, task["scheduled_date"], task["message_type"]
            )
            logger.info(f"Successfully executed task {task}")
        except BaseException as e:
            logger.exception(e)
            task["error"] = str(e)
            update_task(subscription_uuid, task)


def update_task(subscription_uuid, task):
    return subscription_service.update_nested(
        uuid=subscription_uuid,
        field="tasks.$",
        data=task,
        params={"tasks.task_uuid": task["task_uuid"]},
    )


def add_new_task(subscription_uuid, scheduled_date, message_type):
    logger.info("checking for new task to add")

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

        logger.info(f"Adding new task {task}")

        return subscription_service.push_nested(
            uuid=subscription_uuid, field="tasks", data=task
        )

    return None


def execute_task(subscription, message_type):
    task = {
        "start_subscription_email": start_subscription_email,
        "monthly_report": email_subscription_monthly,
        "cycle_report": email_subscription_cycle,
        "yearly_report": email_subscription_yearly,
        "start_new_cycle": start_subscription_cycle,
    }
    task[message_type](subscription)


def start_subscription_email(subscription):
    send_start_notification(subscription)
    subscription_service.update(
        subscription["subscription_uuid"], {"status": "In Progress"}
    )


def start_subscription_cycle(subscription):
    """
    Create the next subscription cycle
    """
    actions.start_subscription(
        subscription_uuid=subscription.get("subscription_uuid"), new_cycle=True
    )
    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }
    return context


def email_subscription_monthly(subscription):
    """
    schedule the next monthly subscription report email
    """
    # Send email
    sender = EmailSender(
        subscription,
        "monthly_report",
        datetime.now().isoformat(),
        subscription["cycles"][-1]["cycle_uuid"],
    )
    sender.send()

    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }

    return context


def email_subscription_cycle(subscription):
    """
    schedule the next subscription cycle report email
    """
    # Send email
    sender = EmailSender(subscription, "cycle_report", datetime.now().isoformat())
    sender.send()

    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }

    return context


def email_subscription_yearly(subscription):
    """
    schedule the next yearly subscription report email
    """
    # Send email
    cycle = subscription["cycles"][-1]["start_date"].isoformat()
    sender = EmailSender(subscription, "yearly_report", cycle)
    sender.send()

    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }

    return context

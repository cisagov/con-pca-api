"""Process Tasks Lambda Function."""
# Standard Python Libraries
from datetime import datetime, timedelta
import json
import logging
from uuid import uuid4

# Third-Party Libraries
import dateutil.parser
from django.core.wsgi import get_wsgi_application

# cisagov Libraries
from api.notifications import EmailSender
from api.services import CampaignService, SubscriptionService
from api.utils.subscription import actions
from api.utils.subscription.cycles import get_last_run_cycle
from api.utils.subscription.static import CYCLE_MINUTES, MONTHLY_MINUTES, YEARLY_MINUTES

logger = logging.getLogger()
logger.setLevel(logging.INFO)

application = get_wsgi_application()

subscription_service = SubscriptionService()
campaign_service = CampaignService()


def lambda_handler(event, context):
    """Handle SQS Event."""
    for record in event["Records"]:
        payload = json.loads(record["body"])
        subscription_uuid = payload["subscription_uuid"]
        task = payload["task"]

        logger.info(f"Executing task {task}")
        subscription = subscription_service.get(subscription_uuid)

        scheduled_date = dateutil.parser.parse(task["scheduled_date"])

        try:
            execute_task(subscription, task["message_type"])
            task["executed"] = True
            task["error"] = ""
            task["executed_date"] = datetime.now()
            # If the subscription is not stopping, update and add a new task
            if not payload.get("stopping_subscription"):
                update_task(subscription_uuid, task)
                add_new_task(subscription_uuid, scheduled_date, task["message_type"])
            logger.info(f"Successfully executed task {task}")
        except BaseException as e:
            logger.exception(e)
            task["executed"] = False
            task["queued"] = False
            task["error"] = str(e)
            update_task(subscription_uuid, task)


def update_task(subscription_uuid, task):
    """Update Subscription Task."""
    return subscription_service.update_nested(
        uuid=subscription_uuid,
        field="tasks.$",
        data=task,
        params={"tasks.task_uuid": task["task_uuid"]},
    )


def add_new_task(subscription_uuid, scheduled_date, message_type):
    """Add new task."""
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
            "queued": False,
        }

        logger.info(f"Adding new task {task}")

        return subscription_service.push_nested(
            uuid=subscription_uuid, field="tasks", data=task
        )

    return None


def execute_task(subscription, message_type):
    """Execute Task."""
    task = {
        "start_subscription": start_subscription,
        "start_subscription_email": start_subscription_email,
        "monthly_report": email_subscription_monthly,
        "cycle_report": email_subscription_cycle,
        "yearly_report": email_subscription_yearly,
        "start_new_cycle": start_subscription_cycle,
        "stop_subscription": stop_subscription,
    }
    task[message_type](subscription)


def start_subscription(subscription):
    """Start Subscription Task."""
    actions.start_subscription(subscription["subscription_uuid"])


def start_subscription_email(subscription):
    """Start Subscription Email Task."""
    sender = EmailSender(subscription, "subscription_started")
    sender.send()
    subscription_service.update(
        subscription["subscription_uuid"], {"status": "In Progress"}
    )


def start_subscription_cycle(subscription):
    """Start Subscription Cycle Task."""
    actions.start_subscription(subscription["subscription_uuid"], new_cycle=True)


def stop_subscription(subscription):
    """Stop Subscription Task."""
    actions.stop_subscription(subscription)


def email_subscription_monthly(subscription):
    """Email Monthly Report Task."""
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
    """Email Cycle Report Task."""
    # Send email
    selected_cycle = get_last_run_cycle(subscription["cycles"][-2:])

    sender = EmailSender(
        subscription, "cycle_report", selected_cycle["start_date"].isoformat()
    )
    sender.send()

    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }

    return context


def email_subscription_yearly(subscription):
    """Email Yearly Report Task."""
    # Send email
    cycle = subscription["cycles"][-1]["start_date"].isoformat()
    sender = EmailSender(subscription, "yearly_report", cycle)
    sender.send()

    context = {
        "subscription_uuid": subscription.get("subscription_uuid"),
    }

    return context

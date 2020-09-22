from api.utils import db_utils as db
from api.models.subscription_models import SubscriptionModel, validate_subscription
from api.utils.subscription.static import YEARLY_MINUTES, MONTHLY_MINUTES, CYCLE_MINUTES
from api.utils.subscription.subscriptions import send_start_notification
from api.utils.subscription import actions

from notifications.views import EmailSender

from datetime import datetime, timedelta
from uuid import uuid4

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()


def lambda_handler(event, context):
    print("Getting tasks to execute")

    subscriptions = db.get_list(
        {}, "subscription", SubscriptionModel, validate_subscription
    )

    executed_count = 0

    for s in subscriptions:
        tasks = s.get("tasks")
        if tasks:
            for t in tasks:
                scheduled_date = t.get("scheduled_date")
                if not scheduled_date:
                    scheduled_date = datetime.now() + timedelta(days=1)

                executed = t.get("executed")

                if (
                    scheduled_date.replace(tzinfo=None) < datetime.utcnow()
                    and not executed
                ):
                    print(f"Executing task {t}")

                    # Execute Task
                    try:
                        execute_task(s, t["message_type"])
                        executed_count += 1
                        t["executed"] = True
                        t["error"] = ""
                        t["executed_date"] = datetime.now()
                        update_task(s["subscription_uuid"], t)
                        add_new_task(
                            s["subscription_uuid"],
                            t["scheduled_date"],
                            t["message_type"],
                        )

                        print(f"Successfully executed task {t}")

                    except BaseException as e:
                        print(e)
                        t["error"] = str(e)
                        update_task(s["subscription_uuid"], t)

    print(f"{str(executed_count)} tasks executed")


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
    print("checking for new task to add")

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

        print(f"Adding new task {task}")

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
        "start_subscription_email": start_subscription_email,
        "monthly_report": email_subscription_monthly,
        "cycle_report": email_subscription_cycle,
        "yearly_report": email_subscription_yearly,
        "start_new_cycle": start_subscription_cycle,
    }
    task[message_type](subscription)


def start_subscription_email(subscription):
    send_start_notification(subscription)


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

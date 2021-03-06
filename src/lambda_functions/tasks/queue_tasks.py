"""Queue Tasks Lambda Function."""
# Standard Python Libraries
from datetime import datetime
import json
import logging
import os

# Third-Party Libraries
import boto3
import dateutil.parser
from django.core.wsgi import get_wsgi_application

# cisagov Libraries
from api.services import SubscriptionService
from api.utils.generic import format_json
from lambda_functions.tasks.process_tasks import update_task

logger = logging.getLogger()
logger.setLevel(logging.INFO)

application = get_wsgi_application()


def lambda_handler(event, context):
    """Handle CloudWatch Event."""
    logger.info("Getting tasks to queue.")
    tasks = get_tasks_to_queue()

    logger.info("Queueing tasks")
    queue_tasks(tasks)

    logger.info(f"Queued {len(tasks)} tasks")


def get_tasks_to_queue():
    """Get Tasks to Queue."""
    subscription_service = SubscriptionService()
    tasks_to_queue = []
    for s in subscription_service.get_list():
        tasks = s.get("tasks", [])
        for task in tasks:
            scheduled_date = task.get("scheduled_date")

            if type(scheduled_date) is str:
                scheduled_date = dateutil.parser.parse(scheduled_date)
            executed = task.get("executed")
            if (
                scheduled_date.replace(tzinfo=None) < datetime.utcnow()
                and not executed
                and not task.get("queued")
            ):
                tasks_to_queue.append(
                    {
                        "subscription_uuid": s["subscription_uuid"],
                        "task": task,
                    }
                )
    return tasks_to_queue


def queue_tasks(tasks):
    """Queue Tasks in SQS."""
    sqs = boto3.client("sqs")

    for task in tasks:
        stop_task = list(
            filter(
                lambda x: x["subscription_uuid"] == task["subscription_uuid"]
                and x["task"]["message_type"] == "stop_subscription",
                tasks,
            )
        )

        logger.info(f"Queueing task {task}")
        task["task"]["queued"] = True
        task["stopping_subscription"] = bool(stop_task)
        sqs.send_message(
            QueueUrl=os.environ["TASKS_QUEUE_URL"],
            MessageBody=json.dumps(task, default=format_json),
        )
        update_task(task["subscription_uuid"], task["task"])

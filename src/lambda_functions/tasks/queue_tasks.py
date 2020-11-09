import logging
import boto3
import json
import os
from datetime import datetime
import dateutil.parser

from lambda_functions.tasks.process_tasks import update_task
from api.services import SubscriptionService
from api.utils.generic import format_json

from django.core.wsgi import get_wsgi_application

logger = logging.getLogger()
logger.setLevel(logging.INFO)

application = get_wsgi_application()


def lambda_handler(event, context):
    logger.info("Getting tasks to queue")
    tasks = get_tasks_to_queue()

    logger.info("Queueing tasks")
    queue_tasks(tasks)

    logger.info(f"Queued {len(tasks)} tasks")


def get_tasks_to_queue():
    subscription_service = SubscriptionService()
    tasks_to_queue = []
    for s in subscription_service.get_list():
        tasks = s.get("tasks", [])
        for task in tasks:
            scheduled_date = task.get("scheduled_date")

            if not isinstance(scheduled_date, datetime):
                scheduled_date = dateutil.parser.parse(scheduled_date)

            executed = task.get("executed")
            if (
                scheduled_date.replace(tzinfo=None) < datetime.utcnow()
                and not executed
                and not task.get("queued")
            ):
                tasks_to_queue.append(
                    {"subscription_uuid": s["subscription_uuid"], "task": task}
                )
    return tasks_to_queue


def queue_tasks(tasks):
    sqs = boto3.client("sqs")

    for task in tasks:
        logger.info(f"Queueing task {task}")
        task["queued"] = True
        sqs.send_message(
            QueueUrl=os.environ["TASKS_QUEUE_URL"],
            MessageBody=json.dumps(task, default=format_json),
        )
        update_task(task["subscription_uuid"], task["task"])

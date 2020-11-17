import json
from lambda_functions.tasks.process_tasks import lambda_handler
from lambda_functions.tasks.queue_tasks import get_tasks_to_queue
from api.utils.generic import format_json

tasks = get_tasks_to_queue()
for task in tasks:
    event = {"Records": [{"body": json.dumps(task, default=format_json)}]}
    lambda_handler(event, None)

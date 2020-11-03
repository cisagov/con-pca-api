import os
import sys
import json


from dotenv import load_dotenv, find_dotenv

script_dir = os.path.dirname(os.path.realpath(__file__))

sys.path.append(os.path.realpath(f"{script_dir}/../.."))

load_dotenv(find_dotenv())

os.environ["DB_HOST"] = "localhost"
os.environ["GP_URL"] = "http://localhost:3333/"
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
os.environ["BROWSERLESS_ENDPOINT"] = "localhost:3000"

from lambda_functions.tasks.process_tasks import lambda_handler
from lambda_functions.tasks.queue_tasks import get_tasks_to_queue
from api.utils.generic import format_json

tasks = get_tasks_to_queue()
for task in tasks:
    event = {"Records": [{"body": json.dumps(task, default=format_json)}]}
    lambda_handler(event, None)

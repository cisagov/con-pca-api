import os
import sys
from faker import Faker
from dotenv import load_dotenv, find_dotenv
import random
from datetime import datetime, timedelta
from django.core.wsgi import get_wsgi_application


sys.path.append(os.path.realpath("./src"))

load_dotenv(find_dotenv())

os.environ["DB_HOST"] = "localhost"
os.environ["GP_URL"] = "http://localhost:3333/"
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"
os.environ["BROWSERLESS_ENDPOINT"] = "localhost:3000"

application = get_wsgi_application()

from api.services import TargetHistoryService, TemplateService
import random
from datetime import datetime

target_service = TargetHistoryService()
template_service = TemplateService()


templates = template_service.get_list()
now = datetime.now().isoformat()

for i in range(0, 150000):
    email = f"target_{i}@test.com"
    data = {
        "template_uuid": random.choice(templates)["template_uuid"],
        "sent_timestamp": now,
    }
    target_service.save({"email": email, "history_list": [data]})

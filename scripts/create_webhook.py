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

import requests
from datetime import datetime
from api.services import CampaignService

campaign_service = CampaignService()

campaigns = campaign_service.get_list()
campaign = random.choice(list(filter(lambda x: x["campaign_id"] > 25000, campaigns)))
email = random.choice(campaign["target_email_list"])["email"]


data = {
    "campaign_id": campaign["campaign_id"],
    "email": email,
    "time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
    "message": "Clicked Link",
    "details": "",
}

resp = requests.post("http://localhost:8000/api/v1/inboundwebhook/", json=data)

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


from api.services import (
    SubscriptionService,
    TemplateService,
    CustomerService,
    DHSContactService,
    CampaignService,
)
from api.utils.subscription.subscriptions import create_subscription_name


fake = Faker()
subscription_service = SubscriptionService()
campaign_service = CampaignService()
template_service = TemplateService()
customer_service = CustomerService()
dhs_service = DHSContactService()

templates = template_service.get_list()
customer = random.choice(customer_service.get_list())

target_email_list = []
for i in range(0, 15000):
    target_email_list.append(
        {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
            "position": fake.job(),
            "email": f"target_{i}@test.com",
        }
    )

subscription = {
    "customer_uuid": customer["customer_uuid"],
    "tasks": [],
    "name": create_subscription_name(customer),
    "url": None,
    "target_domain": "@test.com",
    "keywords": None,
    "start_date": datetime.now(),
    "end_date": datetime.now() + timedelta(days=30),
    "primary_contact": {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "office_phone": None,
        "mobile_phone": None,
        "email": fake.email(),
        "active": True,
        "notes": "",
    },
    "dhs_contact_uuid": random.choice(dhs_service.get_list())["dhs_contact_uuid"],
    "status": "stopped",
    "target_email_list": target_email_list,
    "target_email_list_cached_copy": target_email_list,
    "templates_selected_uuid_list": [],
    "sending_profile_name": "SMTP",
    "active": False,
    "archived": False,
    "manually_stopped": True,
    "cycles": [],
    "email_report_history": [],
    "stagger_emails": False,
}

subscription_uuid = str(subscription_service.save(subscription)["subscription_uuid"])
response = subscription_service.update(subscription_uuid, subscription)

campaign_ids = random.sample(range(25000, 30000), 5)
campaigns = []

cycle_uuid = fake.uuid4()

batches = []
batch_count = 5
batch_size = int(len(target_email_list) / batch_count)
for i in range(0, len(target_email_list), batch_size):
    batches.append(target_email_list[i : i + batch_size])

for i in range(0, batch_count):
    timeline = []
    timeline.append(
        {
            "email": None,
            "time": datetime.now(),
            "message": "Campaign Created",
            "details": "",
            "duplicate": None,
        }
    )
    sent = 0
    opened = 0
    clicked = 0
    submitted = 0
    reported = 0

    for t in batches[i]:
        timeline.append(
            {
                "email": t["email"],
                "time": datetime.now(),
                "message": "Email Sent",
                "details": "",
                "duplicate": None,
            }
        )

        sent += 1

        timeline.append(
            {
                "email": t["email"],
                "time": datetime.now() + timedelta(minutes=5),
                "message": "Email Opened",
                "details": "",
                "duplicate": None,
            }
        )
        opened += 1

        if random.randint(0, 1) == 1:
            timeline.append(
                {
                    "email": t["email"],
                    "time": datetime.now() + timedelta(minutes=6),
                    "message": "Clicked Link",
                    "details": "",
                    "duplicate": None,
                }
            )
            clicked += 1

    campaigns.append(
        {
            "campaign_uuid": fake.uuid4(),
            "campaign_id": campaign_ids[i],
            "subscription_uuid": subscription_uuid,
            "cycle_uuid": cycle_uuid,
            "name": f"{subscription['name']}_{i}",
            "created_date": datetime.now(),
            "launch_date": datetime.now(),
            "send_by_date": datetime.now() + timedelta(seconds=30),
            "completed_date": datetime.now() + timedelta(minutes=1),
            "email_template": f"{subscription['name']}_{i}",
            "email_template_id": 1,
            "email_template_uuid": campaign_ids[i],
            "template_uuid": random.choice(templates)["template_uuid"],
            "deception_level": random.randint(1, 3),
            "landing_page_template": "Phished",
            "status": "stopped",
            "results": [],
            "phish_results": {
                "sent": sent,
                "opened": opened,
                "clicked": clicked,
                "submitted": submitted,
                "reported": reported,
            },
            "phish_results_dirty": True,
            "groups": [],
            "timeline": timeline,
            "target_email_list": batches[i],
            "smtp": {
                "id": 1,
                "name": subscription["name"],
                "host": "test",
                "interface_type": "SMTP",
                "from_address": "test@test.com",
                "ignore_cert_errors": True,
                "modified_date": datetime.now(),
            },
        }
    )

for c in campaigns:
    campaign_service.save(c)

update_cycle = {
    "cycle_uuid": cycle_uuid,
    "start_date": datetime.now() - timedelta(minutes=3),
    "end_date": datetime.now(),
    "active": True,
    "campaigns_in_cycle": campaign_ids,
    "phish_results": {
        "sent": 0,
        "opened": 0,
        "clicked": 0,
        "submitted": 0,
        "reported": 0,
    },
    "phish_results_dirty": True,
    "override_total_reported": -1,
}

result = subscription_service.update(subscription_uuid, {"cycles": [update_cycle]})

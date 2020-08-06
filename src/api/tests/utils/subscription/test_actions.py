# Third-Party Libraries
from datetime import datetime
from api.utils.subscription.actions import send_templates_list
from api.tests.models.subscription_models.test_gophish_group_model import (
    gophish_group_model_data,
)
from api.tests.models.subscription_models.test_gophish_result_model import (
    gophish_result_model_data,
)
from api.tests.models.subscription_models.test_gophish_timeline_model import (
    gophish_timeline_model_data,
)
from api.tests.models.subscription_models.test_subscription_target_model import (
    subscription_target_model_data,
)
from faker import Faker

fake = Faker()


gophish_campaigns_model_data = {
    "campaign_id": fake.random_number(),
    "name": fake.name(),
    "created_date": fake.date_time(),
    "launch_date": fake.date_time(),
    "send_by_date": fake.date_time(),
    "completed_date": fake.date_time(),
    "email_template": fake.name(),
    "landing_page_template": fake.name(),
    "status": fake.word(),
    "results": [gophish_result_model_data, gophish_result_model_data],
    "groups": [gophish_group_model_data, gophish_group_model_data],
    "timeline": [gophish_timeline_model_data, gophish_timeline_model_data],
    "target_email_list": [
        subscription_target_model_data,
        subscription_target_model_data,
    ],
}


def test_template_email():
    start_date = datetime.now()
    end_date = datetime.now()
    subscription = None

    sub_levels = {
        "high": {
            "start_date": start_date,
            "end_date": end_date,
            "template_targets": {},
            "template_uuids": [],
            "personalized_templates": [],
            "targets": [],
            "deception_level": "high",
        },
        "moderate": {
            "start_date": start_date,
            "end_date": end_date,
            "template_targets": {},
            "template_uuids": [],
            "personalized_templates": [],
            "targets": [],
            "deception_level": "moderate",
        },
        "low": {
            "start_date": start_date,
            "end_date": end_date,
            "template_targets": {},
            "template_uuids": [],
            "personalized_templates": [],
            "targets": [],
            "deception_level": "low",
        },
    }
    send_templates_list(sub_levels, subscription, "bcctest@example.com")
    return

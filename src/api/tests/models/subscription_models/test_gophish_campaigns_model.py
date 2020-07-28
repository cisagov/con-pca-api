# Third-Party Libraries
from api.models.subscription_models import GoPhishCampaignsModel
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


def test_creation():

    gpc = GoPhishCampaignsModel(gophish_campaigns_model_data)
    assert isinstance(gpc, GoPhishCampaignsModel) is True

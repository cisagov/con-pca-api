# Third-Party Libraries
from api.models.subscription_models import SubscriptionModel
from api.tests.models.customer_models.test_customer_contact_model import (
    customer_contact_model_data,
)
from api.tests.models.subscription_models.test_gophish_campaigns_model import (
    gophish_campaigns_model_data,
)
from api.tests.models.subscription_models.test_subscription_target_model import (
    subscription_target_model_data,
)
from faker import Faker

fake = Faker()

subscription_model_data = {
    "subscription_uuid": fake.uuid4(),
    "customer_uuid": fake.uuid4(),
    "name": fake.name(),
    "url": fake.url(),
    "keywords": " ".join(fake.words()),
    "start_date": fake.date_time(),
    "gophish_campaign_list": [
        gophish_campaigns_model_data,
        gophish_campaigns_model_data,
    ],
    "primary_contact": customer_contact_model_data,
    "status": fake.word(),
    "target_email_list": [subscription_target_model_data],
    "templates_selected_uuid_list": [fake.uuid4(), fake.uuid4()],
    "active": fake.boolean(),
    "created_by": fake.name(),
    "cb_timestamp": fake.date_time(),
    "last_updated_by": fake.name(),
    "lub_timestamp": fake.date_time(),
}


def test_creation():
    sm = SubscriptionModel(subscription_model_data)
    assert isinstance(sm, SubscriptionModel) is True

# Third-Party Libraries
from api.models.subscription_models import SubscriptionClicksModel
from faker import Faker

fake = Faker()

subscription_clicks_model_data = {
    "source_ip": fake.ipv4(),
    "timestamp": fake.date_time(),
    "target_uuid": fake.uuid4(),
}


def test_creation():
    sc = SubscriptionClicksModel(subscription_clicks_model_data)
    assert isinstance(sc, SubscriptionClicksModel) is True

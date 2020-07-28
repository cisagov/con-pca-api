# Third-Party Libraries
from api.models.subscription_models import SubscriptionTargetModel
from faker import Faker

fake = Faker()

subscription_target_model_data = {
    "first_name": fake.first_name(),
    "last_name": fake.last_name(),
    "position": fake.job(),
    "email": fake.email(),
}


def test_creation():
    st = SubscriptionTargetModel(subscription_target_model_data)
    assert isinstance(st, SubscriptionTargetModel) is True

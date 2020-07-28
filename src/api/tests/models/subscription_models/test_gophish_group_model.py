# Third-Party Libraries
from api.models.subscription_models import GoPhishGroupModel
from api.tests.models.subscription_models.test_subscription_target_model import (
    subscription_target_model_data,
)
from faker import Faker

fake = Faker()

gophish_group_model_data = {
    "id": fake.random_number(),
    "name": fake.name(),
    "targets": [subscription_target_model_data, subscription_target_model_data],
    "modified_date": fake.date_time(),
}


def test_creation():

    gpg = GoPhishGroupModel(gophish_group_model_data)
    assert isinstance(gpg, GoPhishGroupModel) is True

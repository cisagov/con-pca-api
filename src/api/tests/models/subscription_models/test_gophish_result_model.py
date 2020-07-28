# Third-Party Libraries
from api.models.subscription_models import GoPhishResultModel
from faker import Faker

fake = Faker()

gophish_result_model_data = {
    "first_name": fake.first_name(),
    "last_name": fake.last_name(),
    "position": fake.job(),
    "status": fake.word(),
    "ip": fake.ipv4(),
    "latitude": fake.latitude(),
    "longitude": fake.longitude(),
    "send_date": fake.date_time(),
    "reported": fake.boolean(),
}


def test_creation():
    gpr = GoPhishResultModel(gophish_result_model_data)
    assert isinstance(gpr, GoPhishResultModel) is True

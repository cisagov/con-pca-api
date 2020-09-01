# Third-Party Libraries
from api.models.subscription_models import GoPhishTimelineModel
from faker import Faker

fake = Faker()

gophish_timeline_model_data = {
    "email": fake.email(),
    "time": fake.date_time(),
    "message": fake.paragraph(),
    "details": fake.paragraph(),
}


def test_creation():
    gpt = GoPhishTimelineModel(gophish_timeline_model_data)
    assert isinstance(gpt, GoPhishTimelineModel) is True

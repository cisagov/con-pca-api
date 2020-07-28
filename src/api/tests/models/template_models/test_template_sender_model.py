# Third-Party Libraries
from api.models.template_models import TemplateSenderModel
from faker import Faker

fake = Faker()

template_sender_model_data = {
    "external": fake.random_number(),
    "internal": fake.random_number(),
    "authoritative": fake.random_number(),
}


def test_creation():
    tsm = TemplateSenderModel(template_sender_model_data)
    assert isinstance(tsm, TemplateSenderModel)
    assert isinstance(tsm.external, int)
    assert isinstance(tsm.internal, int)
    assert isinstance(tsm.authoritative, int)

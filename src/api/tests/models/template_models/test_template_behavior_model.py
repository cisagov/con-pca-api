# Third-Party Libraries
from api.models.template_models import TemplateBehaviorModel
from faker import Faker

fake = Faker()


template_behavior_model_data = {
    "fear": fake.random_number(),
    "duty_obligation": fake.random_number(),
    "curiosity": fake.random_number(),
    "greed": fake.random_number(),
}


def test_creation():
    tbm = TemplateBehaviorModel(template_behavior_model_data)
    assert isinstance(tbm, TemplateBehaviorModel)
    assert isinstance(tbm.fear, int)
    assert isinstance(tbm.duty_obligation, int)
    assert isinstance(tbm.curiosity, int)
    assert isinstance(tbm.greed, int)

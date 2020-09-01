# Third-Party Libraries
from api.models.template_models import TemplateRelevancyModel
from faker import Faker

fake = Faker()


template_relevancy_model_data = {
    "organization": fake.random_number(),
    "public_news": fake.random_number(),
}


def test_creation():
    trm = TemplateRelevancyModel(template_relevancy_model_data)
    assert isinstance(trm, TemplateRelevancyModel)
    assert isinstance(trm.organization, int)
    assert isinstance(trm.public_news, int)

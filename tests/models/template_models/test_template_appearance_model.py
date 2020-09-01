# Third-Party Libraries
from api.models.template_models import TemplateAppearanceModel
from faker import Faker

fake = Faker()

template_appearance_model_data = {
    "grammar": fake.random_number(),
    "link_domain": fake.random_number(),
    "logo_graphics": fake.random_number(),
}


def test_creation():
    tam = TemplateAppearanceModel(template_appearance_model_data)
    assert isinstance(tam, TemplateAppearanceModel)
    assert isinstance(tam.grammar, int)
    assert isinstance(tam.link_domain, int)
    assert isinstance(tam.logo_graphics, int)

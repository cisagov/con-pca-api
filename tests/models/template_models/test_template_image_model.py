# Third-Party Libraries
from api.models.template_models import TemplateImageModel
from faker import Faker

fake = Faker()

template_image_model_data = {
    "file_name": fake.file_name(),
    "file_url": fake.image_url(),
}


def test_creation():
    tim = TemplateImageModel(template_image_model_data)
    assert isinstance(tim, TemplateImageModel)
    assert isinstance(tim.file_name, str)
    assert isinstance(tim.file_url, str)

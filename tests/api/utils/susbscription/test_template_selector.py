"""Template Selector Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
from faker import Faker

# cisagov Libraries
from src.api.utils.subscription import template_selector

fake = Faker()


def create_templates():
    """Create Sample Templates."""
    templates = []

    for i in range(0, 15):
        templates.append(
            {
                "template_uuid": fake.uuid4(),
                "deception_score": fake.random_int(0, 2),
                "descriptive_words": " ".join(fake.words()),
            }
        )
        templates.append(
            {
                "template_uuid": fake.uuid4(),
                "deception_score": fake.random_int(3, 4),
                "descriptive_words": " ".join(fake.words()),
            }
        )
        templates.append(
            {
                "template_uuid": fake.uuid4(),
                "deception_score": fake.random_int(5, 9),
                "descriptive_words": " ".join(fake.words()),
            }
        )
    return templates


def test_get_num_templates_per_batch():
    """Test Num Templates."""
    assert template_selector.get_num_templates_per_batch("high") == 8
    assert template_selector.get_num_templates_per_batch("moderate") == 5
    assert template_selector.get_num_templates_per_batch("low") == 3
    assert template_selector.get_num_templates_per_batch() == 5


def test_group_templates():
    """Test Group Templates."""
    templates = create_templates()
    result = template_selector.group_templates(templates)
    assert len(result["low"]) == 15
    assert len(result["moderate"]) == 15
    assert len(result["high"]) == 15


def test_batch_templates():
    """Test Batch Templates."""
    templates = {
        "high": list(range(1, 15)),
        "moderate": list(range(1, 15)),
        "low": list(range(1, 15)),
    }

    sub_levels = {"high": {}, "moderate": {}, "low": {}}

    sub_levels = template_selector.batch_templates(templates, 5, sub_levels)
    assert len(sub_levels["high"]["template_uuids"]) == 5
    assert len(sub_levels["moderate"]["template_uuids"]) == 5
    assert len(sub_levels["low"]["template_uuids"]) == 5


@mock.patch("api.services.DBService.get_list", return_value=[])
@mock.patch("api.utils.template.personalize.personalize_template")
def test_personalize_templates(mock_personalize, mocked_get_list):
    """Test Personalize Templates."""
    templates = create_templates()
    grouped_templates = template_selector.group_templates(templates)
    subscription = {"url": fake.url(), "keywords": " ".join(fake.words())}

    sub_levels = {"high": {}, "moderate": {}, "low": {}}
    sub_levels = template_selector.batch_templates(grouped_templates, 5, sub_levels)
    sub_levels = template_selector.personalize_templates(
        {}, subscription, templates, sub_levels
    )

    assert len(sub_levels["high"]["template_uuids"]) == 5
    assert len(sub_levels["moderate"]["template_uuids"]) == 5
    assert len(sub_levels["low"]["template_uuids"]) == 5

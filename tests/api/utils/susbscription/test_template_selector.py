from src.api.utils.subscription import template_selector

from unittest import mock
from faker import Faker

fake = Faker()


def create_templates():
    templates = []

    for i in range(0, 15):
        templates.append(
            {
                "template_uuid": fake.uuid4(),
                "deception_score": fake.random_int(0, 1),
                "descriptive_words": " ".join(fake.words()),
            }
        )
        templates.append(
            {
                "template_uuid": fake.uuid4(),
                "deception_score": fake.random_int(2, 4),
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


def create_subscription():
    return {"url": fake.url(), "keywords": " ".join(fake.words())}


def test_get_num_templates_per_batch():
    assert template_selector.get_num_templates_per_batch("high") == 8
    assert template_selector.get_num_templates_per_batch("moderate") == 5
    assert template_selector.get_num_templates_per_batch("low") == 3
    assert template_selector.get_num_templates_per_batch() == 5


def test_group_templates():
    templates = create_templates()
    result = template_selector.group_templates(templates)
    assert len(result["low"]) == 15
    assert len(result["medium"]) == 15
    assert len(result["high"]) == 15


@mock.patch("api.manager.TemplateManager.get_templates", return_value="test")
def test_get_relevant_templates(mock_get_templates):
    templates = create_templates()
    subscription = create_subscription()
    template_selector.get_relevant_templates(templates, subscription, 15)
    assert mock_get_templates.call_count == 3


def test_batch_templates():
    templates = {
        "high": list(range(1, 15)),
        "medium": list(range(1, 15)),
        "low": list(range(1, 15)),
    }

    sub_levels = {"high": {}, "moderate": {}, "low": {}}

    sub_levels = template_selector.batch_templates(templates, 5, sub_levels)
    assert len(sub_levels["high"]["template_uuids"]) == 5
    assert len(sub_levels["moderate"]["template_uuids"]) == 5
    assert len(sub_levels["low"]["template_uuids"]) == 5


@mock.patch("api.utils.db_utils.get_list", return_value=[])
@mock.patch("api.utils.template.personalize.personalize_template")
def test_personalize_templates(mock_personalize, mocked_get_list):
    templates = create_templates()
    grouped_templates = template_selector.group_templates(templates)
    subscription = create_subscription()

    sub_levels = {"high": {}, "moderate": {}, "low": {}}
    sub_levels = template_selector.batch_templates(grouped_templates, 5, sub_levels)
    sub_levels = template_selector.personalize_templates(
        {}, subscription, templates, sub_levels
    )

    assert len(sub_levels["high"]["template_uuids"]) == 5
    assert len(sub_levels["moderate"]["template_uuids"]) == 5
    assert len(sub_levels["low"]["template_uuids"]) == 5

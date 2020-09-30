from src.api.utils.subscription import targets

from unittest import mock
from faker import Faker

fake = Faker()


def test_batch_targets():
    subscription = {
        "target_email_list": [
            {"email": fake.email()},
            {"email": fake.email()},
            {"email": fake.email()},
            {"email": fake.email()},
            {"email": fake.email()},
        ]
    }
    sub_levels = {
        "low": {"targets": []},
        "moderate": {"targets": []},
        "high": {"targets": []},
    }
    targets.batch_targets(subscription, sub_levels)
    assert len(sub_levels["low"]["targets"]) == 1
    assert len(sub_levels["moderate"]["targets"]) == 2
    assert len(sub_levels["high"]["targets"]) == 2

    subscription = {"target_email_list": [{"email": fake.email()},]}
    sub_levels = {
        "low": {"targets": []},
        "moderate": {"targets": []},
        "high": {"targets": []},
    }
    targets.batch_targets(subscription, sub_levels)
    assert len(sub_levels["low"]["targets"]) == 0
    assert len(sub_levels["moderate"]["targets"]) == 0
    assert len(sub_levels["high"]["targets"]) == 1


def test_get_target_available_templates():
    templates = ["a", "b", "c"]
    with mock.patch("api.utils.db_utils.get_list", return_value=[]):
        result = targets.get_target_available_templates("test@test.com", templates)
        assert result == templates

    with mock.patch(
        "api.utils.db_utils.get_list",
        return_value=[{"history_list": [{"template_uuid": "a"}]}],
    ):
        result = targets.get_target_available_templates("test@test.com", templates)
        assert "a" not in result
        assert "b" in result
        assert "c" in result

    with mock.patch(
        "api.utils.db_utils.get_list",
        return_value=[
            {
                "history_list": [
                    {"template_uuid": "a"},
                    {"template_uuid": "b"},
                    {"template_uuid": "c"},
                ]
            }
        ],
    ):
        result = targets.get_target_available_templates("test@test.com", templates)
        assert result == templates


def test_assign_targets():
    with mock.patch("api.utils.db_utils.get_list", return_value=[]):
        sub_level = {
            "template_uuids": ["a", "b", "c"],
            "targets": [{"email": fake.email()}, {"email": fake.email()}],
            "template_targets": {},
        }
        targets.assign_targets(sub_level)
        assert len(sub_level["template_targets"].keys()) > 0

        values = []
        for value in sub_level["template_targets"].values():
            values.extend(value)

        assert len(values) == 2

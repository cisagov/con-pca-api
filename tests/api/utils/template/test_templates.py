from unittest import mock
from datetime import datetime

from src.api.utils.template import templates


@mock.patch("api.utils.db_utils.get_list")
def test_get_email_templates(mocked_get_list):
    templates.get_email_templates()
    assert mocked_get_list.called


@mock.patch("api.utils.db_utils.get_list", return_value=[])
@mock.patch("api.utils.db_utils.update_single")
@mock.patch("api.utils.db_utils.save_single")
def test_update_target_history_no_history(mocked_save, mocked_update, mocked_get_list):
    """
    If a target has no history.
    New history doc will be saved.
    """
    templates.update_target_history(
        {"template_uuid": "1"},
        {"email": "test@test.com", "time": datetime.now().isoformat()},
    )
    assert mocked_get_list.called
    assert not mocked_update.called
    assert mocked_save.called


@mock.patch(
    "api.utils.db_utils.get_list",
    return_value=[{"email": "test@test.com", "history_list": [{"template_uuid": "1"}]}],
)
@mock.patch("api.utils.db_utils.update_single")
@mock.patch("api.utils.db_utils.save_single")
def test_update_target_history_with_history(
    mocked_save, mocked_update, mocked_get_list
):
    """
    If a target has history with the same template,
    no history will be added.
    """
    templates.update_target_history(
        {"template_uuid": "1"},
        {"email": "test@test.com", "time": datetime.now().isoformat()},
    )
    assert mocked_get_list.called
    assert not mocked_update.called
    assert not mocked_save.called


@mock.patch(
    "api.utils.db_utils.get_list",
    return_value=[
        {
            "target_uuid": "1",
            "email": "test@test.com",
            "history_list": [{"template_uuid": "2"}],
        }
    ],
)
@mock.patch("api.utils.db_utils.update_single")
@mock.patch("api.utils.db_utils.save_single")
def test_update_target_history_with_history_other(
    mocked_save, mocked_update, mocked_get_list
):
    """
    If a target has history with another template,
    a new history will be added.
    """
    templates.update_target_history(
        {"template_uuid": "1"},
        {"email": "test@test.com", "time": datetime.now().isoformat()},
    )
    assert mocked_get_list.called
    assert mocked_update.called
    assert not mocked_save.called


@mock.patch("api.utils.db_utils.get_list")
def test_get_subscription_templates(mocked_get_list):
    subscription = {"templates_selected_uuid_list": ["1"]}
    templates.get_subscription_templates(subscription)
    assert mocked_get_list.called

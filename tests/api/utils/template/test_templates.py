from unittest import mock
from datetime import datetime

from src.api.utils.template import templates


@mock.patch("api.services.TargetHistoryService.exists", return_value=False)
@mock.patch("api.services.TargetHistoryService.save")
def test_update_target_history_no_history(mocked_save, mock_exists):
    """
    If a target has no history.
    New history doc will be saved.
    """
    templates.update_target_history(
        {"template_uuid": "1"},
        {"email": "test@test.com", "time": datetime.now().isoformat()},
    )
    assert mock_exists.called
    assert mocked_save.called


@mock.patch("api.services.TargetHistoryService.exists", return_value=True)
@mock.patch(
    "api.services.TargetHistoryService.get_list",
    return_value=[
        {
            "target_uuid": "1234",
            "email": "test@test.com",
            "history_list": [{"template_uuid": "1"}],
        }
    ],
)
@mock.patch("api.services.TargetHistoryService.push_nested")
def test_update_target_history_with_history(mocked_push, mocked_get_list, mock_exists):
    """
    If a target has history with the same template,
    no history will be added.
    """
    templates.update_target_history(
        {"template_uuid": "1"},
        {"email": "test@test.com", "time": datetime.now().isoformat()},
    )
    assert mock_exists.called
    assert mocked_get_list.called
    assert mocked_push.called

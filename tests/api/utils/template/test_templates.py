"""Template Util Tests."""
# Standard Python Libraries
from datetime import datetime
from unittest import mock

# cisagov Libraries
from src.api.utils.template import templates


@mock.patch("api.services.TargetHistoryService.get_single", return_value=False)
@mock.patch("api.services.TargetHistoryService.save")
def test_update_target_history_no_history(mocked_save, mock_get):
    """Test Target with No History."""
    templates.update_target_history("1", "test@test.com", datetime.now().isoformat())
    assert mock_get.called
    assert mocked_save.called


@mock.patch(
    "api.services.TargetHistoryService.get_single",
    return_value={
        "target_uuid": "1234",
        "email": "test@test.com",
        "history_list": [{"template_uuid": "1"}],
    },
)
@mock.patch("api.services.TargetHistoryService.push_nested")
def test_update_target_history_with_history(mocked_push, mock_get):
    """Test Target with History."""
    templates.update_target_history(
        "1",
        "test@test.com",
        datetime.now().isoformat(),
    )
    assert mock_get.called
    assert mocked_push.called

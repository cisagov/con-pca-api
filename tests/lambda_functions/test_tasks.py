"""Test Lambda Function Tasks."""
# Standard Python Libraries
from datetime import datetime
from unittest import mock

# Third-Party Libraries
from faker import Faker
import pytest

# cisagov Libraries
from src.lambda_functions.tasks import process_tasks as handler

fake = Faker()


@mock.patch("api.services.SubscriptionService.update_nested")
def test_update_task(mock_update):
    """Test Update Task."""
    handler.update_task(fake.uuid4(), {"task_uuid": fake.uuid4()})
    assert mock_update.called


@mock.patch("api.services.SubscriptionService.push_nested")
def test_add_new_task(mock_push):
    """Test Add New Task."""
    now = datetime.now()
    handler.add_new_task(fake.uuid4(), now, "monthly_report", 60, 15)
    assert mock_push.call_count == 1

    handler.add_new_task(fake.uuid4(), now, "nomessage", 60, 15)
    assert mock_push.call_count == 1


def test_execute_task():
    """Test Execute Task."""
    with pytest.raises(Exception):
        assert handler.execute_task({}, "test")

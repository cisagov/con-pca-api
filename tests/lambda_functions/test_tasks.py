from src.lambda_functions.tasks import process_tasks as handler
from unittest import mock
from faker import Faker
from datetime import datetime
import pytest

fake = Faker()


@mock.patch("api.services.SubscriptionService.update_nested")
def test_update_task(mock_update):
    handler.update_task(fake.uuid4(), {"task_uuid": fake.uuid4()})
    assert mock_update.called


@mock.patch("api.services.SubscriptionService.push_nested")
def test_add_new_task(mock_push):
    now = datetime.now()
    handler.add_new_task(fake.uuid4(), now, "monthly_report")
    assert mock_push.call_count == 1

    handler.add_new_task(fake.uuid4(), now, "nomessage")
    assert mock_push.call_count == 1


def test_execute_task():
    with pytest.raises(Exception):
        assert handler.execute_task({}, "test")

from src.api.utils import webhooks

from unittest import mock

from faker import Faker


fake = Faker()


@mock.patch("api.utils.db_utils.push_nested_item")
def test_push_webhook(mock_push):
    webhooks.push_webhook(
        fake.uuid4(),
        fake.pyint(),
        fake.email(),
        fake.paragraph(),
        fake.date_time(),
        fake.paragraph(),
    )
    assert mock_push.called


def test_check_opened_event():
    email = fake.email()
    timeline = [{"email": email, "message": "Email Opened"}]
    assert webhooks.check_opened_event(timeline, email)
    assert not webhooks.check_opened_event(timeline, fake.email())

"""Webhook Tests."""
# Standard Python Libraries
from unittest import mock

# Third-Party Libraries
from faker import Faker

# cisagov Libraries
from src.api.utils import webhooks

fake = Faker()


@mock.patch("api.services.CampaignService.push_nested")
def test_push_webhook(mock_push):
    """Push Webhook Test."""
    webhooks.push_webhook(
        fake.uuid4(),
        fake.email(),
        fake.paragraph(),
        fake.date_time(),
        fake.paragraph(),
    )
    assert mock_push.called


def test_check_opened_event():
    """Check Opened Event Test."""
    email = fake.email()
    timeline = [{"email": email, "message": "Email Opened"}]
    assert webhooks.check_opened_event(timeline, email)
    assert not webhooks.check_opened_event(timeline, fake.email())

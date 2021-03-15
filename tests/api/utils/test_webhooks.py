"""Webhook Tests."""
# Third-Party Libraries
from faker import Faker

# cisagov Libraries
from src.api.utils import webhooks

fake = Faker()


def test_check_opened_event():
    """Check Opened Event Test."""
    email = fake.email()
    timeline = [{"email": email, "message": "Email Opened"}]
    assert webhooks.check_opened_event(timeline, email)
    assert not webhooks.check_opened_event(timeline, fake.email())

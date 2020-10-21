from unittest import mock

from api import notifications
from gophish.models import SMTP

from faker import Faker

fake = Faker()


@mock.patch("api.services.TemplateService.get_list", return_value=[])
@mock.patch(
    "api.manager.CampaignManager.get_sending_profile",
    return_value=[SMTP(from_address=fake.email())],
)
@mock.patch("api.services.DHSContactService.get", return_value={})
def test_email_sender(mock_dhs_contact_get, mock_smtp, mock_template_list):
    subscription = {
        "cycles": [{"cycle_uuid": fake.uuid4()}],
        "primary_contact": {
            "first_name": fake.first_name(),
            "last_name": fake.last_name(),
        },
        "start_date": fake.date_time_this_month(),
        "campaigns": [],
        "target_email_list": [],
    }
    message_type = "subscription_started"
    sender = notifications.EmailSender(subscription, message_type)
    assert sender.subscription == subscription
    assert sender.cycle_uuid is None
    assert sender.notification["type"] == "Cycle Start Notification"
    assert mock_dhs_contact_get.called
    assert mock_smtp.called
    assert mock_template_list.called
    assert sender.text_content.strip().startswith(
        f"Dear {subscription['primary_contact']['first_name']} {subscription['primary_contact']['last_name']}"
    )

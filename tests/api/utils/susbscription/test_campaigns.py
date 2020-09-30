from src.api.utils.subscription import campaigns
from gophish.models import SMTP

from unittest import mock


@mock.patch("api.manager.CampaignManager.complete_campaign")
@mock.patch("api.manager.CampaignManager.delete_campaign")
@mock.patch("api.manager.CampaignManager.delete_email_template")
@mock.patch("api.manager.CampaignManager.delete_sending_profile")
@mock.patch("api.manager.CampaignManager.delete_user_group")
def test_stop_campaigns(
    mock_del_user_group, mock_del_sp, mock_del_et, mock_del_camp, mock_comp
):
    to_stop = [
        {
            "campaign_id": 1,
            "status": "In Progress",
            "email_template_id": 1,
            "smtp": {"id": 1},
            "groups": [{"id": 1}, {"id": 2}, {"id": 3}],
        },
        {
            "campaign_id": 1,
            "status": "In Progress",
            "email_template_id": 1,
            "smtp": {"id": 1},
            "groups": [{"id": 1}, {"id": 2}, {"id": 3}],
        },
        {
            "campaign_id": 1,
            "email_template_id": 1,
            "status": "stopped",
            "smtp": {"id": 1},
            "groups": [{"id": 1}, {"id": 2}, {"id": 3}],
        },
    ]

    campaigns.stop_campaigns(to_stop)

    for c in to_stop:
        assert c["status"] == "stopped"

    assert mock_comp.call_count == 2
    assert mock_del_camp.call_count == 2
    assert mock_del_sp.call_count == 2
    assert mock_del_et.call_count == 2
    assert mock_del_user_group.call_count == 6


def test_get_campaign_from_addres():
    smtp = SMTP(name="Test SMTP")
    smtp.from_address = "Test <test@test.com>"
    template_from_address = "other@other.com"
    result = campaigns.get_campaign_from_address(smtp, template_from_address)
    assert result == "other@test.com"

    smtp.from_address = "test@test.com"
    template_from_address = "Somebody <other@other.com>"
    result = campaigns.get_campaign_from_address(smtp, template_from_address)
    assert result == "Somebody <other@test.com>"


def test_set_smtp_headers():
    smtp = SMTP(name="Test SMTP")
    cycle_uuid = "test"
    campaigns.__set_smtp_headers(smtp, cycle_uuid)

    assert len(list(filter(lambda x: x["key"] == "DHS-PHISH", smtp.headers))) == 1
    assert (
        len(list(filter(lambda x: x["key"] == "X-Gophish-Contact", smtp.headers))) == 1
    )
    assert len(smtp.headers) == 2

from src.api.utils.subscription import cycles
from src.api.utils.generic import format_ztime
from datetime import datetime, timedelta


def test_get_reported_emails():
    date = datetime.now()
    subscription = {
        "gophish_campaign_list": [
            {
                "campaign_id": 1,
                "timeline": [
                    {
                        "message": "Email Reported",
                        "email": "test@test.com",
                        "time": date,
                    }
                ],
            }
        ],
        "cycles": [
            {
                "start_date": date,
                "end_date": date,
                "campaigns_in_cycle": [1],
                "cycle_uuid": 1,
                "phish_results": {},
                "override_total_reported": -1,
            }
        ],
    }

    result = cycles.get_reported_emails(subscription)
    assert subscription["cycles"][0]["phish_results"]["reported"] == 1
    assert result[0]["email_list"][0]["campaign_id"] == 1
    assert result[0]["email_list"][0]["email"] == "test@test.com"


def test_delete_reported_emails():
    date = datetime.now()
    subscription = {
        "gophish_campaign_list": [
            {
                "campaign_id": 1,
                "timeline": [
                    {
                        "message": "Email Reported",
                        "email": "test@test.com",
                        "time": date,
                    }
                ],
            }
        ],
        "cycles": [
            {
                "start_date": date,
                "end_date": date,
                "campaigns_in_cycle": [1],
                "cycle_uuid": 1,
                "phish_results": {},
                "override_total_reported": -1,
            }
        ],
    }

    cycles.delete_reported_emails(
        subscription,
        {
            "cycle_uuid": 1,
            "delete_list": [{"campaign_id": 1, "email": "test@test.com"}],
        },
    )
    assert len(subscription["gophish_campaign_list"][0]["timeline"]) == 0


def test_update_reported_emails():
    date = datetime.now().isoformat()
    new_date = (datetime.now() + timedelta(days=1)).isoformat()
    subscription = {
        "gophish_campaign_list": [
            {
                "campaign_id": 1,
                "timeline": [
                    {
                        "message": "Email Reported",
                        "email": "test@test.com",
                        "time": date,
                    }
                ],
                "target_email_list": [
                    {"email": "test@test.com"},
                    {"email": "test2@test.com"},
                ],
            }
        ],
        "cycles": [
            {
                "start_date": date,
                "end_date": date,
                "campaigns_in_cycle": [1],
                "cycle_uuid": 1,
                "phish_results": {},
                "override_total_reported": -1,
            }
        ],
    }
    cycles.update_reported_emails(
        subscription,
        {
            "cycle_uuid": 1,
            "update_list": [
                {"campaign_id": 1, "email": "test@test.com", "date": new_date},
                {"email": "test2@test.com", "date": date},
            ],
        },
    )
    assert subscription["gophish_campaign_list"][0]["timeline"][0][
        "time"
    ] == format_ztime(new_date)
    assert len(subscription["gophish_campaign_list"][0]["timeline"]) == 2
    assert subscription["gophish_campaign_list"][0]["timeline"][1][
        "time"
    ] == format_ztime(date)


def test_override_total_reported():
    subscription = {
        "cycles": [{"cycle_uuid": "1"}, {"cycle_uuid": "2"}, {"cycle_uuid": "3"}]
    }
    cycles.override_total_reported(subscription, {"cycle_uuid": "2"})
    assert len(subscription["cycles"][1].keys()) == 1
    cycles.override_total_reported(
        subscription, {"cycle_uuid": "2", "override_total_reported": None}
    )
    assert subscription["cycles"][1]["override_total_reported"] == -1
    cycles.override_total_reported(
        subscription, {"cycle_uuid": "2", "override_total_reported": 3}
    )
    assert subscription["cycles"][1]["override_total_reported"] == 3


def test_get_cycle():
    subscription = {
        "cycles": [{"cycle_uuid": "1"}, {"cycle_uuid": "2"}, {"cycle_uuid": "3"}]
    }
    cycle_data_override = {"cycle_uuid": "2"}
    result = cycles.get_cycle(subscription, cycle_data_override)
    assert result == {"cycle_uuid": "2"}

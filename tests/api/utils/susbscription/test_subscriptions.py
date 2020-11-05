from src.api.utils.subscription import subscriptions
from faker import Faker
from datetime import datetime, timedelta
from src.api.utils.subscription.static import CYCLE_MINUTES, DELAY_MINUTES

from unittest import mock

fake = Faker()


def test_create_subscription_name():
    with mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[{"active": True, "name": "test_1.1"}],
    ) as mocked_get:
        customer = {"customer_uuid": "1", "identifier": "test"}
        result = subscriptions.create_subscription_name(customer)
        assert result == "test_2"
        assert mocked_get.called

    with mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[{"active": True, "name": "test_2.1"}],
    ) as mocked_get:
        customer = {"customer_uuid": "1", "identifier": "test"}
        result = subscriptions.create_subscription_name(customer)
        assert result == "test_3"
        assert mocked_get.called

    with mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[],
    ) as mocked_get:
        customer = {"customer_uuid": "1", "identifier": "test"}
        result = subscriptions.create_subscription_name(customer)
        assert result == "test_1"
        assert mocked_get.called

    with mock.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[
            {"active": True, "name": "test_1"},
            {"active": True, "name": "test_2"},
        ],
    ) as mocked_get:
        customer = {"customer_uuid": "1", "identifier": "test"}
        result = subscriptions.create_subscription_name(customer)
        assert result == "test_3"
        assert mocked_get.called


def test_calculate_subscription_start_end_date():
    # less than current date
    start_date = datetime.now() - timedelta(days=3)
    start, end = subscriptions.calculate_subscription_start_end_date(start_date)
    assert start > (start_date + timedelta(days=3))
    assert end > (start_date + timedelta(days=3) + timedelta(minutes=CYCLE_MINUTES))

    # greater than today's date
    start_date = datetime.now() + timedelta(days=3)
    start, end = subscriptions.calculate_subscription_start_end_date(start_date)
    assert start == start_date + timedelta(minutes=DELAY_MINUTES)
    assert end == start_date + timedelta(minutes=DELAY_MINUTES) + timedelta(
        minutes=CYCLE_MINUTES
    )

    # passing string to function
    start_date = datetime.now() + timedelta(hours=1)
    start, end = subscriptions.calculate_subscription_start_end_date(
        start_date.isoformat()
    )
    assert start <= start_date + timedelta(minutes=DELAY_MINUTES)
    assert start > start_date - timedelta(minutes=(DELAY_MINUTES + 3))


def test_get_subscription_cycles():
    campaigns = [
        {"campaign_id": 1},
        {"campaign_id": 2},
        {"campaign_id": 3},
    ]
    start_date = datetime.now()
    end_date = datetime.now() + timedelta(days=2)
    new_uuid = fake.uuid4()

    result = subscriptions.get_subscription_cycles(
        campaigns, start_date, end_date, new_uuid
    )

    assert result == [
        {
            "cycle_uuid": new_uuid,
            "start_date": start_date,
            "end_date": end_date,
            "active": True,
            "campaigns_in_cycle": [c["campaign_id"] for c in campaigns],
            "phish_results": {
                "sent": 0,
                "opened": 0,
                "clicked": 0,
                "submitted": 0,
                "reported": 0,
            },
        }
    ]


def test_init_subscription_tasks():
    start = datetime.now()
    result = subscriptions.init_subscription_tasks(start)
    assert len(result) == 5


def test_get_staggered_dates_in_range():
    start = datetime.now()
    result = subscriptions.get_staggered_dates_in_range(start, 3)
    assert len(result) == 3
    assert result[0] == start
    assert result[1] == start + timedelta(hours=1)
    assert result[2] == start + timedelta(hours=2)

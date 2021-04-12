"""Subscription Util Tests."""
# Standard Python Libraries
from datetime import datetime, timedelta, timezone
from unittest import mock

# Third-Party Libraries
from faker import Faker

# cisagov Libraries
from config.settings import DELAY_MINUTES
from src.api.utils.subscription import subscriptions

fake = Faker()


def subscription():
    """Sample subscription."""
    return {
        "subscription_uuid": "12334",
        "status": "  Waiting on SRF",
        "cycles": [
            {
                "cycle_uuid": "2bfd4b54-b587-4fa2-a60d-4daba861959e",
                "start_date": datetime(
                    2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc
                ),
                "end_date": datetime(2020, 10, 30, 5, 49, 2),
                "active": True,
                "campaigns_in_cycle": [1],
                "phish_results": {
                    "sent": 1,
                    "opened": 0,
                    "clicked": 0,
                    "submitted": 0,
                    "reported": 0,
                },
                "phish_results_dirty": False,
                "override_total_reported": -1,
            }
        ],
    }


def subscription_queued():
    """Sample Queued Subscription."""
    return {
        "subscription_uuid": "12334",
        "status": "Queued",
        "cycles": [
            {
                "cycle_uuid": "2bfd4b54-b587-4fa2-a60d-4daba861959e",
                "start_date": datetime(
                    2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc
                ),
                "end_date": datetime(2020, 10, 30, 5, 49, 2),
                "active": True,
                "campaigns_in_cycle": [1],
                "phish_results": {
                    "sent": 1,
                    "opened": 0,
                    "clicked": 0,
                    "submitted": 0,
                    "reported": 0,
                },
                "phish_results_dirty": False,
                "override_total_reported": -1,
            }
        ],
    }


def subscription_no_cycles():
    """Sample Subscription No Cycles."""
    return {
        "subscription_uuid": "12334",
        "status": "  Waiting on SRF",
        "cycles": [],
    }


def test_create_subscription_name():
    """Test Name Create."""
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
    """Test Start End Date."""
    # less than current date
    start_date = datetime.now() - timedelta(days=3)
    start, end = subscriptions.calculate_subscription_start_end_date(start_date, 60)
    assert start > (start_date + timedelta(days=3))
    assert end > (start_date + timedelta(days=3) + timedelta(minutes=60))

    # greater than today's date
    start_date = datetime.now() + timedelta(days=3)
    start, end = subscriptions.calculate_subscription_start_end_date(start_date, 60)
    assert start == start_date + timedelta(minutes=DELAY_MINUTES)
    assert end == start_date + timedelta(minutes=DELAY_MINUTES) + timedelta(minutes=60)

    # passing string to function
    start_date = datetime.now() + timedelta(hours=1)
    start, end = subscriptions.calculate_subscription_start_end_date(
        start_date.isoformat(), 60
    )
    assert start <= start_date + timedelta(minutes=DELAY_MINUTES)
    assert start > start_date - timedelta(minutes=(DELAY_MINUTES + 3))


def test_get_subscription_cycles():
    """Test Get Subscription Cycles."""
    campaigns = [
        {"campaign_id": 1},
        {"campaign_id": 2},
        {"campaign_id": 3},
    ]
    start_date = datetime.now()
    end_date = datetime.now() + timedelta(days=2)
    new_uuid = fake.uuid4()
    total_targets = 5

    result = subscriptions.get_subscription_cycles(
        campaigns, start_date, end_date, new_uuid, total_targets
    )

    assert result == [
        {
            "cycle_uuid": new_uuid,
            "start_date": start_date,
            "end_date": end_date,
            "active": True,
            "campaigns_in_cycle": [c["campaign_id"] for c in campaigns],
            "total_targets": 5,
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
    """Test init subscription tasks."""
    start = datetime.now()
    result = subscriptions.init_subscription_tasks(start, True, 60)
    assert len(result) == 5
    assert result[-1]["message_type"] == "start_new_cycle"

    result = subscriptions.init_subscription_tasks(start, False, 60)
    assert len(result) == 5
    assert result[-1]["message_type"] == "stop_subscription"


def test_get_staggered_dates_in_range():
    """Test Stagger Dates."""
    start = datetime.now()
    result = subscriptions.get_staggered_dates_in_range(start, 3)
    assert len(result) == 3
    assert result[0] == start
    assert result[1] == start + timedelta(hours=1)
    assert result[2] == start + timedelta(hours=2)


@mock.patch("api.services.SubscriptionService.update_nested")
def test_add_remove_continuous_subscription_task(mock_update):
    """Test continuous subscription tasks."""
    subscription_uuid = "1234"
    now = datetime.now()
    tasks = [
        {
            "task_uuid": "1234",
            "message_type": "start_new_cycle",
            "scheduled_date": now,
            "executed": False,
        },
        {
            "task_uuid": "5678",
            "message_type": "start_subscription_email",
            "scheduled_date": now,
            "executed": False,
        },
    ]

    subscriptions.add_remove_continuous_subscription_task(
        subscription_uuid, tasks, False
    )
    assert "stop_subscription" in str(mock_update.call_args_list[0])

    tasks = [
        {
            "task_uuid": "1234",
            "message_type": "stop_subscription",
            "scheduled_date": now,
            "executed": False,
        },
        {
            "task_uuid": "5678",
            "message_type": "start_subscription_email",
            "scheduled_date": now,
            "executed": False,
        },
    ]

    subscriptions.add_remove_continuous_subscription_task(
        subscription_uuid, tasks, True
    )
    assert "start_new_cycle" in str(mock_update.call_args_list[1])

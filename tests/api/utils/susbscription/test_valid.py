"""Test api.utils.subscription.valid."""
# Standard Python Libraries
from datetime import datetime, timedelta

# cisagov Libraries
from api.utils.subscription import valid


def test_is_subscription_valid(mocker):
    """Test is_subscription_valid function."""
    # Test too great of an hourly rate
    mocker.patch("api.utils.subscription.valid.get_daily_rate", return_value=1000)
    mocker.patch("api.utils.subscription.valid.get_hourly_rate", return_value=120)
    mocker.patch("api.utils.subscription.valid.get_all_daily_rates", return_value=0)

    is_valid, message = valid.is_subscription_valid(
        target_count=2880, campaign_minutes=60 * 24
    )
    assert not is_valid
    assert "There cannot be more than 100 emails per hour" in message
    assert "reduce targets to 2400" in message

    # Test too great of a daily rate
    mocker.patch("api.utils.subscription.valid.get_daily_rate", return_value=1100)
    mocker.patch("api.utils.subscription.valid.get_hourly_rate", return_value=100)
    is_valid, message = valid.is_subscription_valid(
        target_count=2880, campaign_minutes=60 * 24
    )
    assert not is_valid
    assert "There cannot be more than 1000 emails per day." in message
    assert "reduce targets to 1000" in message

    # Test good daily rate
    mocker.patch("api.utils.subscription.valid.get_all_daily_rates", return_value=20)
    mocker.patch(
        "api.utils.subscription.valid.get_daily_percent_increase", return_value=0
    )
    mocker.patch("api.utils.subscription.valid.get_daily_rate", return_value=70)
    is_valid, message = valid.is_subscription_valid(
        target_count=70, campaign_minutes=60 * 24
    )
    assert is_valid
    assert not message

    # Test too great of a percentage increase
    mocker.patch("api.utils.subscription.valid.get_all_daily_rates", return_value=1000)
    mocker.patch(
        "api.utils.subscription.valid.get_daily_percent_increase", return_value=30
    )
    mocker.patch("api.utils.subscription.valid.get_daily_rate", return_value=300)
    is_valid, message = valid.is_subscription_valid(
        target_count=300, campaign_minutes=60 * 24
    )
    assert not is_valid
    assert "There cannot be more than a 20% increase in a 24 hour window" in message
    assert "reduce targets to 200" in message

    # Test everything good
    mocker.patch("api.utils.subscription.valid.get_all_daily_rates", return_value=1000)
    mocker.patch(
        "api.utils.subscription.valid.get_daily_percent_increase", return_value=19
    )
    mocker.patch("api.utils.subscription.valid.get_daily_rate", return_value=190)
    is_valid, message = valid.is_subscription_valid(
        target_count=190, campaign_minutes=60 * 24
    )
    assert is_valid
    assert not message


def test_get_needed_hourly_rate():
    """Test get_needed_hourly_rate function."""
    targets, minutes = valid.get_needed_hourly_rate(
        campaign_minutes=60, target_count=120, needed_hourly_rate=100
    )
    assert targets == 100
    assert minutes > 60


def test_get_needed_daily_rate():
    """Test get_needed_daily_rate function."""
    targets, minutes = valid.get_needed_daily_rate(
        campaign_minutes=60 * 24,
        target_count=1200,
        current_daily_rate=0,
        needed_daily_rate=1000,
    )
    assert targets == 1000
    assert minutes > 60 * 24


def test_get_needed_percent_increase():
    """Test get_needed_percent_increase function."""
    targets, minutes = valid.get_needed_percent_increase(
        campaign_minutes=60 * 24,
        target_count=300,
        current_daily_rate=1000,
        needed_percent_increase=20,
    )
    assert targets == 200
    assert minutes > 60 * 24


def test_get_hourly_rate():
    """Test get_hourly_rate function."""
    result = valid.get_hourly_rate(30, 60)
    assert result == 30

    result = valid.get_hourly_rate(30, 180)
    assert result == 10


def test_get_daily_rate():
    """Test get_daily_rate function."""
    result = valid.get_daily_rate(24, 60)
    assert result == 576

    result = valid.get_daily_rate(60, 1440)
    assert result == 60


def test_get_all_daily_rates(mocker):
    """Test get_all_daily_rates function."""
    now = datetime.now()
    mocker.patch(
        "api.services.SubscriptionService.get_list",
        return_value=[
            {
                "cycles": [
                    {
                        "start_date": now,
                        "send_by_date": now + timedelta(days=1),
                        "end_date": now + timedelta(days=2),
                        "total_targets": 50,
                    },
                ]
            },
            {
                "cycles": [
                    {
                        "start_date": now,
                        "send_by_date": now + timedelta(days=1),
                        "end_date": now + timedelta(days=2),
                        "total_targets": 50,
                    },
                ]
            },
        ],
    )
    result = valid.get_all_daily_rates()
    assert result == 100


def test_get_daily_percent_increase():
    """Test get_daily_percent_increase function."""
    result = valid.get_daily_percent_increase(50, 25)
    assert result == 50

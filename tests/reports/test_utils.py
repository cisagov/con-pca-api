"""Report Util Tests."""
# Standard Python Libraries
from datetime import datetime, timedelta, timezone

# Third-Party Libraries
from faker import Faker

# cisagov Libraries
from samples import subscription
from src.reports import utils

fake = Faker()


def test_get_closest_cycle_within_day_range():
    """Test closest cycle."""
    result = utils.get_closest_cycle_within_day_range(
        subscription(),
        datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        day_range=90,
    )

    assert result["cycle_uuid"] == "2bfd4b54-b587-4fa2-a60d-4daba861959e"


def test_get_cycle_by_date_in_range():
    """Test Cycle By Date."""
    result = utils.get_cycle_by_date_in_range(
        subscription(), datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc)
    )
    assert result


def test_find_send_timeline_moment():
    """Test find moment."""
    timeline_items = [{"email": "test@test.com"}]
    result = utils.find_send_timeline_moment("test@test.com", timeline_items)

    assert result == {"email": "test@test.com"}

    result = utils.find_send_timeline_moment("test2@test.com", timeline_items)

    assert result == {}


def test_add_moment_no_duplicates():
    """Test add moment."""
    moment = {
        "message": "sent",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }

    timeline_items = [{"email": "test@test.com"}]

    result = utils.add_moment_no_duplicates(moment, timeline_items, "sent")

    assert not result


def test_append_timeline_moment():
    """Test Add moment."""
    moment = {
        "message": "Email Sent",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }

    timeline_items = [
        {
            "message": "Email Sent",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        }
    ]

    utils.append_timeline_moment(moment, timeline_items)

    assert len(timeline_items) == 2

    moment = {
        "message": "Email Opened",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        "opened": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }

    utils.append_timeline_moment(moment, timeline_items)

    assert len(timeline_items) == 2

    moment = {
        "message": "Clicked Link",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        "clicked": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }

    utils.append_timeline_moment(moment, timeline_items)
    assert len(timeline_items) == 2

    moment = {
        "message": "Submitted Data",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        "submitted": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }

    utils.append_timeline_moment(moment, timeline_items)
    assert len(timeline_items) == 2

    moment = {
        "message": "Email Reported",
        "email": "test@test.com",
        "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        "reported": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
    }

    utils.append_timeline_moment(moment, timeline_items)
    assert len(timeline_items) == 2


def test_generate_time_difference_stats():
    """Test time diff stats."""
    list_of_times = [timedelta(days=90)]

    result = utils.generate_time_difference_stats(list_of_times)

    assert result
    assert result["count"] == 1
    assert result["average"] == timedelta(days=90)
    assert result["minimum"] == timedelta(days=90)
    assert result["median"] == timedelta(days=90)
    assert result["maximum"] == timedelta(days=90)


def test_generate_campaign_statistics():
    """Test campaign stats."""
    campaign_timeline_summary = [
        {
            "message": "Email Sent",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        },
        {
            "message": "Email Opened",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened_difference": timedelta(days=1),
        },
        {
            "message": "Email Reported",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted_difference": timedelta(days=1),
        },
    ]

    result = utils.generate_campaign_statistics(campaign_timeline_summary)
    assert result


def test_date_in_range():
    """Test date in range."""
    date = datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc)
    date_not_in = datetime(2020, 7, 22, 19, 37, 54, 960000, tzinfo=timezone.utc)
    min_date = datetime(2020, 7, 1, 19, 37, 54, 960000, tzinfo=timezone.utc)
    max_date = datetime(2020, 7, 10, 19, 37, 54, 960000, tzinfo=timezone.utc)

    result_true = utils.date_in_range(date, min_date, max_date)
    result_false = utils.date_in_range(date_not_in, min_date, max_date)

    assert result_true is True
    assert result_false is False


def test_filter_campaign_timeline_by_date_range():
    """Test filter campaign by date in range."""
    campaign_timeline_summary = [
        {
            "message": "Email Sent",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        },
        {
            "message": "Email Opened",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened_difference": timedelta(days=1),
        },
        {
            "message": "Email Reported",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted_difference": timedelta(days=1),
        },
    ]

    start_date = datetime(2020, 7, 1, 19, 37, 54, 960000, tzinfo=timezone.utc)
    end_date = datetime(2020, 7, 10, 19, 37, 54, 960000, tzinfo=timezone.utc)

    utils.filter_campaign_timeline_by_date_range(
        campaign_timeline_summary, start_date, end_date
    )

    assert len(campaign_timeline_summary) == 5


def test_get_unique_moments():
    """Test unique moments."""
    campaign_timeline_summary = [
        {
            "message": "Email Sent",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        },
        {
            "message": "Email Opened",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened_difference": timedelta(days=1),
        },
        {
            "message": "Email Reported",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted_difference": timedelta(days=1),
        },
    ]

    results = utils.get_unique_moments(campaign_timeline_summary)

    assert len(results) == 4
    assert len(results) != len(campaign_timeline_summary)


def test_count_timeline_moments():
    """Test count timeline moments."""
    campaign_timeline_summary = [
        {
            "message": "Email Sent",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
        },
        {
            "message": "Email Opened",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "sent": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "opened_difference": timedelta(days=1),
        },
        {
            "message": "Email Reported",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "reported_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "clicked_difference": timedelta(days=1),
        },
        {
            "message": "Clicked Link",
            "email": "test@test.com",
            "time": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted": datetime(2020, 7, 7, 19, 37, 54, 960000, tzinfo=timezone.utc),
            "submitted_difference": timedelta(days=1),
        },
    ]

    results = utils.count_timeline_moments(campaign_timeline_summary)

    assert results["sent"] == 1
    assert results["opened"] == 1
    assert results["clicked"] == 2
    assert results["submitted"] == 0
    assert results["reported"] == 1

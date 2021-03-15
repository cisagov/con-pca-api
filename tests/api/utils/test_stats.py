"""Stats tests."""
# Standard Python Libraries
from datetime import datetime, timedelta

# cisagov Libraries
from src.api.utils import stats


def test_get_cycle_campaigns():
    """Test get cycle campaigns."""
    campaigns = [
        {"cycle_uuid": "a"},
        {"cycle_uuid": "b"},
        {"cycle_uuid": "b"},
        {"cycle_uuid": "c"},
    ]
    result = stats.get_cycle_campaigns(campaigns, "b")
    assert result == [{"cycle_uuid": "b"}, {"cycle_uuid": "b"}]


def test_get_event():
    """Test get event."""
    now = datetime.now()
    previous = now - timedelta(minutes=3)
    events = [
        {"message": "Email Opened", "time": now},
        {"message": "Email Opened", "time": previous},
        {"message": "Email Sent", "time": previous},
    ]
    resp = stats.get_event(events, "Email Opened")
    assert len(resp) == 2
    resp = stats.get_event(events, "Email Opened", many=False)
    assert resp["time"] == previous
    resp = stats.get_event(events, "Clicked Link", many=False)
    assert resp is None


def test_get_ratios():
    """Test get ratios."""
    stats = {
        "sent": {"count": 4},
        "opened": {"count": 2},
        "clicked": {"count": 1},
        "reported": {"count": 0},
    }
    result = stats.get_ratios(stats)
    assert result["clicked_ratio"] == 0.25
    assert result["opened_ratio"] == 0.5
    assert result["reported_ratio"] == 0


def test_get_time_stats_for_event():
    """Test get time stats for event."""
    diffs = [timedelta(minutes=3), timedelta(minutes=2), timedelta(minutes=1)]

    result = stats.get_time_stats_for_event(diffs)
    assert result["count"] == 3
    assert result["average"] == timedelta(seconds=120)
    assert result["minimum"] == timedelta(seconds=60)
    assert result["maximum"] == timedelta(seconds=180)
    assert result["median"] == timedelta(seconds=120)


def test_clean_nonhuman_events():
    """Test clean nonhuman events."""
    sent_time = datetime.now() - timedelta(days=1)
    events = [
        {"email": "test1@test.com", "message": "Email Sent", "time": sent_time},
        {
            "email": "test1@test.com",
            "message": "Email Opened",
            "time": sent_time + timedelta(seconds=59),
        },
        {
            "email": "test1@test.com",
            "message": "Clicked Link",
            "time": sent_time + timedelta(minutes=5),
        },
        {"email": "test2@test.com", "message": "Email Sent", "time": sent_time},
        {
            "email": "test1@test.com",
            "message": "Email Opened",
            "time": sent_time + timedelta(minutes=5),
        },
        {
            "email": "test1@test.com",
            "message": "Clicked Link",
            "time": sent_time + timedelta(seconds=59),
        },
        {"email": "test3@test.com", "message": "Email Sent", "time": sent_time},
    ]
    result = stats.clean_nonhuman_events(events)
    assert len(result) == 5
    assert {
        "email": "test1@test.com",
        "message": "Email Opened",
        "time": sent_time + timedelta(seconds=59),
    } not in result

    assert {
        "email": "test1@test.com",
        "message": "Clicked Link",
        "time": sent_time + timedelta(seconds=59),
    } not in result


def test_is_nonhuman_event():
    """Test is nonhuman event."""
    sent_time = datetime.now() - timedelta(days=1)
    event_time = sent_time + timedelta(minutes=1)
    result = stats.is_nonhuman_event(sent_time, event_time)
    assert result is True
    event_time = sent_time + timedelta(minutes=1, seconds=29)
    result = stats.is_nonhuman_event(sent_time, event_time)
    assert result is True
    event_time = sent_time + timedelta(minutes=2)
    result = stats.is_nonhuman_event(sent_time, event_time)
    assert result is False
    event_time = sent_time + timedelta(minutes=1, seconds=30)
    result = stats.is_nonhuman_event(sent_time, event_time)
    assert result is False

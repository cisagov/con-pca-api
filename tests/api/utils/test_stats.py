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
    result = stats.get_cycle_campaigns("b", campaigns)
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
    data = {
        "sent": {"count": 4},
        "opened": {"count": 2},
        "clicked": {"count": 1},
        "reported": {"count": 0},
    }
    result = stats.get_ratios(data)
    assert result["clicked_ratio"] == 0.25
    assert result["opened_ratio"] == 0.5
    assert result["reported_ratio"] == 0


def test_get_time_stats_for_event():
    """Test get time stats for event."""
    data = {
        "diffs": [timedelta(minutes=3), timedelta(minutes=2), timedelta(minutes=1)],
        "count": 3,
    }

    result = stats.get_time_stats_for_event(data)
    assert result["count"] == 3
    assert result["average"] == timedelta(seconds=120)
    assert result["minimum"] == timedelta(seconds=60)
    assert result["maximum"] == timedelta(seconds=180)
    assert result["median"] == timedelta(seconds=120)


def test_clean_nonhuman_events():
    """Test clean nonhuman events."""
    events = [
        {"message": "Email Sent"},
        {
            "message": "Email Opened",
            "asn_org": "OTHER",
        },
        {
            "message": "Clicked Link",
            "asn_org": "OTHER",
        },
        {
            "message": "Email Opened",
            "asn_org": "GOOGLE",
        },
        {
            "message": "Email Opened",
            "asn_org": "GOOGLE",
        },
        {
            "message": "Clicked Link",
            "asn_org": "GOOGLE",
        },
        {
            "message": "Clicked Link",
            "asn_org": "GOOGLE",
        },
    ]
    result = stats.clean_nonhuman_events(events)
    assert len(result) == 3
    assert {
        "message": "Email Opened",
        "asn_org": "GOOGLE",
    } not in result

    assert {
        "message": "Clicked Link",
        "time": "GOOGLE",
    } not in result


def test_is_nonhuman_event():
    """Test is nonhuman event."""
    result = stats.is_nonhuman_event("GOOGLE")
    assert result is True
    result = stats.is_nonhuman_event("AMAZON-02")
    assert result is True
    result = stats.is_nonhuman_event("SOMETHING_RANDOM")
    assert result is False

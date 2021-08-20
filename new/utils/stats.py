"""Stat utils."""


def get_cycle_stats(cycle):
    """Get stats for cycle."""
    stats = {
        "high": {
            "sent": {"count": 0},
            "opened": {"count": 0},
            "clicked": {"count": 0},
        },
        "moderate": {
            "sent": {"count": 0},
            "opened": {"count": 0},
            "clicked": {"count": 0},
        },
        "low": {
            "sent": {"count": 0},
            "opened": {"count": 0},
            "clicked": {"count": 0},
        },
        "all": {
            "sent": {"count": 0},
            "opened": {"count": 0},
            "clicked": {"count": 0},
        },
    }
    for target in cycle["targets"]:
        timeline = target.get("timeline", [])
        timeline = filter_nonhuman_events(timeline)
        sent = target.get("sent")
        opened = get_event(timeline, "opened")
        clicked = get_event(timeline, "clicked")

        if clicked and not opened:
            opened = clicked

        if sent:
            stats["all"]["sent"]["count"] += 1
            stats[target["deception_level"]]["sent"]["count"] += 1
        if opened:
            stats["all"]["opened"]["count"] += 1
            stats[target["deception_level"]]["opened"]["count"] += 1
        if clicked:
            stats["all"]["clicked"]["count"] += 1
            stats[target["deception_level"]]["clicked"]["count"] += 1
    return stats


def get_event(timeline, event):
    """Get event from timeline."""
    events = list(filter(lambda x: x["message"] == event, timeline))
    if events:
        return min(events, key=lambda x: x["time"])
    return None


def filter_nonhuman_events(timeline):
    """Filter nonhuman events from timeline."""
    return list(
        filter(
            lambda x: not is_nonhuman_event(x.get("details", "").get("asn_org")),
            timeline,
        )
    )


def is_nonhuman_event(asn_org):
    """Determine if nonhuman event."""
    if asn_org in ["GOOGLE", "AMAZON-02", "MICROSOFT-CORP-MSN-AS-BLOCK"]:
        return True
    return False

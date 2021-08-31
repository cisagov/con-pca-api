"""Stat utils."""
# Standard Python Libraries
from datetime import timedelta
from itertools import groupby
import statistics

# Third-Party Libraries
from utils.templates import TEMPLATE_INDICATORS

# cisagov Libraries
from api.manager import TemplateManager
from api.schemas.stats_schema import CycleStats

template_manager = TemplateManager()


def get_cycle_stats(cycle):
    """Get stats for cycle."""
    stats = {
        "high": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
        },
        "moderate": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
        },
        "low": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
        },
        "all": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
        },
    }
    template_stats = {}
    for target in cycle["targets"]:
        if target["template_uuid"] not in template_stats:
            template_stats[target["template_uuid"]] = {
                "sent": {"count": 0},
                "opened": {"count": 0},
                "clicked": {"count": 0},
                "template_uuid": target["template_uuid"],
                "template": template_manager.get(
                    uuid=target["template_uuid"],
                    fields=["template_uuid", "name", "subject", "indicators"],
                ),
                "deception_level": target["deception_level"],
            }
        timeline = target.get("timeline", [])
        timeline = filter_nonhuman_events(timeline)
        sent = target.get("sent")
        sent_time = target.get("send_date")
        opened = get_event(timeline, "opened")
        clicked = get_event(timeline, "clicked")

        if clicked and not opened:
            opened = clicked

        if sent:
            stats["all"]["sent"]["count"] += 1
            stats[target["deception_level"]]["sent"]["count"] += 1
            template_stats[target["template_uuid"]]["sent"]["count"] += 1
        if opened:
            stats["all"]["opened"]["count"] += 1
            stats[target["deception_level"]]["opened"]["count"] += 1
            diff = opened["time"] - sent_time
            stats["all"]["opened"]["diffs"].append(diff)
            stats[target["deception_level"]]["opened"]["diffs"].append(diff)
            template_stats[target["template_uuid"]]["opened"]["count"] += 1
        if clicked:
            stats["all"]["clicked"]["count"] += 1
            stats[target["deception_level"]]["clicked"]["count"] += 1
            diff = clicked["time"] - sent_time
            stats["all"]["clicked"]["diffs"].append(diff)
            stats[target["deception_level"]]["clicked"]["diffs"].append(diff)
            template_stats[target["template_uuid"]]["clicked"]["count"] += 1

    process_time_stats(stats)
    process_ratios(stats)
    process_ratios(template_stats)
    rank_templates(template_stats)
    maxmind_stats = get_maxmind_stats(cycle)
    template_stats = template_stats.values()
    indicator_stats = get_indicator_stats(
        template_stats, stats["all"]["clicked"]["count"]
    )
    return CycleStats().dump(
        {
            "stats": stats,
            "template_stats": template_stats,
            "maxmind_stats": maxmind_stats,
            "indicator_stats": indicator_stats,
        }
    )


def rank_templates(template_stats: dict):
    """Rank templates by opened and clicked counts."""
    stats = list(template_stats.values())
    for event in ["opened", "clicked"]:
        stats.sort(reverse=True, key=lambda x: x[event]["ratio"])
        for index, stat in enumerate(stats):
            template_stats[stat["template_uuid"]][event]["rank"] = index + 1


def process_ratios(stats: dict):
    """Get event to sent ratios."""
    for key in stats.keys():
        sent = stats[key]["sent"]["count"]
        for event in ["opened", "clicked"]:
            stats[key][event]["ratio"] = get_ratio(stats[key][event]["count"], sent)


def get_ratio(numerator, denominator):
    """Get ratio from numerator and denominator."""
    return (
        0 if not denominator else round(float(numerator or 0) / float(denominator), 2)
    )


def process_time_stats(stats: dict):
    """Process timedetla stats."""
    for key in stats.keys():
        for event in ["opened", "clicked"]:
            count = stats[key][event]["count"]
            diffs = stats[key][event]["diffs"]
            if len(diffs) > 0:
                stats[key][event]["average"] = (
                    sum(diffs, timedelta()) / count
                ).total_seconds()
                stats[key][event]["minimum"] = min(diffs).total_seconds()
                stats[key][event]["median"] = statistics.median(diffs).total_seconds()
                stats[key][event]["maximum"] = max(diffs).total_seconds()
            else:
                stats[key][event]["average"] = timedelta().total_seconds()
                stats[key][event]["minimum"] = timedelta().total_seconds()
                stats[key][event]["median"] = timedelta().total_seconds()
                stats[key][event]["maximum"] = timedelta().total_seconds()


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


def event_asn_org(event):
    """Get asn org from event."""
    asn_org = event.get("details", {}).get("asn_org")
    if not asn_org:
        return "UNKOWN"
    return asn_org


def get_maxmind_stats(cycle):
    """Get stats from maxmind details."""
    timeline = []
    response = []
    for target in cycle["targets"]:
        timeline.extend(target.get("timeline", []))

    sorted_timeline = sorted(timeline, key=lambda x: event_asn_org(x))
    for org, events in groupby(sorted_timeline, lambda x: event_asn_org(x)):
        val = {
            "asn_org": org,
            "is_nonhuman": is_nonhuman_event(org),
            "ips": set(),
            "cities": set(),
            "opens": 0,
            "clicks": 0,
        }
        for event in events:
            details = event.get("details", {})
            if details.get("ip"):
                val["ips"].add(details["ip"])
            if details.get("city"):
                val["cities"].add(details["city"])
            if event["message"] == "opened":
                val["opens"] += 1
            elif event["message"] == "clicked":
                val["clicks"] += 1
        response.append(val)
    return response


def get_indicator_stats(template_stats, all_clicks):
    """Rank which indicators performed the highest."""
    breakdowns = []
    for stat in template_stats:
        clicks = stat["clicked"]["count"]
        indicators = stat["template"]["indicators"]
        print(indicators)
        for indicator, subindicators in indicators.items():
            for subindicator, score in subindicators.items():
                item = next(
                    filter(
                        lambda x: x["indicator"] == indicator
                        and x["subindicator"] == subindicator
                        and x["score"] == score,
                        breakdowns,
                    ),
                    None,
                )
                if not item:
                    item = {
                        "indicator": indicator,
                        "subindicator": subindicator,
                        "score": score,
                        "clicks": 0,
                        "percentage": 0,
                        "name": TEMPLATE_INDICATORS[indicator][subindicator]["name"],
                        "label": TEMPLATE_INDICATORS[indicator][subindicator][
                            str(score)
                        ],
                    }
                    breakdowns.append(item)
                item["clicks"] += clicks
                item["percentage"] = item["clicks"] / all_clicks
    breakdowns = sorted(breakdowns, key=lambda x: x["percentage"], reverse=True)
    return breakdowns[:5]

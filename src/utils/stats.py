"""Stat utils."""
# Standard Python Libraries
from datetime import timedelta
from itertools import groupby
import statistics

# cisagov Libraries
from api.manager import CycleManager, NonHumanManager, TemplateManager
from api.schemas.stats_schema import CycleStatsSchema
from utils.templates import get_indicators

template_manager = TemplateManager()
cycle_manager = CycleManager()
nonhuman_manager = NonHumanManager()


def get_cycle_stats(cycle):
    """Get stats for cycle."""
    if cycle.get("dirty_stats", True):
        data = {
            "stats": generate_cycle_stats(cycle, nonhuman=False),
            "nonhuman_stats": generate_cycle_stats(cycle, nonhuman=True),
            "dirty_stats": False,
        }
        cycle.update(data)
        if cycle.get("_id"):
            cycle_manager.update(
                document_id=cycle["_id"],
                data=data,
            )


def generate_cycle_stats(cycle, nonhuman=False):
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
    nonhuman_orgs = get_nonhuman_orgs()
    for target in cycle["targets"]:
        if target["template_id"] not in template_stats:
            template_stats[target["template_id"]] = {
                "sent": {"count": 0},
                "opened": {"count": 0},
                "clicked": {"count": 0},
                "template_id": target["template_id"],
                "template": template_manager.get(
                    document_id=target["template_id"],
                    fields=[
                        "_id",
                        "name",
                        "subject",
                        "indicators",
                        "html",
                        "from_address",
                        "deception_score",
                    ],
                ),
                "deception_level": target["deception_level"],
            }
        timeline = target.get("timeline", [])
        if not nonhuman:
            timeline = list(
                filter(
                    lambda x: x.get("details", {}).get("asn_org") not in nonhuman_orgs,
                    timeline,
                )
            )
        sent = target.get("sent")
        sent_time = target.get("send_date")
        opened = get_event(timeline, "opened")
        clicked = get_event(timeline, "clicked")

        if clicked and not opened:
            opened = clicked

        if sent:
            stats["all"]["sent"]["count"] += 1
            stats[target["deception_level"]]["sent"]["count"] += 1
            template_stats[target["template_id"]]["sent"]["count"] += 1
        if opened:
            stats["all"]["opened"]["count"] += 1
            stats[target["deception_level"]]["opened"]["count"] += 1
            diff = opened["time"] - sent_time
            stats["all"]["opened"]["diffs"].append(diff)
            stats[target["deception_level"]]["opened"]["diffs"].append(diff)
            template_stats[target["template_id"]]["opened"]["count"] += 1
        if clicked:
            stats["all"]["clicked"]["count"] += 1
            stats[target["deception_level"]]["clicked"]["count"] += 1
            diff = clicked["time"] - sent_time
            stats["all"]["clicked"]["diffs"].append(diff)
            stats[target["deception_level"]]["clicked"]["diffs"].append(diff)
            template_stats[target["template_id"]]["clicked"]["count"] += 1

    process_time_stats(stats)
    process_ratios(stats)
    process_ratios(template_stats)
    rank_templates(template_stats)

    maxmind_stats = get_maxmind_stats(cycle)
    template_stats = template_stats.values()
    indicator_stats = get_indicator_stats(template_stats)
    time_stats = get_time_stats(stats)

    return CycleStatsSchema().dump(
        {
            "stats": stats,
            "template_stats": template_stats,
            "maxmind_stats": maxmind_stats,
            "indicator_stats": indicator_stats,
            "time_stats": time_stats,
        }
    )


def rank_templates(template_stats: dict):
    """Rank templates by opened and clicked counts."""
    stats = list(template_stats.values())
    for event in ["opened", "clicked"]:
        stats.sort(reverse=True, key=lambda x: x[event]["ratio"])
        rank = 1
        for index, stat in enumerate(stats):
            if (
                stat[event]["ratio"] != stats[index - 1][event]["ratio"]
                and not index == 0
            ):
                rank += 1
            template_stats[stat["template_id"]][event]["rank"] = rank


def process_ratios(stats: dict):
    """Get event to sent ratios."""
    for v in stats.values():
        sent = v["sent"]["count"]
        for event in ["opened", "clicked"]:
            v[event]["ratio"] = get_ratio(v[event]["count"], sent)


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


def get_time_stats(stats):
    """Get time stats."""
    time_stats = {"opened": {}, "clicked": {}}

    for event in ["opened", "clicked"]:
        diffs = stats["all"][event]["diffs"]
        total_count = stats["all"][event]["count"]

        count = sum(diff <= timedelta(seconds=60) for diff in diffs)
        time_stats[event]["one_minutes"] = {
            "count": count,
            "ratio": count / total_count,
        }

        count = sum(diff <= timedelta(minutes=3) for diff in diffs)
        time_stats[event]["three_minutes"] = {
            "count": count,
            "ratio": count / total_count,
        }

        count = sum(diff <= timedelta(minutes=5) for diff in diffs)
        time_stats[event]["five_minutes"] = {
            "count": count,
            "ratio": count / total_count,
        }

        count = sum(diff <= timedelta(minutes=15) for diff in diffs)
        time_stats[event]["fifteen_minutes"] = {
            "count": count,
            "ratio": count / total_count,
        }

        count = sum(diff <= timedelta(minutes=30) for diff in diffs)
        time_stats[event]["thirty_minutes"] = {
            "count": count,
            "ratio": count / total_count,
        }

        count = sum(diff <= timedelta(minutes=60) for diff in diffs)
        time_stats[event]["sixty_minutes"] = {
            "count": count,
            "ratio": count / total_count,
        }

        count = sum(diff <= timedelta(hours=2) for diff in diffs)
        time_stats[event]["two_hours"] = {
            "count": count,
            "ratio": count / total_count,
        }

        count = sum(diff <= timedelta(hours=3) for diff in diffs)
        time_stats[event]["three_hours"] = {
            "count": count,
            "ratio": count / total_count,
        }

        count = sum(diff <= timedelta(hours=4) for diff in diffs)
        time_stats[event]["four_hours"] = {
            "count": count,
            "ratio": count / total_count,
        }

        count = sum(diff <= timedelta(hours=24) for diff in diffs)
        time_stats[event]["one_day"] = {
            "count": count,
            "ratio": count / total_count,
        }

    return time_stats


def get_event(timeline, event):
    """Get event from timeline."""
    events = list(filter(lambda x: x["message"] == event, timeline))
    if events:
        return min(events, key=lambda x: x["time"])
    return None


def get_nonhuman_orgs():
    """Get nonhuman orgs from database."""
    return [x["asn_org"] for x in nonhuman_manager.all()]


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
    nonhuman_orgs = get_nonhuman_orgs()
    for org, events in groupby(sorted_timeline, lambda x: event_asn_org(x)):
        val = {
            "asn_org": org,
            "is_nonhuman": org in nonhuman_orgs,
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


def get_indicator_stats(template_stats):
    """Get all indicator stats."""
    indicator_stats = []
    indicators = get_indicators()
    for group, gv in indicators.items():
        for indicator, iv in gv.items():
            for value, v in iv["values"].items():
                indicator_stats.append(
                    get_stats_from_indicator(
                        group,
                        indicator,
                        value,
                        v["label"],
                        template_stats,
                    )
                )
    return indicator_stats


def get_stats_from_indicator(group, indicator, value, label, template_stats):
    """Get stats for specific indicator."""
    response = {
        "group": group,
        "indicator": indicator,
        "value": value,
        "label": label,
        "sent": {"count": 0},
        "opened": {
            "count": 0,
        },
        "clicked": {
            "count": 0,
        },
    }
    for ts in template_stats:
        template = ts["template"]
        if int(template["indicators"][group][indicator]) == int(value):
            response["sent"]["count"] += ts["sent"]["count"]
            response["opened"]["count"] += ts["opened"]["count"]
            response["clicked"]["count"] += ts["clicked"]["count"]
    process_ratios({"stats": response})
    return response

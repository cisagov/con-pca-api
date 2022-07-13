"""Stat utils."""
# Standard Python Libraries
from datetime import timedelta
from itertools import groupby
import statistics

# cisagov Libraries
from api.manager import (
    CycleManager,
    NonHumanManager,
    RecommendationManager,
    SendingProfileManager,
    SubscriptionManager,
    TargetManager,
    TemplateManager,
)
from api.schemas.stats_schema import CycleStatsSchema
from utils.templates import get_deception_level, get_indicators

template_manager = TemplateManager()
customer_manager = TemplateManager()
cycle_manager = CycleManager()
nonhuman_manager = NonHumanManager()
recommendation_manager = RecommendationManager()
subscription_manager = SubscriptionManager()
target_manager = TargetManager()
sending_profile_manager = SendingProfileManager()


def get_cycle_stats(cycle):
    """Get stats for cycle."""
    if cycle.get("dirty_stats", True):
        targets = target_manager.all(params={"cycle_id": cycle["_id"]})
        data = {
            "stats": generate_cycle_stats(cycle, targets, nonhuman=False),
            "nonhuman_stats": generate_cycle_stats(cycle, targets, nonhuman=True),
            "dirty_stats": False,
        }
        cycle.update(data)
        if cycle.get("_id"):
            cycle_manager.update(
                document_id=cycle["_id"],
                data=data,
            )


def generate_cycle_stats(cycle, targets, nonhuman=False):
    """Get stats for cycle."""
    stats = {
        "high": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
            "reported": {"count": 0, "diffs": []},
        },
        "moderate": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
            "reported": {"count": 0, "diffs": []},
        },
        "low": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
            "reported": {"count": 0, "diffs": []},
        },
        "all": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
            "reported": {"count": 0, "diffs": []},
        },
    }
    stats_by_level = {
        "all": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
            "reported": {"count": 0, "diffs": []},
        },
        "1": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
            "reported": {"count": 0, "diffs": []},
        },
        "2": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
            "reported": {"count": 0, "diffs": []},
        },
        "3": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
            "reported": {"count": 0, "diffs": []},
        },
        "4": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
            "reported": {"count": 0, "diffs": []},
        },
        "5": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
            "reported": {"count": 0, "diffs": []},
        },
        "6": {
            "sent": {"count": 0},
            "opened": {"count": 0, "diffs": []},
            "clicked": {"count": 0, "diffs": []},
            "reported": {"count": 0, "diffs": []},
        },
    }
    template_stats = {}
    nonhuman_orgs = get_nonhuman_orgs()
    for target in targets:
        if target["template_id"] not in template_stats:
            template_stats[target["template_id"]] = {
                "sent": {"count": 0},
                "opened": {"count": 0},
                "clicked": {"count": 0},
                "reported": {"count": 0},
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
                        "sophisticated",
                        "red_flag",
                    ],
                ),
                "deception_level": target["deception_level"],
                "deception_number": target["deception_level_int"],
            }
        decep_level = target["deception_level_int"]
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
        total_clicks = get_all_event(timeline,"clicked")

        reported, reported_time = get_reported_event(
            target["email"], cycle.get("manual_reports", [])
        )

        if clicked and not opened:
            opened = clicked

        add_template_to_stats_by_level(stats_by_level,target,timeline)

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
        if reported:
            stats["all"]["reported"]["count"] += 1
            stats[target["deception_level"]]["reported"]["count"] += 1
            if reported_time:
                diff = reported_time - sent_time
                stats["all"]["reported"]["diffs"].append(diff)
            stats[target["deception_level"]]["reported"]["diffs"].append(diff)
            template_stats[target["template_id"]]["reported"]["count"] += 1

    process_time_stats(stats)
    process_ratios(stats)
    process_ratios(template_stats)
    rank_templates(template_stats)

    maxmind_stats = get_maxmind_stats(cycle, targets)
    template_stats = template_stats.values()
    indicator_stats = get_indicator_stats(template_stats)
    recommendation_stats = get_recommendation_stats(template_stats)
    time_stats = get_time_stats(stats)
    decep_level_stats = get_deception_level_stats(stats_by_level)

    return CycleStatsSchema().dump(
        {
            "stats": stats,
            "template_stats": template_stats,
            "maxmind_stats": maxmind_stats,
            "indicator_stats": indicator_stats,
            "time_stats": time_stats,
            "recommendation_stats": recommendation_stats,
            "deception_level_stats" : decep_level_stats,
        }
    )
def add_template_to_stats_by_level(stats,target,timeline):
    """Add a target/timelines info to the stats by level object"""
    sent = target.get("sent")
    opened = get_all_event(timeline, "opened")
    clicked = get_all_event(timeline, "clicked")
    sent_time = target.get("send_date")

    if sent:
        stats["all"]["sent"]["count"] += 1
        stats[str(target["deception_level_int"])]["sent"]["count"] += 1
    if opened is not None:
        for open in opened:
            diff = open["time"] - sent_time
            stats["all"]["opened"]["count"] += 1
            stats["all"]["opened"]["diffs"].append({"time": diff, "target_id" : target['_id']})
            stats[str(target["deception_level_int"])]["opened"]["count"] += 1
            stats[str(target["deception_level_int"])]["opened"]["diffs"].append({"time": diff, "target_id" : target['_id']})
    if clicked is not None:
        for click in clicked:
            diff = click["time"] - sent_time
            stats["all"]["clicked"]["count"] += 1
            stats["all"]["clicked"]["diffs"].append({"time": diff, "target_id" : target['_id']})
            stats[str(target["deception_level_int"])]["clicked"]["count"] += 1
            stats[str(target["deception_level_int"])]["clicked"]["diffs"].append({"time": diff, "target_id" : target['_id']})


def get_deception_level_stats(stats: dict):
    """Get the deception level based stats"""
    total_unique_clicks =  []
    for event in stats["all"]['clicked']["diffs"]:
        if event['target_id'] not in total_unique_clicks:
            total_unique_clicks.append(event['target_id'])

    decp_lev_stats = []
    for level in [1,2,3,4,5,6]:
        unique_click_array =  []
        for event in stats[str(level)]['clicked']["diffs"]:
            if event['target_id'] not in unique_click_array:
                unique_click_array.append(event['target_id'])
        deception_level = {
            "deception_level" : level,
            "sent_count": stats[str(level)]['sent']['count'],
            "unique_clicks" : len(unique_click_array),
            "total_clicks" : len(stats[str(level)]['clicked']['diffs']),
            "user_reports" : 0,
            "unique_user_clicks" : get_unique_user_click_count(stats[str(level)]['clicked']["diffs"]),
            "click_percentage_over_time" : get_unique_click_over_time(stats[str(level)]['clicked']["diffs"])
        }
        decp_lev_stats.append(deception_level)
    return decp_lev_stats;

def get_unique_click_over_time(diffs):
    """Get the unique click percentage over time"""
    click_percentage_over_time = {
        "one_minutes" : 0,
        "three_minutes" : 0,
        "five_minutes" : 0,
        "fifteen_minutes" : 0,
        "thirty_minutes" : 0,
        "sixty_minutes" : 0,
        "two_hours" : 0,
        "three_hours" : 0,
        "four_hours" : 0,
        "one_day" : 0,
    } 
    times = {
        "one_minutes": 1,
        "three_minutes": 3,
        "five_minutes": 5,
        "fifteen_minutes": 15,
        "thirty_minutes": 30,
        "sixty_minutes": 60,
        "two_hours": 120,
        "three_hours": 180,
        "four_hours": 240,
        "one_day": 1440,
    }

    unique_click_array =  []
    for event in diffs:
        if event['target_id'] not in unique_click_array:
            unique_click_array.append(event['target_id'])
    total = len(unique_click_array)
    for target in unique_click_array:
        clicks = list(filter(lambda x: x["target_id"] == target, diffs))
        click = clicks[0]
        for c in clicks:
            if c['time'].total_seconds() < click['time'].total_seconds():
                click = c

        for t in times:
            if click['time'].total_seconds() < times[t]:
                click_percentage_over_time[t] += 1
    
    for click_count in click_percentage_over_time:
        click_percentage_over_time[click_count] = {
            "count" : click_percentage_over_time[click_count],
            "ratio" : get_ratio(click_percentage_over_time[click_count],total),
        }

    
    return click_percentage_over_time
                
    
def get_unique_user_click_count(diffs):
    """Get how many tiems each unique user clicked"""
    unique_click_array = []
    for event in diffs:
        if event['target_id'] not in unique_click_array:
            unique_click_array.append(event['target_id'])

    unique_user_clicks = {
        "one_click" : 0,
        "two_three_clicks" : 0,
        "four_five_clicks" : 0,
        "six_ten_clicks" : 0,
        "ten_plus_clicks" : 0,
    }

    for target in unique_click_array:
        times_clicked =  len(list(filter(lambda x: x["target_id"] == target, diffs)))
        if times_clicked is 1:
            unique_user_clicks['one_click'] += 1
        elif times_clicked <= 3:
            unique_user_clicks['two_three_clicks'] += 1
        elif times_clicked <= 5:
            unique_user_clicks['four_five_clicks'] += 1
        elif times_clicked <= 10:
            unique_user_clicks['six_ten_clicks'] += 1
        else:
            unique_user_clicks['ten_plus_clicks'] += 1
    return unique_user_clicks


def rank_templates(template_stats: dict):
    """Rank templates by opened and clicked counts."""
    stats = list(template_stats.values())
    for event in ["opened", "clicked", "reported"]:
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
        for event in ["opened", "clicked", "reported"]:
            v[event]["ratio"] = get_ratio(v[event]["count"], sent)


def get_ratio(numerator, denominator):
    """Get ratio from numerator and denominator."""
    return (
        0 if not denominator else round(float(numerator or 0) / float(denominator), 2)
    )


def process_time_stats(stats: dict):
    """Process timedetla stats."""
    for key in stats.keys():
        for event in ["opened", "clicked", "reported"]:
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
    time_stats = {
        "opened": {},
        "clicked": {},
        "reported": {},
    }

    for event in ["opened", "clicked", "reported"]:
        times = {
            "one_minutes": 1,
            "three_minutes": 3,
            "five_minutes": 5,
            "fifteen_minutes": 15,
            "thirty_minutes": 30,
            "sixty_minutes": 60,
            "two_hours": 120,
            "three_hours": 180,
            "four_hours": 240,
            "one_day": 1440,
        }

        diffs = stats["all"][event]["diffs"]
        total_count = stats["all"][event]["count"]

        for label, minutes in times.items():
            count = sum(diff <= timedelta(minutes=minutes) for diff in diffs)
            time_stats[event][label] = {
                "count": count,
                "ratio": get_ratio(count, total_count),
            }

    return time_stats


def get_reported_event(email, manual_reports):
    """Get reported event."""
    for r in manual_reports:
        if email == r["email"]:
            return True, r.get("report_date")
    return False, None


def get_event(timeline, event):
    """Get most recent event from timeline."""
    events = list(filter(lambda x: x["message"] == event, timeline))
    if events:
        return min(events, key=lambda x: x["time"])
    return None

def get_all_event(timeline, event):
    """Get all event from timeline."""
    events = list(filter(lambda x: x["message"] == event, timeline))
    if events:
        return events
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


def get_maxmind_stats(cycle, targets):
    """Get stats from maxmind details."""
    timeline = []
    response = []
    for target in targets:
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
        "reported": {
            "count": 0,
        },
    }
    for ts in template_stats:
        template = ts["template"]
        if int(template["indicators"][group][indicator]) == int(value):
            response["sent"]["count"] += ts["sent"]["count"]
            response["opened"]["count"] += ts["opened"]["count"]
            response["clicked"]["count"] += ts["clicked"]["count"]
            response["reported"]["count"] += ts["reported"]["count"]
    process_ratios({"stats": response})
    return response


def get_recommendation_stats(template_stats):
    """Get recommendation stats."""
    recommendation_ids = []
    for t in template_stats:
        if t["template"].get("sophisticated"):
            recommendation_ids.extend(t["template"]["sophisticated"])
        if t["template"].get("red_flag"):
            recommendation_ids.extend(t["template"]["red_flag"])

    recommendations = recommendation_manager.all(
        params={"_id": {"$in": recommendation_ids}},
        fields=["title", "type", "description"],
    )

    recommendation_stats = []
    for recommendation in recommendations:
        # Get all templates with recommendation
        ts = []
        for t in template_stats:
            if t["template"].get("sophisticated"):
                if recommendation["_id"] in t["template"]["sophisticated"]:
                    ts.append(t)
            if t["template"].get("red_flag"):
                if recommendation["_id"] in t["template"]["red_flag"]:
                    ts.append(t)

        stats = {
            "templates": [x["template"] for x in ts],
            "recommendation": recommendation,
            "sent": {"count": 0},
            "opened": {"count": 0},
            "clicked": {"count": 0},
            "reported": {"count": 0},
        }
        for t in ts:
            stats["sent"]["count"] += t["sent"]["count"]
            stats["opened"]["count"] += t["opened"]["count"]
            stats["clicked"]["count"] += t["clicked"]["count"]
            stats["reported"]["count"] += t["reported"]["count"]
        process_ratios({"stats": stats})
        recommendation_stats.append(stats)
    return recommendation_stats


def get_all_customer_stats():
    """Get all customer stats."""
    levels = ["all", "low", "moderate", "high"]
    actions = ["sent", "opened", "clicked", "reported"]
    all_stats = {}
    for level in levels:
        all_stats[level] = {}
        for action in actions:
            all_stats[level][action] = {"count": 0, "ratios": []}

    cycles = cycle_manager.all(fields=["_id", "dirty_stats", "stats"])
    for cycle in cycles:
        if cycle.get("dirty_stats", True):
            cycle = cycle_manager.get(cycle["_id"])
            get_cycle_stats(cycle)

        for level in levels:
            for action in actions:
                all_stats[level][action]["count"] += cycle["stats"]["stats"][level][
                    action
                ]["count"]
                if action != "sent":
                    all_stats[level][action]["ratios"].append(
                        cycle["stats"]["stats"][level][action]["ratio"]
                    )

    # Process average of ratios
    for level in levels:
        for action in actions:
            if action != "sent":
                ratios = all_stats[level][action]["ratios"]
                length = len(ratios)
                all_stats[level][action]["average"] = sum(ratios) / length
                all_stats[level][action]["minimum"] = min(ratios)
                all_stats[level][action]["maximum"] = max(ratios)
                all_stats[level][action]["median"] = statistics.median(ratios)

    process_ratios(all_stats)
    return all_stats


def get_all_customer_subscriptions(subscriptions):
    """Get all customer subscriptions stats."""
    new = len(
        [
            subscription
            for subscription in subscriptions
            if subscription["status"] == "created"
        ]
    )
    ongoing = len(
        [
            subscription
            for subscription in subscriptions
            if subscription["status"] in ["queued", "running"]
        ]
    )
    stopped = len(
        [
            subscription
            for subscription in subscriptions
            if subscription["status"] == "stopped"
        ]
    )

    return new, ongoing, stopped


def get_sending_profile_metrics(subscriptions, sending_profiles):
    """Get stats on Sending Profiles."""
    templates = template_manager.all(
        fields=["_id", "sending_profile_id"],
        params={"sending_profile_id": {"$in": [s["_id"] for s in sending_profiles]}},
    )

    cycles = cycle_manager.all(
        fields=["_id", "subscription_id", "template_ids"], params={"active": True}
    )

    for sp in sending_profiles:
        active_subs = list(
            filter(
                lambda x: x["sending_profile_id"] == sp["_id"]
                and x["status"] == "running",
                subscriptions,
            )
        )
        templs = [
            t["_id"]
            for t in list(
                filter(lambda x: x["sending_profile_id"] == sp["_id"], templates)
            )
        ]

        cycles_using = list(
            filter(
                lambda x: any(item in templs for item in x["template_ids"])
                or x["subscription_id"] in [sub["_id"] for sub in active_subs],
                cycles,
            )
        )

        subs_using = list(
            filter(
                lambda x: x["_id"] in [c["subscription_id"] for c in cycles_using],
                subscriptions,
            )
        )

        sp["customers_using"] = len(list({s["customer_id"] for s in subs_using}))

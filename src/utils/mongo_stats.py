"""Stat utils."""
# Standard Python Libraries
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
from utils.stats import get_nonhuman_orgs, get_ratio
from utils.templates import get_deception_level, get_indicators

template_manager = TemplateManager()
customer_manager = TemplateManager()
cycle_manager = CycleManager()
nonhuman_manager = NonHumanManager()
recommendation_manager = RecommendationManager()
subscription_manager = SubscriptionManager()
target_manager = TargetManager()
sending_profile_manager = SendingProfileManager()


def mongo_get_cycle_stats(cycle):
    """Get stats for cycle."""
    # if cycle.get("dirty_stats", True):
    data = {
        "stats": mongo_generate_cycle_stats(cycle["_id"], nonhuman=False),
        "nonhuman_stats": mongo_generate_cycle_stats(cycle["_id"], nonhuman=True),
        "dirty_stats": False,
    }
    cycle.update(data)
    if cycle.get("_id"):
        cycle_manager.update(
            document_id=cycle["_id"],
            data=data,
        )


def mongo_generate_cycle_stats(cycle_id, nonhuman=False):
    """Get stats for cycle."""
    nonhuman_orgs = get_nonhuman_orgs()

    decep_level_stats = mongo_get_deception_level_stats(
        cycle_id, nonhuman, nonhuman_orgs
    )
    indicator_stats = mongo_get_indicator_stats(cycle_id, nonhuman, nonhuman_orgs)
    maxmind_stats = mongo_get_maxmind_stats(cycle_id, nonhuman, nonhuman_orgs)
    recommendation_stats = mongo_get_recommendation_stats(
        cycle_id, nonhuman, nonhuman_orgs
    )
    stats = mongo_get_stats(cycle_id, nonhuman, nonhuman_orgs)
    target_stats = mongo_get_target_stats(cycle_id, nonhuman, nonhuman_orgs)
    template_stats = mongo_get_template_stats(cycle_id, nonhuman, nonhuman_orgs)
    time_stats = mongo_get_time_stats(cycle_id, nonhuman, nonhuman_orgs)

    return CycleStatsSchema().dump(
        {
            "stats": stats,
            "template_stats": template_stats,
            "maxmind_stats": maxmind_stats,
            "indicator_stats": indicator_stats,
            "time_stats": time_stats,
            "recommendation_stats": recommendation_stats,
            "deception_level_stats": decep_level_stats,
            "target_stats": target_stats,
        }
    )


def mongo_get_deception_level_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get deception level stats."""
    pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$addFields": {"template_id": {"$toObjectId": "$template_id"}}},
        {
            "$lookup": {
                "from": "template",
                "localField": "template_id",
                "foreignField": "_id",
                "as": "template",
            }
        },
        {"$unwind": {"path": "$template"}},
        {"$unwind": {"path": "$timeline", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$in": nonhuman_orgs},
            }
        },
        {
            "$group": {
                "_id": "$template.deception_score",
                "deception_level": {"$first": "$template.deception_score"},
                "sent_count": {
                    "$sum": {"$cond": [{"$ne": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "total_clicks": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "unique_clicks": {
                    "$addToSet": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "clicked"]},
                            {"$toString": "$_id"},
                            "$$REMOVE",
                        ]
                    }
                },
                "user_reports": {
                    "$sum": {
                        "$cond": [{"$eq": ["$timeline.message", "reported"]}, 1, 0]
                    }
                },
                "unique_user_clicks": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "clicked"]},
                            {"$toString": "$_id"},
                            "$$REMOVE",
                        ]
                    }
                },
                "click_percentage_over_time": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "clicked"]},
                            {"$subtract": ["$timeline.time", "$sent_date"]},
                            "$$REMOVE",
                        ]
                    }
                },
            }
        },
    ]

    deception_level_stats = target_manager.aggregate(pipeline)
    deception_level_stats = sorted(
        deception_level_stats, key=lambda d: d["deception_level"]
    )

    for deception_level in deception_level_stats:
        deception_level["unique_clicks"] = len(deception_level["unique_clicks"])
        deception_level["unique_user_clicks"] = mongo_calculate_unique_user_clicks(
            deception_level["unique_user_clicks"]
        )
        deception_level[
            "click_percentage_over_time"
        ] = mongo_calculate_click_percentage_over_time(
            deception_level["click_percentage_over_time"]
        )

    for deception_level in [1, 2, 3, 4, 5, 6]:
        index = next(
            (
                i
                for i, item in enumerate(deception_level_stats)
                if item["deception_level"] == deception_level
            ),
            None,
        )
        if index is None:
            empty_deception_level = {
                "click_percentage_over_time": {
                    "fifteen_minutes": {"count": 0, "ratio": 0.0},
                    "five_minutes": {"count": 0, "ratio": 0.0},
                    "four_hours": {"count": 0, "ratio": 0.0},
                    "one_day": {"count": 0, "ratio": 0.0},
                    "one_minutes": {"count": 0, "ratio": 0.0},
                    "sixty_minutes": {"count": 0, "ratio": 0.0},
                    "thirty_minutes": {"count": 0, "ratio": 0.0},
                    "three_hours": {"count": 0, "ratio": 0.0},
                    "three_minutes": {"count": 0, "ratio": 0.0},
                    "two_hours": {"count": 0, "ratio": 0.0},
                },
                "deception_level": deception_level,
                "sent_count": 0,
                "total_clicks": 0,
                "unique_clicks": 0,
                "unique_user_clicks": {
                    "four_five_clicks": 0,
                    "one_click": 0,
                    "six_ten_clicks": 0,
                    "ten_plus_clicks": 0,
                    "two_three_clicks": 0,
                },
                "user_reports": 0,
            }
            deception_level_stats.append(empty_deception_level)

    deception_level_stats = sorted(
        deception_level_stats, key=lambda d: d["deception_level"]
    )
    calculate_composite_deception_stats(deception_level_stats, [0, 1], 11)  # Low
    calculate_composite_deception_stats(deception_level_stats, [2, 3], 12)  # Moderate
    calculate_composite_deception_stats(deception_level_stats, [4, 5], 13)  # High
    calculate_composite_deception_stats(deception_level_stats, [6, 7, 8], 14)  # All

    return deception_level_stats


def calculate_composite_deception_stats(
    deception_level_stats, indices, deception_level
):
    """Aggregate deception score stats to get deception level stats."""
    if len(indices) == 2:
        composite_deception_level = {
            "deception_level": deception_level,
            "sent_count": deception_level_stats[indices[0]]["sent_count"]
            + deception_level_stats[indices[1]]["sent_count"],
            "unique_clicks": deception_level_stats[indices[0]]["unique_clicks"]
            + deception_level_stats[indices[1]]["unique_clicks"],
            "total_clicks": deception_level_stats[indices[0]]["total_clicks"]
            + deception_level_stats[indices[1]]["total_clicks"],
            "user_reports": deception_level_stats[indices[0]]["user_reports"]
            + deception_level_stats[indices[1]]["user_reports"],
            "unique_user_clicks": {
                k: deception_level_stats[indices[0]]["unique_user_clicks"].get(k, 0)
                + deception_level_stats[indices[1]]["unique_user_clicks"].get(k, 0)
                for k in set(deception_level_stats[indices[0]]["unique_user_clicks"])
                | set(deception_level_stats[indices[1]]["unique_user_clicks"])
            },
            "click_percentage_over_time": {
                "one_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["one_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "one_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "three_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["three_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "three_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "five_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["five_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "five_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "fifteen_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["fifteen_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "fifteen_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "thirty_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["thirty_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "thirty_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "sixty_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["sixty_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "sixty_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "two_hours": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["two_hours"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "two_hours"
                    ]["count"],
                    "ratio": 0.0,
                },
                "three_hours": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["three_hours"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "three_hours"
                    ]["count"],
                    "ratio": 0.0,
                },
                "four_hours": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["four_hours"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "four_hours"
                    ]["count"],
                    "ratio": 0.0,
                },
                "one_day": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["one_day"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "one_day"
                    ]["count"],
                    "ratio": 0.0,
                },
            },
        }
        for key in list(composite_deception_level["click_percentage_over_time"].keys()):
            composite_deception_level["click_percentage_over_time"][key][
                "ratio"
            ] = get_ratio(
                composite_deception_level["click_percentage_over_time"][key]["count"],
                composite_deception_level["total_clicks"],
            )
        deception_level_stats.append(composite_deception_level)

    elif len(indices) == 3:
        composite_deception_level = {
            "deception_level": deception_level,
            "sent_count": deception_level_stats[indices[0]]["sent_count"]
            + deception_level_stats[indices[1]]["sent_count"]
            + deception_level_stats[indices[2]]["sent_count"],
            "unique_clicks": deception_level_stats[indices[0]]["unique_clicks"]
            + deception_level_stats[indices[1]]["unique_clicks"]
            + deception_level_stats[indices[2]]["unique_clicks"],
            "total_clicks": deception_level_stats[indices[0]]["total_clicks"]
            + deception_level_stats[indices[1]]["total_clicks"]
            + deception_level_stats[indices[2]]["total_clicks"],
            "user_reports": deception_level_stats[indices[0]]["user_reports"]
            + deception_level_stats[indices[1]]["user_reports"]
            + deception_level_stats[indices[2]]["user_reports"],
            "unique_user_clicks": {
                k: deception_level_stats[indices[0]]["unique_user_clicks"].get(k, 0)
                + deception_level_stats[indices[1]]["unique_user_clicks"].get(k, 0)
                + deception_level_stats[indices[2]]["unique_user_clicks"].get(k, 0)
                for k in set(deception_level_stats[indices[0]]["unique_user_clicks"])
                | set(deception_level_stats[indices[1]]["unique_user_clicks"])
                | set(deception_level_stats[indices[2]]["unique_user_clicks"])
            },
            "click_percentage_over_time": {
                "one_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["one_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "one_minutes"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "one_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "three_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["three_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "three_minutes"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "three_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "five_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["five_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "five_minutes"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "five_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "fifteen_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["fifteen_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "fifteen_minutes"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "fifteen_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "thirty_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["thirty_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "thirty_minutes"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "thirty_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "sixty_minutes": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["sixty_minutes"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "sixty_minutes"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "sixty_minutes"
                    ]["count"],
                    "ratio": 0.0,
                },
                "two_hours": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["two_hours"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "two_hours"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "two_hours"
                    ]["count"],
                    "ratio": 0.0,
                },
                "three_hours": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["three_hours"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "three_hours"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "three_hours"
                    ]["count"],
                    "ratio": 0.0,
                },
                "four_hours": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["four_hours"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "four_hours"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "four_hours"
                    ]["count"],
                    "ratio": 0.0,
                },
                "one_day": {
                    "count": deception_level_stats[indices[0]][
                        "click_percentage_over_time"
                    ]["one_day"]["count"]
                    + deception_level_stats[indices[1]]["click_percentage_over_time"][
                        "one_day"
                    ]["count"]
                    + deception_level_stats[indices[2]]["click_percentage_over_time"][
                        "one_day"
                    ]["count"],
                    "ratio": 0.0,
                },
            },
        }
        for key in list(composite_deception_level["click_percentage_over_time"].keys()):
            composite_deception_level["click_percentage_over_time"][key][
                "ratio"
            ] = get_ratio(
                composite_deception_level["click_percentage_over_time"][key]["count"],
                composite_deception_level["total_clicks"],
            )
        deception_level_stats.append(composite_deception_level)


def mongo_calculate_unique_user_clicks(target_list):
    """Get unique user clicks stats."""
    count_list = list({i: target_list.count(i) for i in target_list}.values())
    count_dict = {i: count_list.count(i) for i in count_list}

    unique_user_clicks = {
        "four_five_clicks": count_dict.get(4, 0) + count_dict.get("5", 0),
        "one_click": count_dict.get(1, 0),
        "six_ten_clicks": count_dict.get(
            6, 0
        )  # TODO rename this field to "six_nine_clicks"
        + count_dict.get(7, 0)
        + count_dict.get(8, 0)
        + count_dict.get(
            9, 0
        ),  # + count_dict.get("10", 0), # Ten clicks should not be counted in two places, the buckets are named poorly.
        "ten_plus_clicks": 0,
        "two_three_clicks": count_dict.get(2, 0) + count_dict.get(3, 0),
    }
    unique_user_clicks["ten_plus_clicks"] = len(set(target_list)) - (
        unique_user_clicks["one_click"]
        + unique_user_clicks["two_three_clicks"]
        + unique_user_clicks["four_five_clicks"]
        + unique_user_clicks["six_ten_clicks"]
    )
    return unique_user_clicks


def mongo_calculate_click_percentage_over_time(time_list):
    """Get click percentage over time stats."""
    click_percentage_over_time = {
        "one_minutes": {"count": 0, "ratio": 0.0},
        "three_minutes": {"count": 0, "ratio": 0.0},
        "five_minutes": {"count": 0, "ratio": 0.0},
        "fifteen_minutes": {"count": 0, "ratio": 0.0},
        "thirty_minutes": {"count": 0, "ratio": 0.0},
        "sixty_minutes": {"count": 0, "ratio": 0.0},
        "two_hours": {"count": 0, "ratio": 0.0},
        "three_hours": {"count": 0, "ratio": 0.0},
        "four_hours": {"count": 0, "ratio": 0.0},
        "one_day": {"count": 0, "ratio": 0.0},
    }
    time_windows = {
        "fifteen_minutes": 15 * 60000,
        "five_minutes": 5 * 60000,
        "four_hours": 4 * 60 * 60000,
        "one_day": 24 * 60 * 60000,
        "one_minutes": 1 * 60000,
        "sixty_minutes": 60 * 60000,
        "thirty_minutes": 30 * 60000,
        "three_hours": 3 * 60 * 60000,
        "three_minutes": 3 * 60000,
        "two_hours": 2 * 60 * 60000,
    }

    for milliseconds_elapsed in time_list:
        if milliseconds_elapsed <= time_windows["one_minutes"]:
            click_percentage_over_time["one_minutes"]["count"] += 1
        elif milliseconds_elapsed <= time_windows["three_minutes"]:
            click_percentage_over_time["three_minutes"]["count"] += 1
        elif milliseconds_elapsed <= time_windows["five_minutes"]:
            click_percentage_over_time["five_minutes"]["count"] += 1
        elif milliseconds_elapsed <= time_windows["fifteen_minutes"]:
            click_percentage_over_time["fifteen_minutes"]["count"] += 1
        elif milliseconds_elapsed <= time_windows["thirty_minutes"]:
            click_percentage_over_time["thirty_minutes"]["count"] += 1
        elif milliseconds_elapsed <= time_windows["sixty_minutes"]:
            click_percentage_over_time["sixty_minutes"]["count"] += 1
        elif milliseconds_elapsed <= time_windows["two_hours"]:
            click_percentage_over_time["two_hours"]["count"] += 1
        elif milliseconds_elapsed <= time_windows["three_hours"]:
            click_percentage_over_time["three_hours"]["count"] += 1
        elif milliseconds_elapsed <= time_windows["four_hours"]:
            click_percentage_over_time["four_hours"]["count"] += 1
        elif milliseconds_elapsed <= time_windows["one_day"]:
            click_percentage_over_time["one_day"]["count"] += 1

    for key in list(click_percentage_over_time.keys()):
        click_percentage_over_time[key]["ratio"] = get_ratio(
            click_percentage_over_time[key]["count"], len(time_list)
        )

    return click_percentage_over_time


def mongo_get_indicator_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get indicator stats."""
    indicators = get_indicators()
    pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$addFields": {"template_id": {"$toObjectId": "$template_id"}}},
        {
            "$lookup": {
                "from": "template",
                "localField": "template_id",
                "foreignField": "_id",
                "as": "template",
            }
        },
        {"$unwind": {"path": "$template"}},
        {"$unwind": {"path": "$timeline", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$in": nonhuman_orgs},
            }
        },
        {"$group": get_group_subpipeline(indicators)},
    ]
    indicator_stats = target_manager.aggregate(pipeline)

    return indicator_stats


def get_group_subpipeline(indicators):
    """Get subpipeline for the group stage."""
    pipeline = {"_id": "$cycle_id"}
    for group, gv in indicators.items():
        for indicator, iv in gv.items():
            for value, label in iv["values"].items():
                label = label["label"]
                for event in ["sent", "clicked", "opened", "reported"]:
                    pipeline[
                        f"{group}_{label}_{indicator}_{event}"
                    ] = get_indicator_subpipeline(group, indicator, value, event)
    return pipeline


def get_indicator_subpipeline(group, indicator, value, event):
    """Get subpipeline for each indicator."""
    if event == "sent":
        return {
            "$sum": {
                "$cond": [
                    {
                        "$and": [
                            {"$ne": ["$timeline.message", "clicked"]},
                            {
                                "$eq": [
                                    f"$template.indicators.{group}.{indicator}",
                                    value,
                                ]
                            },
                        ]
                    },
                    1,
                    0,
                ]
            }
        }
    else:
        return {
            "$sum": {
                "$cond": [
                    {
                        "$and": [
                            {"$eq": ["$timeline.message", event]},
                            {
                                "$eq": [
                                    f"$template.indicators.{group}.{indicator}",
                                    value,
                                ]
                            },
                        ]
                    },
                    1,
                    0,
                ]
            }
        }


def mongo_get_maxmind_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get maxmind stats."""
    pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline"}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$in": nonhuman_orgs},
            }
        },
        {
            "$group": {
                "_id": "$timeline.details.asn_org",
                "asn_org": {"$first": "$timeline.details.asn_org"},
                "ips": {"$addToSet": "$timeline.details.ip"},
                "cities": {"$addToSet": "$timeline.details.city"},
                "clicks": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "opens": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "opened"]}, 1, 0]}
                },
            }
        },
    ]
    maxmind_stats = target_manager.aggregate(pipeline)

    for asn_org in maxmind_stats:
        asn_org["is_nonhuman"] = asn_org["asn_org"] in nonhuman_orgs

    # Sort alphebetically by asn_org
    maxmind_stats = sorted(maxmind_stats, key=lambda d: d["asn_org"])

    return maxmind_stats


def mongo_get_recommendation_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get recommendation stats."""
    recommendation_stats = {}
    return recommendation_stats


def mongo_get_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get stats."""
    stats_pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$in": nonhuman_orgs},
            }
        },
        {
            "$group": {
                "_id": "$deception_level",
                "sent_count": {
                    "$sum": {"$cond": [{"$ne": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "clicked": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "click_times": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "clicked"]},
                            {
                                "$divide": [
                                    {"$subtract": ["$timeline.time", "$sent_date"]},
                                    1000,
                                ]
                            },
                            "$$REMOVE",
                        ]
                    }
                },
                "opened": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "opened"]}, 1, 0]}
                },
                "open_times": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "opened"]},
                            {
                                "$divide": [
                                    {"$subtract": ["$timeline.time", "$sent_date"]},
                                    1000,
                                ]
                            },
                            "$$REMOVE",
                        ]
                    }
                },
                "reported": {
                    "$sum": {
                        "$cond": [{"$eq": ["$timeline.message", "reported"]}, 1, 0]
                    }
                },
                "report_times": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "reported"]},
                            {
                                "$divide": [
                                    {"$subtract": ["$timeline.time", "$sent_date"]},
                                    1000,
                                ]
                            },
                            "$$REMOVE",
                        ]
                    }
                },
            }
        },
        {
            "$project": {
                "sent.count": "$sent_count",
                "clicked.count": "$clicked",
                "clicked.ratio": {
                    "$round": [{"$divide": ["$clicked", "$sent_count"]}, 4]
                },
                "clicked.average": {"$sum": [{"$avg": "$click_times"}, 0]},
                "clicked.maximum": {"$sum": [{"$max": "$click_times"}, 0]},
                "clicked.minimum": {"$sum": [{"$min": "$click_times"}, 0]},
                "clicked.median": "$click_times",
                "opened.count": "$opened",
                "opened.ratio": {
                    "$round": [{"$divide": ["$opened", "$sent_count"]}, 4]
                },
                "opened.average": {"$sum": [{"$avg": "$open_times"}, 0]},
                "opened.maximum": {"$sum": [{"$max": "$open_times"}, 0]},
                "opened.minimum": {"$sum": [{"$min": "$open_times"}, 0]},
                "opened.median": "$open_times",
                "reported.count": "$reported",
                "reported.ratio": {
                    "$round": [{"$divide": ["$reported", "$sent_count"]}, 4]
                },
                "reported.average": {"$sum": [{"$avg": "$report_times"}, 0]},
                "reported.maximum": {"$sum": [{"$max": "$report_times"}, 0]},
                "reported.minimum": {"$sum": [{"$min": "$report_times"}, 0]},
                "reported.median": "$report_times",
            }
        },
    ]
    stats = target_manager.aggregate(stats_pipeline)
    # format from list into dictionary
    stats = {item["_id"]: item for item in stats}

    all_stats_pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$in": nonhuman_orgs},
            }
        },
        {
            "$group": {
                "_id": "$cycle_id",
                "sent_count": {
                    "$sum": {"$cond": [{"$ne": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "clicked": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "click_times": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "clicked"]},
                            {
                                "$divide": [
                                    {"$subtract": ["$timeline.time", "$sent_date"]},
                                    1000,
                                ]
                            },
                            "$$REMOVE",
                        ]
                    }
                },
                "opened": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "opened"]}, 1, 0]}
                },
                "open_times": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "opened"]},
                            {
                                "$divide": [
                                    {"$subtract": ["$timeline.time", "$sent_date"]},
                                    1000,
                                ]
                            },
                            "$$REMOVE",
                        ]
                    }
                },
                "reported": {
                    "$sum": {
                        "$cond": [{"$eq": ["$timeline.message", "reported"]}, 1, 0]
                    }
                },
                "report_times": {
                    "$push": {
                        "$cond": [
                            {"$eq": ["$timeline.message", "reported"]},
                            {
                                "$divide": [
                                    {"$subtract": ["$timeline.time", "$sent_date"]},
                                    1000,
                                ]
                            },
                            "$$REMOVE",
                        ]
                    }
                },
            }
        },
        {
            "$project": {
                "sent.count": "$sent_count",
                "clicked.count": "$clicked",
                "clicked.ratio": {
                    "$round": [{"$divide": ["$clicked", "$sent_count"]}, 4]
                },
                "clicked.average": {"$sum": [{"$avg": "$click_times"}, 0]},
                "clicked.maximum": {"$sum": [{"$max": "$click_times"}, 0]},
                "clicked.minimum": {"$sum": [{"$min": "$click_times"}, 0]},
                "clicked.median": "$click_times",
                "opened.count": "$opened",
                "opened.ratio": {
                    "$round": [{"$divide": ["$opened", "$sent_count"]}, 4]
                },
                "opened.average": {"$sum": [{"$avg": "$open_times"}, 0]},
                "opened.maximum": {"$sum": [{"$max": "$open_times"}, 0]},
                "opened.minimum": {"$sum": [{"$min": "$open_times"}, 0]},
                "opened.median": "$open_times",
                "reported.count": "$reported",
                "reported.ratio": {
                    "$round": [{"$divide": ["$reported", "$sent_count"]}, 4]
                },
                "reported.average": {"$sum": [{"$avg": "$report_times"}, 0]},
                "reported.maximum": {"$sum": [{"$max": "$report_times"}, 0]},
                "reported.minimum": {"$sum": [{"$min": "$report_times"}, 0]},
                "reported.median": "$report_times",
            }
        },
    ]
    all_stats = target_manager.aggregate(all_stats_pipeline)

    emptyStat = {
        "clicked": {
            "average": 0,
            "count": 0,
            "maximum": 0,
            "median": 0,
            "minimum": 0,
            "ratio": 0,
        },
        "opened": {
            "average": 0,
            "count": 0,
            "maximum": 0,
            "median": 0,
            "minimum": 0,
            "ratio": 0,
        },
        "reported": {
            "average": 0,
            "count": 0,
            "maximum": 0,
            "median": 0,
            "minimum": 0,
            "ratio": 0,
        },
        "sent": {"count": 0},
    }

    stats["all"] = all_stats[0] if len(all_stats) > 0 else emptyStat
    stats["low"] = stats["low"] if "low" in stats.keys() else emptyStat
    stats["moderate"] = stats["moderate"] if "moderate" in stats.keys() else emptyStat
    stats["high"] = stats["high"] if "high" in stats.keys() else emptyStat

    # calculate medians on the python side
    for level in ["all", "low", "moderate", "high"]:
        for event in ["clicked", "opened", "reported"]:
            print(level, event, stats[level][event]["median"])
            if stats[level][event]["median"] == 0:
                pass
            elif len(stats[level][event]["median"]) > 0:
                stats[level][event]["median"] = statistics.median(
                    stats[level][event]["median"]
                )
            else:
                stats[level][event]["median"] = 0

    return stats


def mongo_get_target_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get target stats."""
    pipeline = [
        {"$match": {"cycle_id": cycle_id}},
        {"$unwind": {"path": "$timeline", "preserveNullAndEmptyArrays": True}},
        {
            "$match": {
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$in": nonhuman_orgs},
            }
        },
        {
            "$group": {
                "_id": "$position",
                "group": {"$first": "$position"},
                "sent_count": {
                    "$sum": {"$cond": [{"$ne": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "clicks": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "clicked"]}, 1, 0]}
                },
                "opens": {
                    "$sum": {"$cond": [{"$eq": ["$timeline.message", "opened"]}, 1, 0]}
                },
                "reports": {
                    "$sum": {
                        "$cond": [{"$eq": ["$timeline.message", "reported"]}, 1, 0]
                    }
                },
            }
        },
        {
            "$project": {
                "group": "$_id",
                "sent.count": "$sent_count",
                "clicked.count": "$clicks",
                "opened.count": "$opens",
                "reported.count": "$reports",
            }
        },
    ]

    target_stats = target_manager.aggregate(pipeline)

    # Sort alphebetically by group
    target_stats = sorted(target_stats, key=lambda d: d["group"])

    return target_stats


def mongo_get_template_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get template stats."""
    template_stats = []
    cycle = cycle_manager.get(document_id=cycle_id, fields=["template_ids"])
    templates = template_manager.all(
        params={"_id": {"$in": cycle["template_ids"]}},
        fields=[
            "_id",
            "deception_score",
            "from_address",
            "html",
            "indicators",
            "name",
            "retired_description",
            "subject",
        ],
    )

    for template in templates:
        sent_count = target_manager.count(
            {
                "cycle_id": {"$eq": cycle_id},
                "template_id": {"$eq": template["_id"]},
            }
        )
        stats = {
            "template": template,
            "deception_level": get_deception_level(template["deception_score"]),
            "template_id": template["_id"],
            "sent": {"count": sent_count},
            "opened": {},
            "clicked": {},
            "reported": {},
        }
        for event in ["opened", "clicked", "reported"]:
            aggregate = target_manager.aggregate(
                get_template_stats_pipeline(
                    cycle_id, template["_id"], event, nonhuman, nonhuman_orgs
                )
            )
            count = aggregate[0].get("count", 0) if len(aggregate) > 0 else 0
            ratio = get_ratio(count, sent_count)
            stats[event]["count"] = count
            stats[event]["ratio"] = ratio

        template_stats.append(stats)

    mongo_rank_templates(template_stats)

    # Sort low, moderate, high
    template_stats = sorted(template_stats, key=lambda d: d["deception_level"])
    template_stats = [template_stats[1], template_stats[2], template_stats[0]]

    return template_stats


def get_template_stats_pipeline(
    cycle_id, template_id, event_type, nonhuman, nonhuman_orgs
):
    """Get template stats."""
    return [
        {
            "$match": {
                "cycle_id": {"$eq": cycle_id},
                "template_id": {"$eq": template_id},
            }
        },
        {"$unwind": {"path": "$timeline"}},
        {
            "$match": {
                "timeline.message": {
                    "$eq": event_type,
                },
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$in": nonhuman_orgs},
            }
        },
        {"$count": "count"},
    ]


def mongo_rank_templates(template_stats: list):
    """Rank templates by opened and clicked counts."""
    for event in ["opened", "clicked", "reported"]:
        template_stats = sorted(
            template_stats, key=lambda d: d[event]["ratio"], reverse=True
        )
        template_stats[0][event]["rank"] = 1
        template_stats[1][event]["rank"] = (
            template_stats[0][event]["rank"] + 1
            if template_stats[0][event]["ratio"] != template_stats[1][event]["ratio"]
            else template_stats[0][event]["rank"]
        )
        template_stats[2][event]["rank"] = (
            template_stats[1][event]["rank"] + 1
            if template_stats[1][event]["ratio"] != template_stats[2][event]["ratio"]
            else template_stats[1][event]["rank"]
        )


def mongo_get_time_stats(cycle_id, nonhuman, nonhuman_orgs):
    """Get time stats."""
    time_stats = {
        "clicked": {
            "fifteen_minutes": {
                "count": 0,
                "ratio": 0.0,
            },
            "five_minutes": {
                "count": 0,
                "ratio": 0.0,
            },
            "four_hours": {
                "count": 0,
                "ratio": 0.0,
            },
            "one_day": {
                "count": 0,
                "ratio": 0.0,
            },
            "one_minutes": {
                "count": 0,
                "ratio": 0.0,
            },
            "sixty_minutes": {
                "count": 0,
                "ratio": 0.0,
            },
            "thirty_minutes": {
                "count": 0,
                "ratio": 0.0,
            },
            "three_hours": {
                "count": 0,
                "ratio": 0.0,
            },
            "three_minutes": {
                "count": 0,
                "ratio": 0.0,
            },
            "two_hours": {
                "count": 0,
                "ratio": 0.0,
            },
        },
        "opened": {
            "fifteen_minutes": {
                "count": 0,
                "ratio": 0.0,
            },
            "five_minutes": {
                "count": 0,
                "ratio": 0.0,
            },
            "four_hours": {
                "count": 0,
                "ratio": 0.0,
            },
            "one_day": {
                "count": 0,
                "ratio": 0.0,
            },
            "one_minutes": {
                "count": 0,
                "ratio": 0.0,
            },
            "sixty_minutes": {
                "count": 0,
                "ratio": 0.0,
            },
            "thirty_minutes": {
                "count": 0,
                "ratio": 0.0,
            },
            "three_hours": {
                "count": 0,
                "ratio": 0.0,
            },
            "three_minutes": {
                "count": 0,
                "ratio": 0.0,
            },
            "two_hours": {
                "count": 0,
                "ratio": 0.0,
            },
        },
    }

    sent_count = target_manager.count({"cycle_id": {"$eq": cycle_id}})

    events = ["clicked", "opened"]
    time_windows = {
        "fifteen_minutes": 15 * 60000,
        "five_minutes": 5 * 60000,
        "four_hours": 4 * 60 * 60000,
        "one_day": 24 * 60 * 60000,
        "one_minutes": 1 * 60000,
        "sixty_minutes": 60 * 60000,
        "thirty_minutes": 30 * 60000,
        "three_hours": 3 * 60 * 60000,
        "three_minutes": 3 * 60000,
        "two_hours": 2 * 60 * 60000,
    }

    for event in events:
        for time_window in list(time_windows.keys()):
            aggregate = target_manager.aggregate(
                get_time_stats_pipeline(
                    cycle_id, event, time_windows[time_window], nonhuman, nonhuman_orgs
                )
            )
            count = aggregate[0].get("count", 0) if len(aggregate) > 0 else 0
            ratio = get_ratio(count, sent_count)
            time_stats[event][time_window]["count"] = count
            time_stats[event][time_window]["ratio"] = ratio

    return time_stats


def get_time_stats_pipeline(
    cycle_id, event_type, time_milliseconds, nonhuman, nonhuman_orgs
):
    """Get time stats pipeline."""
    return [
        {
            "$match": {
                "cycle_id": {"$eq": cycle_id},
            }
        },
        {"$unwind": {"path": "$timeline"}},
        {
            "$match": {
                "timeline.message": {
                    "$eq": event_type,
                },
                "timeline.details.asn_org": {"$nin": nonhuman_orgs}
                if not nonhuman
                else {"$in": nonhuman_orgs},
            }
        },
        {
            "$project": {
                "time_to_click": {"$subtract": ["$timeline.time", "$sent_date"]}
            }
        },
        {
            "$match": {
                "time_to_click": {
                    "$lte": time_milliseconds,
                },
            }
        },
        {"$count": "count"},
    ]
